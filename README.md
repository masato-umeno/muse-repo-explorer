# muse-repo-explorer

**English** | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [한국어](README.ko.md)

muse-repo-explorer keeps local clones of your GitHub repositories in the Muse environment and
serves them in two ways:

- **To Muse:** source code is read from local files, which is faster than a connector and
  uses considerably fewer tokens.
- **To you:** a private, mobile-first code browser (a Muse space) built from a snapshot of the
  clones. The page supports English, Japanese, Chinese and Korean, in light and dark themes.

## Setup

Send the following prompt to Muse. During setup you will be asked to approve the GitHub
sign-in and to choose the repositories to include. The prompt can be sent again at any time;
completed steps are skipped.

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

## Usage

- **Updating the page:** ask Muse to "refresh the explorer". The page is changed only when a
  repository has new commits, and only the data file is replaced.
- **Adding repositories:** ask Muse to clone them, then refresh.
- **Hiding files:** list glob patterns (for example `.env*` or `*.pem`) in
  `~/workspace/repo-explorer/exclude.txt`. See [Operations](docs/operations.md).

## Security

The snapshot contains the full source code of every included repository. Keep the explorer
page private, never commit or share `snapshot.json`, and sign in only through the device flow.
See [Security](docs/security.md) for the complete guidance.

## Documentation

| Document | Contents |
| --- | --- |
| [Architecture](docs/architecture.md) | Components, data flow, design decisions, token efficiency |
| [Security](docs/security.md) | Data handled, safeguards, and recommendations for users |
| [Manual setup](docs/manual-setup.md) | Running the setup yourself or with Claude Code |
| [Operations](docs/operations.md) | Refreshing, maintenance, troubleshooting, uninstalling |
| [Reference](docs/reference.md) | Commands, configuration, state files, snapshot format |
| [Explorer page](docs/page.md) | Delivery forms and behavior of the bundled page |

## Contributing

This repository is public. Read [CONTRIBUTING.md](CONTRIBUTING.md) before your first commit.

## License

[MIT](LICENSE)
