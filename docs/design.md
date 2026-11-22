# How it works

## Overview

```
GitHub
  │  ghq get / git pull  (HTTPS, authenticated by gh)
  ▼
Muse environment (Linux VM)
  ├─ ~/ghq/github.com/<owner>/<repo>           your clones (pull hooks installed)
  ├─ ~/workspace/muse-repo-explorer/           this repository (the tool)
  │    ├─ tools/repo_explorer.py               the one command the agent uses
  │    └─ page/index.html                      the explorer page, ready-made
  └─ ~/workspace/repo-explorer/                state, outside every repository
       ├─ snapshot.json                        text of every file (private, mode 600)
       ├─ dist/index.html + dist/snapshot.json page, two-file form
       ├─ dist/explorer.html                   page, single-file form (data embedded)
       └─ exclude.txt (optional)               files to hide from the page
  │
  │  upload by path; later replace only what `refresh` names
  ▼
Muse space "Repository Explorer"              browse the tree and read code on your phone
```

## Saving tokens

Every step an agent has to *think* about costs tokens. So the design moves as much as possible
from the agent into scripts, and keeps what the agent reads tiny.

| Where tokens usually go | What this project does instead |
| --- | --- |
| Agent writes a page from a spec | The page is bundled (`page/index.html`); the agent only uploads files |
| Agent reads big files to upload them | The prompt forbids opening the snapshot/page; upload by file path |
| Agent reasons about many shell steps | One CLI, one command per step, idempotent |
| Long command output | Every command prints a few lines; per-repository lines only on failure |
| Deciding whether to update the page | `refresh` decides: `UP_TO_DATE` (stop) or `PAGE_UPDATE_NEEDED` + exact file |
| Re-uploading the whole page each time | Two-file form: only `snapshot.json` is replaced |
| Regenerating after every pull | Git hooks do it in scripts (zero tokens) |
| Reading source through a connector | Muse greps local clones and reads only the lines it needs |

## Design decisions

- **Local clones for reading source.** A connector call returns whole files into context; local
  `grep` + partial reads are far cheaper. Issues and PRs still go through the connector.
- **HTTPS + gh device flow.** SSH (port 22) is often blocked in the Muse VM. The device flow never
  exposes a token to the chat; `gh auth setup-git` makes git use it.
- **Snapshot, not a live server.** The Muse VM accepts no inbound connections, so a phone cannot
  reach a server there. The code is embedded in the page as a snapshot instead.
- **Read from HEAD, not the working tree.** `git ls-tree` / `git cat-file` means uncommitted edits
  and symlink targets outside the repository never reach the page, and the content always
  matches the displayed commit.
- **Two delivery forms.** If a Muse space can hold several files, `index.html` fetches
  `snapshot.json` and a refresh replaces only the data. If it holds a single HTML file,
  `explorer.html` carries the data inline (escaped so it can never break out of its `<script>`).
- **Hooks keep the snapshot fresh.** `post-merge` and `post-rewrite` (for `pull --rebase`) rebuild
  the snapshot and `dist/` in the background. While `refresh` pulls, hooks are suppressed and it
  rebuilds once; a lock prevents overlapping runs.
- **The page notices tool updates too.** When this repository's page changes, `refresh` reports
  `new page version` so the page file can be replaced as well.
- **No external dependencies in the page.** No CDN, no fonts, no analytics: nothing leaves the
  page, and it works offline once loaded.
