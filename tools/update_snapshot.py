#!/usr/bin/env python3
"""Pull every repository under ghq and regenerate snapshot.json for the explorer page.

Usage:
    python3 update_snapshot.py [--no-pull] [--quiet]

Environment:
    GHQ_ROOT           ghq root (default: output of `ghq root`, else ~/ghq)
    REPO_EXPLORER_HOME output directory (default: ~/workspace/repo-explorer)

Output: $REPO_EXPLORER_HOME/snapshot.json

Rules:
- Contents are read from the HEAD commit, not the working tree, so uncommitted
  changes and symlink targets (e.g. ~/.config/gh/hosts.yml) never leak in, and
  what you see always matches `head`.
- Binary files and files over 300 KB carry no `content`; they get `skipped`
  ("binary" / "large" / "symlink" / "submodule" / "excluded") so the tree can
  still show them.
- Globs listed in $REPO_EXPLORER_HOME/exclude.txt (e.g. `*.pem`, `.env*`,
  `your-org/your-repo/secrets/*`) are matched against the in-repo path, the
  file name and `owner/repo/path`; matching files carry no content.
- If any HEAD changed, .snapshot-dirty is created.
- Refuses to write if the output directory is inside a git work tree where
  snapshot.json is not ignored (protects against publishing it by accident).
"""
import argparse
import datetime
import fcntl
import fnmatch
import json
import os
import subprocess
import sys
import tempfile

MAX_FILE = 300_000
SNIFF_BYTES = 8192

# Tells on-pull.sh not to regenerate while this script itself is pulling.
NO_HOOK_ENV = 'REPO_EXPLORER_NO_HOOK'


def default_ghq_root():
    try:
        out = subprocess.run(['ghq', 'root'], capture_output=True, text=True)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except FileNotFoundError:
        pass
    return os.path.expanduser('~/ghq')


def home_dir():
    return os.environ.get(
        'REPO_EXPLORER_HOME', os.path.expanduser('~/workspace/repo-explorer'))


def git(d, *args):
    r = subprocess.run(['git', '-C', d, *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ''


def find_repos(ghq_root):
    """List clones in ghq's <host>/<owner>/<repo> layout."""
    repos = []
    if not os.path.isdir(ghq_root):
        return repos
    for host in sorted(os.listdir(ghq_root)):
        host_dir = os.path.join(ghq_root, host)
        if not os.path.isdir(host_dir):
            continue
        for owner in sorted(os.listdir(host_dir)):
            owner_dir = os.path.join(host_dir, owner)
            if not os.path.isdir(owner_dir):
                continue
            for repo in sorted(os.listdir(owner_dir)):
                d = os.path.join(owner_dir, repo)
                if os.path.exists(os.path.join(d, '.git')):
                    repos.append((f'{owner}/{repo}', d))
    return repos


def load_excludes(path):
    if not os.path.isfile(path):
        return []
    with open(path, encoding='utf-8') as fh:
        return [ln.strip() for ln in fh
                if ln.strip() and not ln.lstrip().startswith('#')]


def is_excluded(repo_id, path, patterns):
    full = f'{repo_id}/{path}'
    name = path.rsplit('/', 1)[-1]
    return any(fnmatch.fnmatchcase(path, p) or fnmatch.fnmatchcase(full, p)
               or fnmatch.fnmatchcase(name, p) for p in patterns)


def list_tree(d):
    """Return HEAD's tree as (mode, type, sha, size, path); paths are not quoted."""
    r = subprocess.run(['git', '-C', d, 'ls-tree', '-r', '-z', '-l', 'HEAD'],
                       capture_output=True)
    if r.returncode != 0:
        return None  # e.g. empty repository
    items = []
    for rec in r.stdout.split(b'\0'):
        if not rec:
            continue
        meta, path = rec.split(b'\t', 1)
        mode, typ, sha, size = meta.split()
        items.append((mode.decode(), typ.decode(), sha.decode(),
                      int(size) if size != b'-' else 0,
                      path.decode('utf-8', errors='replace')))
    return items


def read_blobs(d, shas):
    """Read many blobs at once with `git cat-file --batch`."""
    if not shas:
        return {}
    proc = subprocess.run(['git', '-C', d, 'cat-file', '--batch'],
                          input=b''.join(s.encode() + b'\n' for s in shas),
                          capture_output=True, check=True)
    out, pos, blobs = proc.stdout, 0, {}
    for sha in shas:
        nl = out.index(b'\n', pos)
        header = out[pos:nl].split()
        pos = nl + 1
        if len(header) < 3 or header[1] == b'missing':
            continue
        size = int(header[2])
        blobs[sha] = out[pos:pos + size]
        pos += size + 1  # trailing newline
    return blobs


def snapshot_repo(repo_id, d, excludes):
    tree = list_tree(d)
    if tree is None:
        return []
    entries, want = [], []
    for mode, typ, sha, size, path in tree:
        e = {'path': path, 'size': size}
        if typ == 'commit' or mode == '160000':
            e['skipped'] = 'submodule'
        elif mode == '120000':
            e['skipped'] = 'symlink'
        elif is_excluded(repo_id, path, excludes):
            e['skipped'] = 'excluded'
        elif size > MAX_FILE:
            e['skipped'] = 'large'
        else:
            want.append(sha)
            e['_sha'] = sha
        entries.append(e)
    blobs = read_blobs(d, list(dict.fromkeys(want)))
    for e in entries:
        sha = e.pop('_sha', None)
        if sha is None:
            continue
        raw = blobs.get(sha)
        if raw is None or b'\x00' in raw[:SNIFF_BYTES]:
            e['skipped'] = 'binary'
        else:
            e['content'] = raw.decode('utf-8', errors='replace')
    return entries


def pull(d):
    if not git(d, 'rev-parse', '--abbrev-ref', '@{upstream}'):
        return 'skipped (no upstream)'
    env = dict(os.environ, **{NO_HOOK_ENV: '1'})
    r = subprocess.run(['git', '-C', d, 'pull', '--ff-only', '--quiet'],
                       capture_output=True, text=True, env=env)
    if r.returncode == 0:
        return 'pulled'
    lines = [ln.strip() for ln in r.stderr.splitlines() if ln.strip()]
    msg = next((ln for ln in lines if ln.startswith(('fatal:', 'error:'))),
               lines[0] if lines else 'unknown error')
    return f'pull failed: {msg[:120]}'


def load_previous_heads(path):
    try:
        with open(path, encoding='utf-8') as fh:
            return {r['id']: r.get('head') for r in json.load(fh).get('repos', [])}
    except (OSError, ValueError):
        return None


def write_atomic(path, data):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path),
                               prefix='.snapshot-', suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, ensure_ascii=False, separators=(',', ':'))
        os.chmod(tmp, 0o600)  # private source code: owner-only
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def unsafe_output_dir(out_dir):
    """Return an error message if snapshot.json here could end up in a git commit."""
    top = git(out_dir, 'rev-parse', '--show-toplevel')
    if not top:
        return None
    r = subprocess.run(['git', '-C', out_dir, 'check-ignore', '-q', 'snapshot.json'])
    if r.returncode == 0:
        return None
    return (f'refusing to write: {out_dir} is inside the git work tree {top} '
            'and snapshot.json is not ignored there. Use a directory outside any '
            'repository (default: ~/workspace/repo-explorer) or add it to .gitignore.')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--no-pull', action='store_true',
                    help='do not pull; snapshot the current HEADs only')
    ap.add_argument('--quiet', action='store_true',
                    help='do not print one line per repository')
    args = ap.parse_args(argv)

    ghq_root = os.environ.get('GHQ_ROOT') or default_ghq_root()
    out_dir = home_dir()
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, 'snapshot.json')
    problem = unsafe_output_dir(out_dir)
    if problem:
        print(problem, file=sys.stderr)
        return 2

    # Only one run at a time, even if a manual run and a hook overlap.
    lock = open(os.path.join(out_dir, '.snapshot.lock'), 'w')
    fcntl.flock(lock, fcntl.LOCK_EX)

    repos = find_repos(ghq_root)
    if not repos:
        print(f'no repositories found under {ghq_root}', file=sys.stderr)
        return 1

    excludes = load_excludes(os.path.join(out_dir, 'exclude.txt'))
    prev = load_previous_heads(out)
    snapshot = {
        'generated_at': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
        'repos': [],
    }
    failures = 0
    for repo_id, d in repos:
        status = 'no-pull' if args.no_pull else pull(d)
        if status.startswith('pull failed'):
            failures += 1
        files = snapshot_repo(repo_id, d, excludes)
        snapshot['repos'].append({
            'id': repo_id,
            'branch': git(d, 'branch', '--show-current'),
            'head': git(d, 'rev-parse', '--short', 'HEAD'),
            'committed_at': git(d, 'log', '-1', '--format=%cI'),
            'files': files,
        })
        if not args.quiet:
            print(f'{repo_id}: {status}, files={len(files)}')

    write_atomic(out, snapshot)
    heads = {r['id']: r['head'] for r in snapshot['repos']}
    if prev != heads:
        open(os.path.join(out_dir, '.snapshot-dirty'), 'w').close()
    print(f'written {out} ({os.path.getsize(out) / 1024 / 1024:.1f} MB, '
          f'{len(repos)} repos'
          + (f', {failures} pull failures' if failures else '') + ')')
    return 0


if __name__ == '__main__':
    sys.exit(main())
