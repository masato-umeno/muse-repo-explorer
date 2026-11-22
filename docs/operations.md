# Operations

In this document, `rx` stands for `python3 ~/workspace/muse-repo-explorer/tools/repo_explorer.py`.

## Refreshing the space

```sh
rx refresh
```

The output ends with one of these results:

- `UP_TO_DATE`: the space already shows the latest commits. No action is required.
- `PAGE_UPDATE_NEEDED`: upload the files listed, delete the files listed for deletion, then run
  `rx mark-synced`.
- `NO_REPOSITORIES`: no repository is cloned. Clone at least one (see below).

In the folder form, the files listed are the index (`data/index.json.gz`) and the content files
of the repositories that changed. The page file (`index.html`) and Mermaid are listed only when
they have changed. In the single-file form, `explorer.html` is replaced as a whole.

To refresh on a schedule, add these steps to the end of an existing recurring job.

## Automatic rebuilds

After a `git pull` in any clone (merge or rebase), a git hook rebuilds the snapshot and the page
files in the background and writes its output to `snapshot-hook.log`. The space itself is changed
only by a refresh.

## Maintenance

| Task | Procedure |
| --- | --- |
| Add a repository | `rx clone owner/repo`, then `rx refresh` |
| Remove a repository | Delete its clone directory, then `rx refresh` (its file is listed for deletion) |
| Use the sample repository | `rx clone masato-umeno/muse-repo-explorer`, then `rx refresh` |
| Hide files | Add glob patterns to `exclude.txt`, then `rx refresh --no-pull` |
| Change the language for yourself | Use the gear button on the page |
| Change the initial page language | `rx setup --lang ko` (or `en`, `ja`, `zh-CN`, `auto`), then `rx refresh` |
| Install Mermaid later | `rx setup`, then `rx refresh` |
| Update the tool | `git -C ~/workspace/muse-repo-explorer pull --ff-only`, then `rx refresh` |
| Renew the GitHub sign-in | `rx login`, then `rx login --wait` |

Patterns in `exclude.txt` are matched against the path within the repository, the file name,
and `owner/repo/path`. Lines starting with `#` are ignored.

```
.env*
*.pem
your-org/your-repo/secrets/*
```

## Troubleshooting

| Output | Cause | Action |
| --- | --- | --- |
| `pull failed: …` | The clone has local commits or has diverged from its upstream | Resolve it in that clone; other repositories are still processed |
| `skipped (no upstream)` | The current branch has no tracking branch | None required; the branch is captured as it is |
| `refusing to write: …` | The state directory is inside an unignored git working tree | Use the default location or set `REPO_EXPLORER_HOME` |
| `could not get a device code` | gh could not reach GitHub | Check network access and run `rx login` again |
| `mermaid: not installed (…)` | The download failed or the checksum did not match | Diagrams are shown as source; run `rx setup` again later |
| `diagrams: off` in refresh output | Mermaid is not installed | Run `rx setup`, then `rx refresh` |
| "This browser cannot read the data" on the page | The browser lacks `DecompressionStream` | Update the browser (Safari 16.4 or later, current Chrome or Firefox) |

## Uninstalling

1. Run `gh auth logout`.
2. Remove `~/workspace/repo-explorer` and `~/workspace/muse-repo-explorer`.
3. In each clone, remove `.git/hooks/post-merge` and `.git/hooks/post-rewrite`, and restore
   any `*.bak-repo-explorer` backups.
4. Delete the explorer space in Muse.

Clones are ordinary git repositories and can be kept or removed as needed.
