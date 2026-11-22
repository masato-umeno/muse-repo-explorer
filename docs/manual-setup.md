# Manual setup

For people (or Claude Code) who want to set it up without the prompt in the README.
Steps 1–5 reproduce everything except the explorer page; for the page, see
[explorer-page-spec.md](explorer-page-spec.md).

Requirements: `git`, `python3` (3.8+), a POSIX shell.

## 1. Install ghq and gh

Place the latest release binaries of [ghq](https://github.com/x-motemen/ghq) and
[gh](https://github.com/cli/cli) in `~/.local/bin`, then:

```sh
ghq --version
gh --version
```

## 2. Sign in to GitHub (HTTPS, device flow)

```sh
gh auth login --hostname github.com --git-protocol https --web
gh auth status
gh auth setup-git
```

## 3. Clone repositories

```sh
gh repo list                 # your repositories
gh repo list your-org        # an organization's repositories
ghq get your-org/your-repo
```

## 4. Install the tools

```sh
ghq get https://github.com/masato-umeno/muse-repo-explorer
mkdir -p ~/workspace/repo-explorer
cp "$(ghq root)"/github.com/masato-umeno/muse-repo-explorer/tools/* ~/workspace/repo-explorer/
chmod +x ~/workspace/repo-explorer/*.sh ~/workspace/repo-explorer/*.py
python3 ~/workspace/repo-explorer/update_snapshot.py
```

Optional — hide files from the page:

```sh
cat > ~/workspace/repo-explorer/exclude.txt <<'EOF'
# one glob per line; matched against path, file name and owner/repo/path
.env*
*.pem
your-org/your-repo/secrets/*
EOF
```

## 5. Install the pull hooks

```sh
~/workspace/repo-explorer/install-hooks.sh
```

Existing `post-merge` / `post-rewrite` hooks are backed up as `*.bak-repo-explorer`.

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `GHQ_ROOT` | `ghq root`, else `~/ghq` | Where clones live |
| `REPO_EXPLORER_HOME` | `~/workspace/repo-explorer` | Tools, snapshot and state |

## Tools reference

| Tool | Purpose |
| --- | --- |
| `update_snapshot.py [--no-pull] [--quiet]` | Pull all clones (`--ff-only`) and write `snapshot.json` |
| `sync_status.py [--mark]` | Exit 10 if the page is out of date; `--mark` records it as updated |
| `install-hooks.sh` | Install `post-merge` / `post-rewrite` hooks into every clone |
| `on-pull.sh` | Hook body; regenerates the snapshot in the background |
