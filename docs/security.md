# Security & privacy

This mechanism exists to make **your private source code readable for you alone**.
There are two sides: rules for people who *use* it, and guards for people who *edit this
public repository*.

## For users

1. **Never publish the snapshot.** `snapshot.json` contains the full source of every cloned
   repository. Keep it outside any git repository (the default `~/workspace/repo-explorer`
   is), never upload it to a file-sharing service.
   `update_snapshot.py` refuses to write if its output directory is inside a git work tree
   that does not ignore `snapshot.json`, and writes it (and `dist/`) owner-only (600 / 700).
2. **Never share the explorer page publicly.** A public link lets anyone with the link read
   your code. Keep the space private.
3. **Never put credentials in chat or files.** Sign in only with the device flow
   (`gh auth login --web`). Credentials then live only in `~/.config/gh/`.
4. **Understand the gh token scope.** The default flow grants the `repo` scope (read/write).
   When you stop using this, run `gh auth logout`, or revoke the app on GitHub
   (Settings → Applications → Authorized OAuth Apps).
5. **Clone only what you are allowed to.** For shared/organization repositories, follow that
   project's rules; never expose other people's code without permission.
6. **Let the agent upload files, not read them.** The README prompt tells Muse to upload
   `dist/` files by path and never print them, so your code does not pass through the chat.
7. **Hide sensitive files from the page.** Even private, the page is one share away from
   anyone. List globs such as `.env*`, `*.pem`, `your-org/your-repo/secrets/*` in
   `~/workspace/repo-explorer/exclude.txt`; matching files appear in the tree without content.
   Symlinks and submodules are never followed.

## For contributors

This repository is **public**. Only scripts, instructions and specs belong here — never real
repository names, organization names, personal names, e-mail addresses, or snapshots.
Use placeholders such as `your-org/your-repo`.

### Three layers of protection

| Layer | What | When |
| --- | --- | --- |
| `.gitignore` | Snapshots, logs, sync state, `exclude.txt`, keys, `.env` | Always |
| pre-commit hook | `scripts/check_public_safety.py --staged` | Every local commit |
| GitHub Actions | `.github/workflows/public-safety.yml` (all tracked files) | Every push / PR |

The check blocks:

- forbidden files (`snapshot*.json`, `*.log`, `.page-synced-heads`, `exclude.txt`, keys, `.env`, …)
- snapshot-shaped JSON under any name
- tokens and keys (GitHub, AWS, Slack, Anthropic, OpenAI, Google, private keys)
- e-mail addresses other than `@users.noreply.github.com` and `@example.*`
- files over 200 KB
- any word in your **private denylist**

### Setup (once per machine)

```sh
sh scripts/install-dev-hooks.sh
```

Then put the real names that must never appear here — your organizations, private repository
names, colleagues' names — one per line in:

```
~/.config/muse-repo-explorer/denylist.txt
```

That file lives outside the repository on purpose, so the list itself is never published.
(CI cannot see it; it protects you locally.)

### Also recommended

- In the GitHub repository settings, enable **Secret scanning** and **Push protection**
  (Settings → Code security). They are free for public repositories.
- Commit with your GitHub noreply address (`<id>+<user>@users.noreply.github.com`) and enable
  "Block command line pushes that expose my email" in your GitHub e-mail settings.
- Never bypass the hook with `git commit --no-verify`. If the check fires, fix the content.

### If something sensitive was pushed

Deleting it in a new commit is **not** enough — it stays in history and may already be cloned.

1. Revoke/rotate any leaked credential immediately.
2. Remove it from history (`git filter-repo`), force-push, and ask GitHub Support to purge
   cached views if needed.
3. Treat leaked source code as public from that moment.
