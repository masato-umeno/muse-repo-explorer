# muse-repo-explorer

**English** | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [한국어](README.ko.md)

muse-repo-explorer keeps local clones of your GitHub repositories in the Muse environment and
serves them in two ways:

- **To Muse:** source code is read from local files, which is faster than a connector and
  uses considerably fewer tokens.
- **To you:** a private, mobile-first code browser (a Muse space) built from a snapshot of the
  clones. File names and file contents can be searched, a selected range of code can be sent to
  Muse with a question, Markdown files are shown as formatted documents, and Mermaid diagrams are
  rendered.
  The page is shown in your language (English, Japanese, Chinese or Korean) and stays fast as
  the number of repositories grows, because each repository's content is loaded only when needed.

## Setup

Send this line to Muse:

```text
Set up muse-repo-explorer for me by following https://github.com/masato-umeno/muse-repo-explorer/blob/main/MUSE_SETUP.md
```

Muse reads [MUSE_SETUP.md](MUSE_SETUP.md) and is then guided step by step by the tool itself.
You will be asked to approve the GitHub sign-in and to choose the repositories to include. At
least one repository is required; this repository can be used as a sample. The page is built in
the language you normally use with Muse, and it can be changed in the page's settings (the gear
button). Sending the same line again later is safe: completed steps are skipped, and an existing
installation, including one made with an earlier version, is updated to the latest version.

The line makes Muse follow instructions stored in this repository. To use a fixed version, replace
`main` in the URL with a commit ID or release tag.

## Usage

- **Updating the page:** ask Muse to "refresh the explorer", or send the setup line again. The space is changed only when a
  repository has new commits, and only the files of those repositories are uploaded.
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
