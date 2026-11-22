# muse-repo-explorer

**English** | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [한국어](README.ko.md)

Read your GitHub code from your phone, and let Muse (your personal AI agent) read it cheaply.

- **Muse reads code from local clones**: faster than a connector, and far fewer tokens.
- **You browse code on your phone** in a private explorer page (a Muse space). The page is
  bundled here, available in English / 日本語 / 中文 / 한국어, with light and dark themes.

## Get started: paste this into Muse

Copy the whole block and send it to Muse. You only need to do two things:
approve the GitHub sign-in code, and choose which repositories to include.

````text
Set up "muse-repo-explorer" for me, following these rules the whole time:
- Save tokens: run only the commands below and read only their short output. Never open, print or paste snapshot.json, index.html or explorer.html: upload them by file path. Do not write your own scripts or build the page yourself; it is already made.
- Privacy: keep the page private and never create a public link. Never ask me for a password or token. Clone only the repositories I choose.

In the steps, C means: python3 ~/workspace/muse-repo-explorer/tools/repo_explorer.py

1. Get the tool. If ~/workspace/muse-repo-explorer exists, run `git -C ~/workspace/muse-repo-explorer pull --ff-only`; otherwise run `git clone https://github.com/masato-umeno/muse-repo-explorer ~/workspace/muse-repo-explorer`. Then run `C setup`.
2. Sign in (skip if setup printed "signed in"). Run `C login` and show me the URL and code exactly as printed. Then run `C login --wait`; it finishes when I approve.
3. Choose repositories. Run `C list` and show me the result. Ask me which ones to include (I may answer like "all private ones"). Run `C clone owner/repo ...` with my choice.
4. Build. Run `C refresh`.
5. Create the page. Make a private Muse space named "Repository Explorer" by uploading, unchanged, the files that refresh printed: preferably the two files index.html and snapshot.json; if a space can hold only one HTML file, upload explorer.html instead. Then run `C mark-synced --mode two-file` (or `--mode single-file`).
6. Report to me in at most 3 lines: the GitHub account, the number of repositories, and the page.

Remember this for later: when I say "refresh the explorer", or at the end of a recurring job I already have, run `C refresh`. If it prints UP_TO_DATE, stop there. If it prints PAGE_UPDATE_NEEDED, replace only the file(s) it names in the page, then run `C mark-synced`.
````

Pasting it again later is safe: every step skips work that is already done.

## Before you start: three rules

1. **The snapshot is your full source code.** Keep `snapshot.json` out of git and out of anything shared.
2. **Keep the explorer page private.** A public link lets anyone with the link read your code.
3. **Sign in with the device flow only.** Never paste a GitHub password or token into a chat.

Details: [docs/security.md](docs/security.md)

## Documentation

| Document | What it covers |
| --- | --- |
| [How it works](docs/design.md) | Architecture, design decisions, how tokens are saved |
| [Security & privacy](docs/security.md) | Rules for users, and the safety checks for this public repository |
| [Manual setup](docs/manual-setup.md) | Setting it up yourself (or with Claude Code), command reference |
| [Operations](docs/operations.md) | Refreshing, hooks, excluding files, uninstalling |
| [Explorer page spec](docs/explorer-page-spec.md) | Snapshot format and the bundled page |

## Contributing

This repository is **public**. Before your first commit, run:

```sh
sh scripts/install-dev-hooks.sh
```

It blocks snapshots, logs, tokens, private e-mail addresses and the real names you list in
your private denylist. CI runs the same check on every push. See [docs/security.md](docs/security.md#for-contributors).

## License

MIT. See [LICENSE](LICENSE).
