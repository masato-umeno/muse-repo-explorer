# Manual setup

This document describes the steps performed by the setup prompt, for users who prefer to run
them directly or with Claude Code.

## Requirements

- Linux
- git
- Python 3.8 or later

`ghq` and `gh` are installed into `~/.local/bin` by `setup` if they are not already available.
`setup` also installs a verified Mermaid build; if this fails, diagrams are shown as source.

## Steps

```sh
git clone https://github.com/masato-umeno/muse-repo-explorer ~/workspace/muse-repo-explorer
alias rx='python3 ~/workspace/muse-repo-explorer/tools/repo_explorer.py'
```

1. Install the required tools and set the page language (`en`, `ja`, `zh-CN` or `ko`):

   ```sh
   rx setup --lang en
   ```

2. Sign in to GitHub. `login` prints a URL and a one-time code; enter the code in a browser,
   then run `login --wait`, which returns after the approval and configures git:

   ```sh
   rx login
   rx login --wait
   ```

3. Clone the repositories to include. At least one is required. `list` shows the repositories
   available to the account and its organizations; this repository can be used as a sample:

   ```sh
   rx list
   rx clone your-org/your-repo your-name/another-repo
   rx clone masato-umeno/muse-repo-explorer        # sample
   ```

4. Build the snapshot and the page files:

   ```sh
   rx refresh
   ```

5. Create a private Muse space from `~/workspace/repo-explorer/dist/site/` (keeping the `data/`
   folder) or, if a space can hold only one HTML file, from `dist/explorer.html`. See
   [Explorer page](page.md#delivery). Then record the form used:

   ```sh
   rx mark-synced --mode folder    # or --mode single-file
   ```

For ongoing use, see [Operations](operations.md). All commands are listed in
[Reference](reference.md).
