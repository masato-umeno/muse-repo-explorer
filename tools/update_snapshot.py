#!/usr/bin/env python3
"""ghq配下の全リポジトリを pull して、エクスプローラー用スナップショットJSONを再生成する。

使い方:
    python3 update_snapshot.py [--no-pull]

環境変数:
    GHQ_ROOT          ghq のルート（省略時: `ghq root` の出力、無ければ ~/ghq）
    REPO_EXPLORER_HOME スナップショットの出力先ディレクトリ
                       （省略時: ~/workspace/repo-explorer）

出力: $REPO_EXPLORER_HOME/snapshot.json
ルール: git管理下のファイルのみ。バイナリと300KB超のファイルは content を持たず、
        skipped ("binary" / "large") を付けてツリー表示だけできるようにする。
"""
import subprocess, os, json, sys, datetime


def default_ghq_root():
    try:
        out = subprocess.run(['ghq', 'root'], capture_output=True, text=True)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except FileNotFoundError:
        pass
    return os.path.expanduser('~/ghq')


GHQ = os.environ.get('GHQ_ROOT', default_ghq_root())
HOME_DIR = os.environ.get(
    'REPO_EXPLORER_HOME', os.path.expanduser('~/workspace/repo-explorer'))
OUT = os.path.join(HOME_DIR, 'snapshot.json')
MAX_FILE = 300_000


def git(d, *args):
    return subprocess.run(['git', '-C', d, *args],
                          capture_output=True, text=True).stdout.strip()


def main():
    do_pull = '--no-pull' not in sys.argv
    repos = []
    for host in sorted(os.listdir(GHQ)):
        host_dir = os.path.join(GHQ, host)
        if not os.path.isdir(host_dir):
            continue
        for owner in sorted(os.listdir(host_dir)):
            owner_dir = os.path.join(host_dir, owner)
            if not os.path.isdir(owner_dir):
                continue
            for repo in sorted(os.listdir(owner_dir)):
                d = os.path.join(owner_dir, repo)
                if os.path.isdir(os.path.join(d, '.git')):
                    repos.append((f'{owner}/{repo}', d))
    snapshot = {
        'generated_at': datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec='seconds'),
        'repos': [],
    }
    for repo_id, d in repos:
        if do_pull:
            r = subprocess.run(['git', '-C', d, 'pull', '--ff-only'],
                               capture_output=True, text=True)
            status = 'pulled' if r.returncode == 0 else f'pull failed: {r.stderr.strip()[:80]}'
        else:
            status = 'no-pull'
        entries = []
        for f in git(d, 'ls-files').splitlines():
            p = os.path.join(d, f)
            try:
                sz = os.path.getsize(p)
            except OSError:
                continue
            if sz > MAX_FILE:
                entries.append({'path': f, 'size': sz, 'skipped': 'large'})
                continue
            with open(p, 'rb') as fh:
                raw = fh.read()
            if b'\x00' in raw[:8192]:
                entries.append({'path': f, 'size': sz, 'skipped': 'binary'})
                continue
            entries.append({'path': f, 'size': sz,
                            'content': raw.decode('utf-8', errors='replace')})
        snapshot['repos'].append({
            'id': repo_id,
            'branch': git(d, 'branch', '--show-current'),
            'head': git(d, 'rev-parse', '--short', 'HEAD'),
            'files': entries,
        })
        print(f'{repo_id}: {status}, files={len(entries)}')
    os.makedirs(HOME_DIR, exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(snapshot, fh, ensure_ascii=False, separators=(',', ':'))
    print(f'written {OUT} ({os.path.getsize(OUT) / 1024 / 1024:.1f} MB)')


if __name__ == '__main__':
    main()
