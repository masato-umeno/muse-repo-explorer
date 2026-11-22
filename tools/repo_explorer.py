#!/usr/bin/env python3
"""One command per step, short output. Designed so an AI agent spends as few tokens as possible.

    python3 repo_explorer.py setup                 install ghq/gh if missing, check sign-in
    python3 repo_explorer.py login                 start GitHub device sign-in, print the code
    python3 repo_explorer.py login --wait          wait for approval, then configure git
    python3 repo_explorer.py list [--all]          repositories you can clone (compact)
    python3 repo_explorer.py clone OWNER/REPO ...  clone with ghq and install hooks
    python3 repo_explorer.py refresh [--no-pull]   pull, snapshot, build page, say what to upload
    python3 repo_explorer.py mark-synced --mode two-file|single-file
                                                   record that the page now shows this snapshot
    python3 repo_explorer.py status                one-line state
    python3 repo_explorer.py build                 snapshot + page without pulling (used by hooks)

Every command is idempotent: re-running a finished step is safe and cheap.
State lives in $REPO_EXPLORER_HOME (default ~/workspace/repo-explorer), outside any repository.
"""
import hashlib
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
import zipfile
from contextlib import redirect_stdout

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import update_snapshot  # noqa: E402
import sync_status  # noqa: E402

BIN = os.path.expanduser('~/.local/bin')
TEMPLATE = os.path.join(TOOLS, '..', 'page', 'index.html')
HOME = update_snapshot.home_dir()
# Binaries installed by `setup` must be usable by every subprocess.
os.environ['PATH'] = BIN + os.pathsep + os.environ.get('PATH', '')
DIST = os.path.join(HOME, 'dist')
MODE_FILE = os.path.join(HOME, '.page-mode')
TEMPLATE_HASH_FILE = os.path.join(HOME, '.page-template-hash')


# ---------------------------------------------------------------- binaries

def find_bin(name):
    local = os.path.join(BIN, name)
    if os.access(local, os.X_OK):
        return local
    return shutil.which(name)


def run(cmd, **kw):
    kw.setdefault('capture_output', True)
    kw.setdefault('text', True)
    return subprocess.run(cmd, **kw)


def arch():
    m = platform.machine().lower()
    return {'x86_64': 'amd64', 'amd64': 'amd64', 'aarch64': 'arm64', 'arm64': 'arm64'}.get(m, m)


def latest_asset(repo, pattern):
    req = urllib.request.Request(f'https://api.github.com/repos/{repo}/releases/latest',
                                 headers={'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        rel = json.load(r)
    for a in rel.get('assets', []):
        if re.fullmatch(pattern, a['name']):
            return rel['tag_name'], a['browser_download_url']
    raise RuntimeError(f'no release asset matching {pattern} in {repo}')


def download(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


def install_binary(name):
    if platform.system() != 'Linux':
        raise RuntimeError(f'please install {name} yourself on {platform.system()}')
    a = arch()
    if name == 'ghq':
        tag, url = latest_asset('x-motemen/ghq', rf'ghq_linux_{a}\.zip')
        with zipfile.ZipFile(io.BytesIO(download(url))) as z:
            member = next(n for n in z.namelist() if n.endswith('/ghq'))
            data = z.read(member)
    else:
        tag, url = latest_asset('cli/cli', rf'gh_[\d.]+_linux_{a}\.tar\.gz')
        with tarfile.open(fileobj=io.BytesIO(download(url)), mode='r:gz') as tz:
            member = next(m for m in tz.getmembers() if m.name.endswith('/bin/gh'))
            data = tz.extractfile(member).read()
    os.makedirs(BIN, exist_ok=True)
    path = os.path.join(BIN, name)
    with open(path + '.tmp', 'wb') as fh:
        fh.write(data)
    os.chmod(path + '.tmp', 0o755)
    os.replace(path + '.tmp', path)
    return tag


def gh(*args, **kw):
    exe = find_bin('gh')
    if not exe:
        raise SystemExit('gh not installed: run `repo_explorer.py setup` first')
    return run([exe, *args], **kw)


def signed_in_user():
    r = gh('api', 'user', '--jq', '.login')
    return r.stdout.strip() if r.returncode == 0 else None


# ---------------------------------------------------------------- commands

def cmd_setup(args):
    os.makedirs(HOME, exist_ok=True)
    for name in ('ghq', 'gh'):
        if find_bin(name):
            print(f'{name}: ok')
        else:
            try:
                print(f'{name}: installed {install_binary(name)}')
            except Exception as e:  # report, keep going
                print(f'{name}: FAILED to install ({e})')
                return 1
    user = signed_in_user()
    print(f'github: signed in as {user}' if user
          else 'github: not signed in -> next: repo_explorer.py login')
    return 0


def cmd_login(args):
    user = signed_in_user()
    if user:
        gh('auth', 'setup-git')
        print(f'already signed in as {user}')
        return 0
    log = os.path.join(HOME, '.login.log')
    if args and args[0] == '--wait':
        deadline = time.time() + 900
        while time.time() < deadline:
            user = signed_in_user()
            if user:
                gh('auth', 'setup-git')
                print(f'signed in as {user}; git configured for HTTPS')
                return 0
            time.sleep(3)
        print('timed out waiting for approval; run `repo_explorer.py login` again')
        return 1
    os.makedirs(HOME, exist_ok=True)
    out = open(log, 'w')
    env = dict(os.environ, GH_BROWSER='true', BROWSER='true', GH_PROMPT_DISABLED='1')
    subprocess.Popen([find_bin('gh'), 'auth', 'login', '--hostname', 'github.com',
                      '--git-protocol', 'https', '--web', '--skip-ssh-key'],
                     stdin=subprocess.DEVNULL, stdout=out, stderr=out, env=env,
                     start_new_session=True)
    code = None
    for _ in range(40):
        time.sleep(0.5)
        m = re.search(r'\b([A-Z0-9]{4}-[A-Z0-9]{4})\b', open(log).read())
        if m:
            code = m.group(1)
            break
    if not code:
        tail = [ln for ln in open(log).read().splitlines() if ln.strip()][-2:]
        print('could not get a device code: ' + (' / '.join(tail) or 'no output from gh'))
        return 1
    print(f'Open https://github.com/login/device and enter: {code}')
    print('Then run: repo_explorer.py login --wait')
    return 0


def owners():
    me = signed_in_user()
    if not me:
        raise SystemExit('not signed in: run `repo_explorer.py login`')
    orgs = gh('api', 'user/orgs', '--jq', '.[].login').stdout.split()
    return [me] + orgs


def cloned_ids():
    return {rid for rid, _ in update_snapshot.find_repos(ghq_root())}


def ghq_root():
    if os.environ.get('GHQ_ROOT'):
        return os.environ['GHQ_ROOT']
    exe = find_bin('ghq')
    if exe:
        r = run([exe, 'root'])
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return os.path.expanduser('~/ghq')


def cmd_list(args):
    show_all = '--all' in args
    have = cloned_ids()
    total = 0
    for owner in owners():
        r = gh('repo', 'list', owner, '--limit', '1000',
               '--json', 'nameWithOwner,isArchived,isPrivate,isFork')
        if r.returncode != 0:
            print(f'{owner}: cannot list ({r.stderr.strip()[:80]})')
            continue
        for repo in sorted(json.loads(r.stdout), key=lambda x: x['nameWithOwner'].lower()):
            if repo['isArchived'] and not show_all:
                continue
            flags = [f for f, on in (('private', repo['isPrivate']), ('fork', repo['isFork']),
                                     ('archived', repo['isArchived']),
                                     ('cloned', repo['nameWithOwner'] in have)) if on]
            print(repo['nameWithOwner'] + (f'  [{",".join(flags)}]' if flags else ''))
            total += 1
    print(f'-- {total} repositories' + ('' if show_all else ' (archived hidden; --all to show)'))
    return 0


def install_hooks(quiet=True):
    r = run(['sh', os.path.join(TOOLS, 'install-hooks.sh')],
            env=dict(os.environ, GHQ_ROOT=ghq_root()))
    if r.returncode != 0 or not quiet:
        print((r.stdout + r.stderr).strip())
    return r.returncode


def cmd_clone(args):
    if not args:
        print('usage: repo_explorer.py clone OWNER/REPO ...')
        return 2
    exe = find_bin('ghq')
    if not exe:
        raise SystemExit('ghq not installed: run `repo_explorer.py setup` first')
    have, ok, bad = cloned_ids(), 0, 0
    for rid in args:
        if rid in have:
            ok += 1
            continue
        r = run([exe, 'get', '--silent', rid])
        if r.returncode == 0:
            ok += 1
        else:
            bad += 1
            print(f'FAILED {rid}: {(r.stderr.strip().splitlines() or ["?"])[-1][:120]}')
    install_hooks()
    print(f'cloned: {ok} ok, {bad} failed')
    return 1 if bad else 0


def build_page():
    """Write dist/index.html, dist/snapshot.json and the single-file dist/explorer.html."""
    snap = os.path.join(HOME, 'snapshot.json')
    with open(TEMPLATE, encoding='utf-8') as fh:
        tpl = fh.read()
    with open(snap, encoding='utf-8') as fh:
        raw = fh.read()
    os.makedirs(DIST, exist_ok=True)
    os.chmod(DIST, 0o700)
    marker = '<script id="snapshot-data" type="application/json"></script>'
    assert marker in tpl, 'page template is missing the snapshot-data tag'
    # "<" is escaped so the JSON can never close the <script> element.
    single = tpl.replace(marker, '<script id="snapshot-data" type="application/json">'
                         + raw.replace('<', '\\u003c') + '</script>')
    for name, data in (('index.html', tpl), ('snapshot.json', raw), ('explorer.html', single)):
        path = os.path.join(DIST, name)
        with open(path + '.tmp', 'w', encoding='utf-8') as fh:
            fh.write(data)
        os.chmod(path + '.tmp', 0o600)
        os.replace(path + '.tmp', path)


def snapshot(pull):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = update_snapshot.main(['--quiet'] + ([] if pull else ['--no-pull']))
    return rc, buf.getvalue()


def snapshot_stats():
    with open(os.path.join(HOME, 'snapshot.json'), encoding='utf-8') as fh:
        s = json.load(fh)
    files = sum(len(r['files']) for r in s['repos'])
    size = os.path.getsize(os.path.join(HOME, 'snapshot.json')) / 1024 / 1024
    return len(s['repos']), files, size


def page_mode():
    try:
        return open(MODE_FILE).read().strip()
    except OSError:
        return None


def template_hash():
    with open(TEMPLATE, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def template_changed():
    try:
        return open(TEMPLATE_HASH_FILE).read().strip() != template_hash()
    except OSError:
        return True


def changed_repos():
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = sync_status.main([])
    return rc == sync_status.NEEDS_UPDATE, [ln for ln in buf.getvalue().splitlines()
                                            if ln.startswith(('changed:', 'removed:'))]


def cmd_build(args):
    rc, _ = snapshot(pull=False)
    if rc == 0:
        build_page()
    return rc


def cmd_refresh(args):
    if not cloned_ids():
        print('nothing cloned yet: run setup, login and clone first')
        return 1
    install_hooks()
    rc, out = snapshot(pull='--no-pull' not in args)
    for line in out.splitlines():
        if 'pull failed' in line or line.startswith(('no repositories', 'refusing')):
            print(line)
    if rc != 0:
        return rc
    build_page()
    repos, files, size = snapshot_stats()
    print(f'repos: {repos}, files: {files}, snapshot: {size:.1f} MB')
    needed, changes = changed_repos()
    mode = page_mode()
    new_page = mode is not None and template_changed()
    if not needed and not new_page:
        print('UP_TO_DATE: the page already shows this snapshot. Nothing to do.')
        return 0
    print('PAGE_UPDATE_NEEDED: ' + ', '.join(
        x for x in (f'{len(changes)} repositories changed' if needed else '',
                    'new page version' if new_page else '') if x))
    if mode == 'two-file':
        if needed:
            print(f'replace the page asset snapshot.json with: {DIST}/snapshot.json')
        if new_page:
            print(f'replace the page file index.html with: {DIST}/index.html')
    elif mode == 'single-file':
        print(f'replace the page file with: {DIST}/explorer.html')
    else:
        print('first time: create the page from either')
        print(f'  two files (preferred): {DIST}/index.html + {DIST}/snapshot.json')
        print(f'  one file:              {DIST}/explorer.html')
    print('then run: repo_explorer.py mark-synced'
          + ('' if mode else ' --mode two-file|single-file'))
    return 0


def cmd_mark_synced(args):
    if '--mode' in args:
        i = args.index('--mode')
        mode = args[i + 1] if i + 1 < len(args) else ''
        if mode not in ('two-file', 'single-file'):
            print('--mode must be two-file or single-file')
            return 2
        with open(MODE_FILE, 'w') as fh:
            fh.write(mode)
    elif not page_mode():
        print('first time: add --mode two-file or --mode single-file')
        return 2
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = sync_status.main(['--mark'])
    if rc == 0:
        with open(TEMPLATE_HASH_FILE, 'w') as fh:
            fh.write(template_hash())
    print(buf.getvalue().strip())
    return rc


def cmd_status(args):
    parts = [f'ghq:{"ok" if find_bin("ghq") else "missing"}',
             f'gh:{"ok" if find_bin("gh") else "missing"}']
    if find_bin('gh'):
        parts.append(f'user:{signed_in_user() or "-"}')
    parts.append(f'clones:{len(cloned_ids())}')
    if os.path.exists(os.path.join(HOME, 'snapshot.json')):
        needed, changes = changed_repos()
        parts.append(f'page:{"needs-update" if needed else "up-to-date"}')
    else:
        parts.append('snapshot:none')
    parts.append(f'mode:{page_mode() or "-"}')
    print(' '.join(parts))
    return 0


COMMANDS = {
    'setup': cmd_setup, 'login': cmd_login, 'list': cmd_list, 'clone': cmd_clone,
    'refresh': cmd_refresh, 'build': cmd_build, 'mark-synced': cmd_mark_synced,
    'status': cmd_status,
}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    os.environ.setdefault('GHQ_ROOT', ghq_root())
    if not argv or argv[0] not in COMMANDS:
        print(__doc__)
        return 2
    return COMMANDS[argv[0]](argv[1:]) or 0


if __name__ == '__main__':
    sys.exit(main())
