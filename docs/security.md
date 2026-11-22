# Security

This document is for users. Guidance for contributors to this public repository is in
[CONTRIBUTING.md](../CONTRIBUTING.md).

## Data handled

| Data | Where it is stored | Sensitivity |
| --- | --- | --- |
| Source code of included repositories | Clones, `snapshot.json`, `dist/`, the Muse space | As sensitive as the repositories themselves |
| Mermaid build | `vendor/` in the state directory | Third-party code that runs in the page |
| GitHub credentials | `~/.config/gh/` (managed by gh) | Grants access to every repository the account can reach |
| Repository names and commit IDs | State files in `~/workspace/repo-explorer` | May reveal private project names |

## Built-in safeguards

- The snapshot is built from committed content only. Symbolic links and submodules are listed
  but never followed, so files outside a repository cannot be included.
- Files matching `exclude.txt` appear in the tree without their content.
- `snapshot.json` and `dist/` are written with owner-only permissions (600 and 700).
- `update_snapshot.py` refuses to write into a git working tree unless `snapshot.json` is
  ignored there, which prevents the snapshot from being committed by mistake.
- The page makes no external requests and sets `noindex` and `no-referrer`. File content is
  escaped before display and is never interpreted as markup. Markdown previews do not render raw
  HTML, and only `http`, `https` and `mailto` links are made clickable.
- Mermaid is downloaded once, at a pinned version, and kept only if its SHA-256 matches the value
  in the CLI. A modified file is rejected. Diagrams are rendered with `securityLevel: 'strict'`.
- The setup instructions tell the agent to upload page files by path and not to read them, so
  source code does not pass through the conversation.

## Recommendations

1. **Keep the explorer page private.** A public link gives anyone who has it access to the
   code. Do not create one.
2. **Do not copy `snapshot.json` elsewhere.** Keep it out of git repositories and file-sharing
   services.
3. **Sign in only through the device flow.** Never paste a password or token into a
   conversation.
4. **Exclude sensitive files.** Add patterns such as `.env*`, `*.pem` or
   `your-org/your-repo/secrets/*` to `exclude.txt`, even though the page is private.
5. **Include only repositories you are authorized to access,** and follow the policies of
   shared or organization repositories.
6. **Pin the setup instructions if you need a fixed version.** The one-line setup makes Muse follow
   `MUSE_SETUP.md` and the output of `next` from this repository. Replace `main` in the URL with
   a commit ID or release tag to use a version you have reviewed.
7. **Revoke access when you stop using the tool.** The default gh token has the `repo` scope
   (read and write). Run `gh auth logout`, or revoke the authorization under GitHub
   Settings → Applications → Authorized OAuth Apps.
