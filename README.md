# muse-repo-explorer

**English** | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [한국어](README.ko.md)

Keep local clones of your GitHub repositories inside Muse (your personal AI agent), so that:

- **Muse reads code from local files** — faster and far fewer tokens than going through a connector.
- **You read code from your phone** — in a private "file explorer" page (a Muse space) with a snapshot of the code embedded.

## Get started: paste this into Muse

Copy the whole block below and send it to Muse. Muse will only stop to ask you two things:
(1) the one-time code for GitHub sign-in, and (2) which repositories to clone.

````text
Please set up "muse-repo-explorer" (https://github.com/masato-umeno/muse-repo-explorer) in my environment. Follow the privacy rules at the end strictly.

1. Install tools (under my home directory, so they survive VM replacement)
   - Download the latest ghq release binary (github.com/x-motemen/ghq) to ~/.local/bin/ghq.
   - Download the latest gh (GitHub CLI) release binary (github.com/cli/cli) to ~/.local/bin/gh.
   - Check both with --version.

2. GitHub sign-in (device flow, HTTPS only)
   - Run `gh auth login --hostname github.com --git-protocol https --web`.
   - Show me the one-time code and https://github.com/login/device, then wait until I approve it in my browser.
   - Then report the account name from `gh auth status` and run `gh auth setup-git`.
   - Do not use SSH. Never ask me to paste a password or token.

3. Clone my repositories
   - List the repositories I can access (`gh repo list`, including my organizations), ask me which ones to clone, then run `ghq get <owner>/<repo>` for each.
   - Skip archived repositories unless I ask for them.

4. Install the snapshot tools
   - Run `ghq get https://github.com/masato-umeno/muse-repo-explorer`.
   - Copy everything in its tools/ directory to ~/workspace/repo-explorer/ (NOT inside any git repository) and make the scripts executable.
   - Run `python3 ~/workspace/repo-explorer/update_snapshot.py` and confirm snapshot.json is created.
   - Ask me whether any files should be hidden from the page (for example `.env*`, `*.pem`, `secrets/*`). If so, write those globs to ~/workspace/repo-explorer/exclude.txt and run update_snapshot.py again.

5. Install the pull hooks
   - Run `~/workspace/repo-explorer/install-hooks.sh`.
   - Pull one repository, then confirm snapshot.json was regenerated.

6. Create the explorer page (a Muse space)
   - Build it as specified in docs/explorer-page-spec.md of that repository. Keep snapshot.json as a single separate asset so the page can be refreshed by replacing it.
   - Use my language for the page UI.
   - Keep the page private. Never create a public link.

7. Refreshing
   - When I say "refresh the explorer": run update_snapshot.py, then sync_status.py. Only if sync_status.py exits with code 10, replace the page's snapshot asset and then run `sync_status.py --mark`.
   - Optional: if I already have a recurring job (such as a weekly check), you may append this refresh step to it without reporting in chat.

8. Report
   - The output of `ghq list`, the snapshot size, the page you created, and anything that failed with the reason.

Privacy rules:
- Never put snapshot.json under git, in a public repository, or on a file-sharing service.
- Never share the explorer page publicly.
- Never write credentials (passwords, tokens) to chat, files or logs.
- Only clone repositories I am legitimately allowed to access.
````

## Before you start — three rules

1. **The snapshot is your full source code.** Keep `snapshot.json` out of git and out of anything shared.
2. **Keep the explorer page private.** A public link lets anyone with the link read your code.
3. **Sign in with the device flow only.** Never paste a GitHub password or token into a chat.

Details: [docs/security.md](docs/security.md)

## Documentation

| Document | What it covers |
| --- | --- |
| [How it works](docs/design.md) | Architecture and design decisions |
| [Security & privacy](docs/security.md) | Rules for users, and the safety checks for this public repository |
| [Manual setup](docs/manual-setup.md) | Setting it up yourself (or with Claude Code) without the prompt |
| [Operations](docs/operations.md) | Refreshing, hooks, excluding files, uninstalling |
| [Explorer page spec](docs/explorer-page-spec.md) | Snapshot format and UI requirements for the page |

## Contributing

This repository is **public**. Before your first commit, run:

```sh
sh scripts/install-dev-hooks.sh
```

It blocks snapshots, logs, tokens, private e-mail addresses and the real names you list in
your private denylist. CI runs the same check on every push. See [docs/security.md](docs/security.md#for-contributors).

## License

MIT — see [LICENSE](LICENSE).
