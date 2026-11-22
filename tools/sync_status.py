#!/usr/bin/env python3
"""Tell whether the explorer page needs its data replaced.

Compares the HEADs in snapshot.json with the HEADs recorded the last time the
page was updated (.page-synced-heads).

Usage:
    python3 sync_status.py           # exit 0 = up to date, exit 10 = page needs update
    python3 sync_status.py --mark    # record current snapshot HEADs as synced,
                                     # and clear .snapshot-dirty

Run --mark only after the page data has actually been replaced.
"""
import argparse
import json
import os
import sys

NEEDS_UPDATE = 10


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--mark', action='store_true',
                    help='record the current snapshot as reflected on the page')
    args = ap.parse_args(argv)

    home = os.environ.get('REPO_EXPLORER_HOME',
                          os.path.expanduser('~/workspace/repo-explorer'))
    snap_path = os.path.join(home, 'snapshot.json')
    synced_path = os.path.join(home, '.page-synced-heads')
    dirty_path = os.path.join(home, '.snapshot-dirty')

    try:
        with open(snap_path, encoding='utf-8') as fh:
            current = {r['id']: r['head'] for r in json.load(fh)['repos']}
    except (OSError, ValueError, KeyError) as e:
        print(f'error: cannot read {snap_path}: {e}', file=sys.stderr)
        return 1

    if args.mark:
        with open(synced_path, 'w', encoding='utf-8') as fh:
            json.dump(current, fh, indent=2, sort_keys=True)
        if os.path.exists(dirty_path):
            os.unlink(dirty_path)
        print(f'marked {len(current)} repos as synced')
        return 0

    try:
        with open(synced_path, encoding='utf-8') as fh:
            synced = json.load(fh)
    except (OSError, ValueError):
        synced = {}

    changed = sorted(k for k in current if synced.get(k) != current[k])
    removed = sorted(k for k in synced if k not in current)
    if not changed and not removed:
        print('up to date')
        return 0
    for k in changed:
        print(f'changed: {k} {synced.get(k, "(new)")} -> {current[k]}')
    for k in removed:
        print(f'removed: {k}')
    return NEEDS_UPDATE


if __name__ == '__main__':
    sys.exit(main())
