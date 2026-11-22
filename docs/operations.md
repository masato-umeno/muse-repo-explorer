# Operations

## Refreshing the page

```sh
cd ~/workspace/repo-explorer
python3 update_snapshot.py      # pull everything, rebuild snapshot.json (no tokens)
python3 sync_status.py          # exit 0: up to date / exit 10: page needs update
# only if exit code was 10:
#   replace the page's snapshot asset with snapshot.json, then
python3 sync_status.py --mark
```

`sync_status.py` compares the HEADs in `snapshot.json` with `.page-synced-heads`
(written by `--mark`), so in a week where nothing changed the agent does nothing.

To piggyback on an existing recurring job (e.g. a weekly check), append the steps above to
that job's instructions.

## What runs automatically

- After `git pull` (merge or rebase) in any clone, the hook rebuilds `snapshot.json` in the
  background and logs to `snapshot-hook.log`.
- `.snapshot-dirty` appears whenever a HEAD changes and disappears on `sync_status.py --mark`.

## State files in `~/workspace/repo-explorer`

| File | Meaning |
| --- | --- |
| `snapshot.json` | The data embedded in the page (private source code, mode 600) |
| `.page-synced-heads` | HEADs last pushed to the page |
| `.snapshot-dirty` | A HEAD changed since the page was last updated |
| `exclude.txt` | Your globs for files to hide (optional) |
| `snapshot-hook.log` | Output of hook-triggered runs |

## Common situations

- **Cloned a new repository / re-cloned one:** run `install-hooks.sh` again (safe to repeat).
- **`pull failed` in the output:** the clone has local commits or diverged; fix it in that
  clone. Other repositories are still processed.
- **`skipped (no upstream)`:** the branch has no tracking branch; it is snapshotted as is.
- **Page is slow / snapshot too large:** add big generated directories (e.g. `dist/*`,
  `vendor/*`) to `exclude.txt`.

## Uninstalling

```sh
gh auth logout
rm -rf ~/workspace/repo-explorer
# hooks: remove .git/hooks/post-merge and post-rewrite from each clone
#        (restore *.bak-repo-explorer if you had your own)
```

Clones are ordinary git repositories; delete them as you like. Delete the explorer page in Muse.
