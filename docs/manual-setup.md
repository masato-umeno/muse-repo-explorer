# Manual setup

For people (or Claude Code) who want to run the steps themselves instead of pasting the prompt.

Requirements: Linux, `git`, `python3` (3.8+). `ghq` and `gh` are installed by `setup` if missing
(into `~/.local/bin`).

```sh
git clone https://github.com/masato-umeno/muse-repo-explorer ~/workspace/muse-repo-explorer
alias rx='python3 ~/workspace/muse-repo-explorer/tools/repo_explorer.py'

rx setup                   # install ghq / gh if missing, show sign-in state
rx login                   # prints a URL and a one-time code
rx login --wait            # returns when you approve in the browser; configures git
rx list                    # repositories you can access (archived hidden; --all to show)
rx clone your-org/your-repo your-name/another-repo
rx refresh                 # pull, snapshot, build dist/, say what to upload
```

Then create the page from `~/workspace/repo-explorer/dist/` (see
[explorer-page-spec.md](explorer-page-spec.md#delivery)) and record it:

```sh
rx mark-synced --mode two-file      # or: --mode single-file
```

Optional — hide files from the page:

```sh
cat > ~/workspace/repo-explorer/exclude.txt <<'EOF'
# one glob per line; matched against path, file name and owner/repo/path
.env*
*.pem
your-org/your-repo/secrets/*
EOF
rx refresh --no-pull
```

## Command reference

| Command | Output (short) | Notes |
| --- | --- | --- |
| `setup` | `ghq: ok`, `gh: ok`, sign-in state | Downloads latest release binaries if missing |
| `login` | URL + code | Starts `gh auth login --web` in the background |
| `login --wait` | `signed in as …` | Polls up to 15 min, then `gh auth setup-git` |
| `list [--all]` | `owner/repo  [private,fork,cloned]` | Your account and your organizations |
| `clone OWNER/REPO …` | `cloned: N ok, M failed` | Uses `ghq get`; installs hooks |
| `refresh [--no-pull]` | stats + `UP_TO_DATE` or `PAGE_UPDATE_NEEDED` | Also (re)installs hooks |
| `mark-synced [--mode …]` | `marked N repos as synced` | Run after the page was updated |
| `status` | one line | For quick checks |
| `build` | — | Snapshot + `dist/` without pulling (used by hooks) |

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `GHQ_ROOT` | `ghq root`, else `~/ghq` | Where clones live |
| `REPO_EXPLORER_HOME` | `~/workspace/repo-explorer` | Snapshot, `dist/` and state |

## Lower-level scripts

`repo_explorer.py` is a thin layer over these; they still work on their own.

| Script | Purpose |
| --- | --- |
| `update_snapshot.py [--no-pull] [--quiet]` | Pull all clones (`--ff-only`) and write `snapshot.json` |
| `sync_status.py [--mark]` | Exit 10 if the page is out of date |
| `install-hooks.sh` | Install `post-merge` / `post-rewrite` hooks into every clone |
| `on-pull.sh` | Hook body; rebuilds in the background |
