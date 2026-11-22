# Reference

## Commands

`tools/repo_viewer.py` provides one command per step. All commands are idempotent.

| Command | Description | Output |
| --- | --- | --- |
| `next` | Determines the current state, refreshes when repositories exist, and prints the single next action (`NEXT (n/5 …)`, `DONE` or `STOP`) | A few lines of instructions |
| `setup [--lang en\|ja\|zh-CN\|ko\|auto]` | Installs ghq and gh into `~/.local/bin` and the verified Mermaid build if missing, records the page's initial language (`auto`: follow the browser), and reports the sign-in state | One line per item |
| `login` | Starts the GitHub device flow in the background | URL and one-time code |
| `login --wait` | Waits up to 15 minutes for approval, then runs `gh auth setup-git` | Account name |
| `list [--all]` | Lists repositories of the account and its organizations; archived ones only with `--all` | One line per repository with flags |
| `clone OWNER/REPO …` | Clones with ghq and installs hooks | Counts and the total number of repositories |
| `refresh [--no-pull]` | Pulls, rebuilds the snapshot and the page files, and lists the files to upload or delete | Totals and a result line |
| `mark-synced [--mode folder\|single-file]` | Records that the space shows the current build; `--mode` is required the first time | Confirmation |
| `status` | Summarizes the current state | One line |
| `build` | Rebuilds the snapshot and the page files without pulling; used by the hooks | None |

`refresh` ends with one of these results:

| Result | Exit status | Meaning |
| --- | --- | --- |
| `UP_TO_DATE` | 0 | The space already shows the current build |
| `PAGE_UPDATE_NEEDED` | 0 | Followed by the files to upload and, if any, the files to delete |
| `NO_REPOSITORIES` | 3 | No repository is cloned; at least one is required |

`next` asks for `--lang` until an initial language has been recorded. Unsupported languages and
`auto` are recorded as unset, and the page then follows the browser. Viewers can override the
language in the page's settings.

Lower-level scripts in `tools/` can also be used on their own:

| Script | Description |
| --- | --- |
| `update_snapshot.py [--no-pull] [--quiet]` | Pulls all clones and writes `snapshot.json` |
| `install-hooks.sh` | Installs `post-merge` and `post-rewrite` hooks in every clone; existing hooks are backed up |
| `on-pull.sh` | Hook entry point; runs `build` in the background |

## Configuration

| Environment variable | Default | Description |
| --- | --- | --- |
| `GHQ_ROOT` | Output of `ghq root`, otherwise `~/ghq` | Location of the clones |
| `REPO_VIEWER_HOME` | `~/workspace/repo-viewer` | Location of the snapshot, page files and state |
| `REPO_VIEWER_MERMAID_FILE` | Not set | A local `mermaid.min.js` to install instead of downloading it; it must still match the pinned checksum |

## State files

All files are in `REPO_VIEWER_HOME`.

| File | Description |
| --- | --- |
| `snapshot.json` | Text content of all included repositories (mode 600) |
| `dist/site/` | Folder form of the page (see [Viewer page](page.md#delivery)) |
| `dist/viewer.html` | Single-file form of the page |
| `vendor/mermaid-<version>.min.js` | Verified Mermaid build |
| `exclude.txt` | Optional glob patterns for files to hide |
| `.page-lang` | Initial page language (`en`, `ja`, `zh-CN`, `ko`, or empty for the browser setting) |
| `.page-state.json` | Form of the space and checksums of the files it currently holds |
| `.setup-version` | Setup version last completed; `next` asks for `setup` again when the tool requires a newer one |
| `.star-note-shown` | Marks that the one-time note about starring the repository was shown (a short line in the user's language, then the repository URL on its own line) |
| `.snapshot-dirty` | Present when commits have changed since the last update of the space |
| `.snapshot.lock`, `.build.lock` | Prevent concurrent rebuilds |
| `snapshot-hook.log`, `.login.log` | Logs |

## Snapshot format

`snapshot.json` is the intermediate format from which the page files are built.

```json
{
  "generated_at": "2026-11-22T10:24:53+09:00",
  "repos": [
    {
      "id": "your-org/your-repo",
      "branch": "main",
      "head": "abc1234",
      "committed_at": "2026-11-21T18:02:11+09:00",
      "local": "~/ghq/github.com/your-org/your-repo",
      "files": [
        {"path": "src/main.ts", "size": 1234, "content": "file text (UTF-8)"},
        {"path": "assets/logo.png", "size": 5678, "skipped": "binary"}
      ]
    }
  ]
}
```

Only text files have `content`. All other files have `skipped` set to one of the following:

| Value | Meaning |
| --- | --- |
| `binary` | The file contains a NUL byte in its first 8 KB |
| `large` | The file is larger than 300 KB |
| `excluded` | The file matches a pattern in `exclude.txt` |
| `symlink` | The entry is a symbolic link; the target is not read |
| `submodule` | The entry is a submodule; its content is not included |
