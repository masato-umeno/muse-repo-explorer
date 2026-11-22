#!/usr/bin/env python3
"""Block anything that must never land in this PUBLIC repository.

Usage:
    python3 scripts/check_public_safety.py            # check all tracked files (CI)
    python3 scripts/check_public_safety.py --staged   # check staged files (pre-commit)

Checks:
  1. Forbidden files: snapshots, logs, sync state, exclude lists, keys, .env, ...
  2. Snapshot-shaped JSON (real source code dumps), whatever the file name.
  3. Secrets: GitHub / AWS / Slack / Anthropic / OpenAI tokens, private keys.
  4. E-mail addresses other than GitHub noreply and example.* placeholders.
  5. Files larger than 200 KB.
  6. Your private denylist (real org / repo / person names), read from
     ~/.config/muse-repo-viewer/denylist.txt  (one word per line, '#' comments).
     That file lives OUTSIDE the repo on purpose -- never commit it.

Exit code 1 if anything is found. Fix the finding; do not bypass with --no-verify.
"""
import argparse
import fnmatch
import os
import re
import subprocess
import sys

MAX_BYTES = 200_000
SELF = 'scripts/check_public_safety.py'

FORBIDDEN_NAMES = [
    'snapshot*.json', '*.log', '.page-state.json', '.page-lang', '.snapshot-dirty',
    '.snapshot.lock', 'exclude.txt', 'denylist.txt', '.env', '.env.*',
    '*.pem', '*.key', '*.p12', '*.pfx', 'id_rsa*', 'id_ed25519*', 'hosts.yml',
    '*.bak-repo-viewer',
]

SECRET_PATTERNS = {
    'GitHub token': r'\b(gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})',
    'AWS access key': r'\bAKIA[0-9A-Z]{16}\b',
    'Slack token': r'\bxox[abposr]-[A-Za-z0-9-]{10,}',
    'Anthropic API key': r'\bsk-ant-[A-Za-z0-9_-]{20,}',
    'OpenAI-style API key': r'\bsk-(proj-)?[A-Za-z0-9]{32,}',
    'Google API key': r'\bAIza[0-9A-Za-z_-]{35}\b',
    'Private key': r'-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY',
}

EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
EMAIL_OK = re.compile(
    r'(@users\.noreply\.github\.com|@example\.(com|org|net)|@anthropic\.com)$', re.I)
SNAPSHOT_SHAPE = re.compile(r'"generated_at".{0,200}"repos"\s*:\s*\[\s*\{\s*"id"', re.S)

DENYLIST = os.path.expanduser('~/.config/muse-repo-viewer/denylist.txt')


def git(*args, binary=False):
    r = subprocess.run(['git', *args], capture_output=True, check=True)
    return r.stdout if binary else r.stdout.decode('utf-8', errors='replace')


def file_list(staged):
    if staged:
        out = git('diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z')
    else:
        out = git('ls-files', '-z')
    return [p for p in out.split('\0') if p]


def read(path, staged):
    if staged:
        return git('show', f':{path}', binary=True)
    with open(path, 'rb') as fh:
        return fh.read()


def load_denylist():
    try:
        with open(DENYLIST, encoding='utf-8') as fh:
            return [w.strip() for w in fh if w.strip() and not w.startswith('#')]
    except OSError:
        return []


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--staged', action='store_true')
    args = ap.parse_args(argv)
    os.chdir(git('rev-parse', '--show-toplevel').strip())

    deny = load_denylist()
    deny_re = re.compile('|'.join(re.escape(w) for w in deny), re.I) if deny else None
    problems = []

    for path in file_list(args.staged):
        name = path.rsplit('/', 1)[-1]
        for pat in FORBIDDEN_NAMES:
            if fnmatch.fnmatch(name, pat):
                problems.append(f'{path}: forbidden file type ({pat})')
        try:
            raw = read(path, args.staged)
        except (OSError, subprocess.CalledProcessError):
            continue
        if len(raw) > MAX_BYTES:
            problems.append(f'{path}: too large ({len(raw)} bytes) -- is this a data dump?')
        if b'\0' in raw[:8192]:
            continue
        text = raw.decode('utf-8', errors='replace')
        # Markdown may show a tiny format example; real dumps are .json or similar.
        if not path.endswith('.md') and SNAPSHOT_SHAPE.search(text):
            problems.append(f'{path}: looks like a snapshot (real source code)')
        if path == SELF:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for label, pat in SECRET_PATTERNS.items():
                if re.search(pat, line):
                    problems.append(f'{path}:{lineno}: {label}')
            for m in EMAIL.finditer(line):
                if not EMAIL_OK.search(m.group(0)):
                    problems.append(f'{path}:{lineno}: e-mail address ({m.group(0)})')
            if deny_re and (m := deny_re.search(line)):
                # Do not echo the matched word in CI logs; the line number is enough.
                problems.append(f'{path}:{lineno}: matches your private denylist')

    if problems:
        print('PUBLIC SAFETY CHECK FAILED -- this repository is public.', file=sys.stderr)
        for p in problems:
            print('  ' + p, file=sys.stderr)
        print('Remove or replace with placeholders such as your-org/your-repo.',
              file=sys.stderr)
        return 1
    print(f'public safety check passed'
          + ('' if deny else ' (no private denylist found; see CONTRIBUTING.md)'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
