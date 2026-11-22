# Manual setup

This document describes the steps performed by the setup prompt, for users who prefer to run
them directly or with Claude Code.

## Requirements

- Linux
- git
- Python 3.8 or later

`ghq` and `gh` are installed into `~/.local/bin` by `setup` if they are not already available.

## Steps

```sh
git clone https://github.com/masato-umeno/muse-repo-explorer ~/workspace/muse-repo-explorer
alias rx='python3 ~/workspace/muse-repo-explorer/tools/repo_explorer.py'
```

1. Install the required tools:

   ```sh
   rx setup
   ```

2. Sign in to GitHub. `login` prints a URL and a one-time code; enter the code in a browser,
   then run `login --wait`, which returns after the approval and configures git:

   ```sh
   rx login
   rx login --wait
   ```

3. Clone the repositories to include. `list` shows the repositories available to the account
   and its organizations:

   ```sh
   rx list
   rx clone your-org/your-repo your-name/another-repo
   ```

4. Build the snapshot and the page files:

   ```sh
   rx refresh
   ```

5. Create a private Muse space from the files in `~/workspace/repo-explorer/dist/`, using one of
   the two forms described in [Explorer page](page.md#delivery), and record the form used:

   ```sh
   rx mark-synced --mode two-file    # or --mode single-file
   ```

For ongoing use, see [Operations](operations.md). All commands are listed in
[Reference](reference.md).
