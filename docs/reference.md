# Reference

## Commands

`tools/repo_explorer.py` provides one command per step. All commands are idempotent.

| Command | Description | Output |
| --- | --- | --- |
| `setup` | Installs ghq and gh into `~/.local/bin` if missing and reports the sign-in state | Tool status and account |
| `login` | Starts the GitHub device flow in the background | URL and one-time code |
| `login --wait` | Waits up to 15 minutes for approval, then runs `gh auth setup-git` | Account name |
| `list [--all]` | Lists repositories of the account and its organizations; archived ones only with `--all` | One line per repository with flags |
| `clone OWNER/REPO …` | Clones with ghq and installs hooks | Counts of successes and failures |
| `refresh [--no-pull]` | Pulls, rebuilds the snapshot and `dist/`, and reports whether the page needs updating | Totals and a result line |
| `mark-synced [--mode two-file\|single-file]` | Records that the page shows the current snapshot; `--mode` is required the first time | Confirmation |
| `status` | Summarizes the current state | One line |
| `build` | Rebuilds the snapshot and `dist/` without pulling; used by the hooks | None |

Lower-level scripts in `tools/` can also be used on their own:

| Script | Description |
| --- | --- |
| `update_snapshot.py [--no-pull] [--quiet]` | Pulls all clones and writes `snapshot.json` |
| `sync_status.py [--mark]` | Exits with status 10 if the page is out of date |
| `install-hooks.sh` | Installs `post-merge` and `post-rewrite` hooks in every clone; existing hooks are backed up |
| `on-pull.sh` | Hook entry point; runs `build` in the background |

## Configuration

| Environment variable | Default | Description |
| --- | --- | --- |
| `GHQ_ROOT` | Output of `ghq root`, otherwise `~/ghq` | Location of the clones |
| `REPO_EXPLORER_HOME` | `~/workspace/repo-explorer` | Location of the snapshot, page files and state |

## State files

All files are in `REPO_EXPLORER_HOME`.

| File | Description |
| --- | --- |
| `snapshot.json` | Text content of all included repositories (mode 600) |
| `dist/` | Page files ready for upload (mode 700) |
| `exclude.txt` | Optional glob patterns for files to hide |
| `.page-synced-heads` | Commit IDs currently shown on the page |
| `.page-mode` | `two-file` or `single-file` |
| `.page-template-hash` | Version of the page file currently uploaded |
| `.snapshot-dirty` | Present when commits have changed since the last page update |
| `.snapshot.lock` | Prevents concurrent rebuilds |
| `snapshot-hook.log`, `.login.log` | Logs |

## Snapshot format

```json
{
  "generated_at": "2026-11-22T10:24:53+09:00",
  "repos": [
    {
      "id": "your-org/your-repo",
      "branch": "main",
      "head": "abc1234",
      "committed_at": "2026-11-21T18:02:11+09:00",
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
