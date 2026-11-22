# Operations

In this document, `rx` stands for `python3 ~/workspace/muse-repo-explorer/tools/repo_explorer.py`.

## Refreshing the page

```sh
rx refresh
```

The output ends with one of two results:

- `UP_TO_DATE`: the page already shows the latest commits. No action is required.
- `PAGE_UPDATE_NEEDED`: replace the file or files named in the output, then run
  `rx mark-synced`.

| Page form | File replaced after new commits | Additional file after a tool update |
| --- | --- | --- |
| Two-file | `dist/snapshot.json` | `dist/index.html` |
| Single-file | `dist/explorer.html` | None |

To refresh on a schedule, add these steps to the end of an existing recurring job.

## Automatic rebuilds

After a `git pull` in any clone (merge or rebase), a git hook rebuilds `snapshot.json` and
`dist/` in the background and writes its output to `snapshot-hook.log`. The page itself is
changed only by a refresh.

## Maintenance

| Task | Procedure |
| --- | --- |
| Add a repository | `rx clone owner/repo`, then `rx refresh` |
| Remove a repository | Delete its clone directory, then `rx refresh` |
| Hide files | Add glob patterns to `exclude.txt`, then `rx refresh --no-pull` |
| Update the tool | `git -C ~/workspace/muse-repo-explorer pull --ff-only`, then `rx refresh` |
| Renew the GitHub sign-in | `rx login`, then `rx login --wait` |

Patterns in `exclude.txt` are matched against the path within the repository, the file name,
and `owner/repo/path`. Lines starting with `#` are ignored.

```
.env*
*.pem
your-org/your-repo/secrets/*
```

When the tool is updated and the bundled page has changed, `refresh` reports
`new page version` and names the page file to replace.

## Troubleshooting

| Output | Cause | Action |
| --- | --- | --- |
| `pull failed: …` | The clone has local commits or has diverged from its upstream | Resolve it in that clone; other repositories are still processed |
| `skipped (no upstream)` | The current branch has no tracking branch | None required; the branch is captured as it is |
| `refusing to write: …` | The state directory is inside an unignored git working tree | Use the default location or set `REPO_EXPLORER_HOME` |
| `could not get a device code` | gh could not reach GitHub | Check network access and run `rx login` again |
| Page loads slowly | The snapshot is large | Exclude generated directories such as `dist/*` or `vendor/*` |

## Uninstalling

1. Run `gh auth logout`.
2. Remove `~/workspace/repo-explorer` and `~/workspace/muse-repo-explorer`.
3. In each clone, remove `.git/hooks/post-merge` and `.git/hooks/post-rewrite`, and restore
   any `*.bak-repo-explorer` backups.
4. Delete the explorer page in Muse.

Clones are ordinary git repositories and can be kept or removed as needed.
