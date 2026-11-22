# How it works

## Overview

```
GitHub
  │  ghq get / git pull  (HTTPS, authenticated by gh)
  ▼
Muse environment (Linux VM)
  ├─ ~/ghq/github.com/<owner>/<repo>      local clones
  ├─ ~/workspace/repo-explorer/
  │    ├─ update_snapshot.py              pull all clones, build snapshot.json
  │    ├─ on-pull.sh                      run by the pull hooks (no tokens used)
  │    ├─ install-hooks.sh                put hooks into every clone
  │    ├─ sync_status.py                  "does the page need updating?"
  │    ├─ exclude.txt        (optional)   files to hide from the page
  │    └─ snapshot.json                   text of every file, all repositories
  │
  │  replace the asset — only when a HEAD changed
  ▼
Muse space "Repository Explorer"         browse the tree and read code on your phone
```

## Design decisions

- **Read source from local clones.** Through a connector, every file is an API call and its
  whole content lands in context. Locally, Muse can `grep` first and read only the lines it
  needs, so wide exploration costs far fewer tokens. Issues and PRs still go through the
  connector.
- **HTTPS + gh authentication.** Port 22 (SSH) is often blocked in the Muse VM. The device flow
  (`gh auth login --web`) plus `gh auth setup-git` works reliably and never exposes a token.
- **Snapshot instead of a live connection.** The Muse VM does not accept inbound connections
  (a code-server would not be reachable from a phone), so the code is embedded in the page
  as a snapshot. The trade-off: refreshing means "regenerate the snapshot, then replace the
  page data".
- **Read from HEAD, not the working tree.** The snapshot is built with `git ls-tree` /
  `git cat-file`, so uncommitted edits and symlink targets outside the repository can never
  leak into the page, and the content always matches the displayed commit.
- **Hooks do the regeneration.** `post-merge` and `post-rewrite` (for `pull --rebase`) hooks
  rebuild the snapshot after every pull. This is pure scripting, so it costs no tokens.
  While `update_snapshot.py` pulls by itself, hooks are suppressed and it rebuilds once at the
  end; a lock file prevents overlapping runs.
- **Update the page only when something changed.** Replacing the page data needs the agent.
  `sync_status.py` compares the snapshot's HEADs with those last pushed to the page, so the
  agent only acts (and spends tokens) when a repository actually moved.

## Snapshot format

See [explorer-page-spec.md](explorer-page-spec.md#snapshot-format).
