# muse-repo-viewer

**English** | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [한국어](README.ko.md)

A repository viewer that runs in Muse. It keeps local clones of your GitHub repositories in the
Muse environment, so that:

- **you** can read and search the code on your phone in a private Muse space, and ask Muse about
  the lines you select;
- **Muse** reads source code from local files, which is faster than a connector and uses fewer
  tokens.

Overview: <https://masato-umeno.github.io/muse-repo-viewer/>

## Setup

Copy this line and paste it into Muse. Muse keeps replying in the language you normally use.

```text
Set up muse-repo-viewer for me by following https://github.com/masato-umeno/muse-repo-viewer/blob/main/MUSE_SETUP.md (keep replying in the language we normally use)
```

During setup you approve the GitHub sign-in and choose the repositories to include (this
repository works as a sample). If Muse pauses to ask whether to continue, for example before
creating the space, reply that it may go ahead. To update later, send the same line again.

## Usage

- **Refresh:** ask Muse to "refresh the viewer". Only repositories with new commits are uploaded.
- **Add repositories:** ask Muse to clone them, then refresh.
- **Hide files:** list glob patterns such as `.env*` in `~/workspace/repo-viewer/exclude.txt`.
- **Language:** change it in the page settings (gear button).

## Security

The space contains the full source code of the included repositories, so keep it private. The
setup line makes Muse follow instructions stored in this repository; to pin a version, replace
`main` in the URL with a commit ID or tag. See [Security](docs/security.md).

## Documentation

| Document | Contents |
| --- | --- |
| [Architecture](docs/architecture.md) | Components, data flow, design decisions, token efficiency |
| [Security](docs/security.md) | Data handled, safeguards, and recommendations for users |
| [Manual setup](docs/manual-setup.md) | Running the setup yourself or with Claude Code |
| [Operations](docs/operations.md) | Refreshing, maintenance, troubleshooting, uninstalling |
| [Reference](docs/reference.md) | Commands, configuration, state files, snapshot format |
| [Viewer page](docs/page.md) | Delivery forms and behavior of the bundled page |

## Contributing

This repository is public. Read [CONTRIBUTING.md](CONTRIBUTING.md) before your first commit.

## License

[MIT](LICENSE)
