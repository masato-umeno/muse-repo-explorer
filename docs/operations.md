# Operations

`rx` below means `python3 ~/workspace/muse-repo-explorer/tools/repo_explorer.py`.

## Refreshing the page

```sh
rx refresh
```

- `UP_TO_DATE: …` → nothing to do (no tokens spent beyond this one command).
- `PAGE_UPDATE_NEEDED: …` → replace exactly the file(s) it names in the page, then `rx mark-synced`.

| Page form | Usually replaced | When the tool's page changed |
| --- | --- | --- |
| two-file | `dist/snapshot.json` | also `dist/index.html` |
| single-file | `dist/explorer.html` | `dist/explorer.html` (same) |

To piggyback on an existing recurring job (e.g. a weekly check), add the two lines above to the
end of that job.

## Updating the tool itself

```sh
git -C ~/workspace/muse-repo-explorer pull --ff-only
rx refresh          # reports "new page version" if the page changed
```

Pasting the README prompt again does the same.

## What runs automatically

- After `git pull` (merge or rebase) in any clone, the hook rebuilds `snapshot.json` and `dist/`
  in the background (log: `snapshot-hook.log`). The page itself is only changed by you/Muse.
- `.snapshot-dirty` appears whenever a HEAD changes and disappears on `mark-synced`.

## State files in `~/workspace/repo-explorer`

| File | Meaning |
| --- | --- |
| `snapshot.json` | All repositories' text files (private source code, mode 600) |
| `dist/` | Page files ready to upload (mode 600, directory 700) |
| `.page-synced-heads` | HEADs the page currently shows |
| `.page-mode` | `two-file` or `single-file` |
| `.page-template-hash` | Version of the page file currently uploaded |
| `.snapshot-dirty` | A HEAD changed since the page was last updated |
| `exclude.txt` | Your globs for files to hide (optional) |
| `snapshot-hook.log`, `.login.log` | Logs |

## Common situations

- **Added a repository:** `rx clone owner/repo`, then `rx refresh`.
- **Removed a repository:** delete its clone directory, then `rx refresh` (reported as changed).
- **`pull failed` lines:** that clone has local commits or diverged; fix it there. Others still update.
- **`skipped (no upstream)`:** the branch tracks nothing; it is snapshotted as is.
- **Page slow / snapshot large:** add generated directories (`dist/*`, `vendor/*`, `*.min.js`) to
  `exclude.txt`, then `rx refresh --no-pull`.
- **Sign-in expired:** `rx login`, then `rx login --wait`.

## Uninstalling

```sh
gh auth logout
rm -rf ~/workspace/repo-explorer ~/workspace/muse-repo-explorer
# in each clone, remove .git/hooks/post-merge and post-rewrite
# (restore *.bak-repo-explorer if you had your own hooks)
```

Clones are ordinary git repositories; delete them as you like. Delete the page in Muse.
