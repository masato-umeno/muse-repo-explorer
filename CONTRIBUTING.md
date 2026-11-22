# Contributing

This repository is public. It must contain only scripts, documentation and the page template.
Do not commit real repository names, organization names, personal names, e-mail addresses or
snapshots. Use placeholders such as `your-org/your-repo` in examples.

## Development setup

Install the pre-commit hook before your first commit:

```sh
sh scripts/install-dev-hooks.sh
```

Then list, one per line, the real names that must never appear in this repository (for example
your organizations, private repository names and colleagues' names) in:

```
~/.config/muse-repo-explorer/denylist.txt
```

This file is stored outside the repository so that the list itself is never published.

## Safety checks

`scripts/check_public_safety.py` runs in three places:

| Layer | Scope | Trigger |
| --- | --- | --- |
| `.gitignore` | Snapshots, logs, state files, keys, `.env` | Always |
| Pre-commit hook | Staged files | Every local commit |
| GitHub Actions | All tracked files | Every push and pull request |

The check rejects:

- Forbidden files: `snapshot*.json`, `*.log`, state files, `exclude.txt`, keys and `.env` files
- JSON content shaped like a snapshot, regardless of file name
- Credentials: GitHub, AWS, Slack, Anthropic, OpenAI and Google keys, and private keys
- E-mail addresses other than `@users.noreply.github.com` and `@example.*`
- Files larger than 200 KB
- Any word in your private denylist (checked locally only)

If the check fails, correct the content. Do not bypass it with `git commit --no-verify`.

Also recommended:

- Enable **Secret scanning** and **Push protection** under Settings → Code security.
- Commit with your GitHub noreply address and enable "Block command line pushes that expose
  my email" in your GitHub e-mail settings.

## Tests

```sh
sh tests/e2e.sh
```

The end-to-end test runs offline against temporary repositories. It covers the requirement for
at least one repository, the refresh and sync cycle with per-repository uploads and deletions,
the git hooks, the built-in page language, the exclusion of symbolic link targets and excluded
files, escaping in the single-file page, and the refusal to write into an unignored working tree.
CI runs it on every push together with a syntax check of all scripts.

To include Mermaid embedding, point the test to a local copy of the pinned build:

```sh
REPO_EXPLORER_MERMAID_FILE=/path/to/mermaid.min.js sh tests/e2e.sh
```

## If sensitive data is pushed

Removing the data in a new commit is not sufficient: it remains in the history and may already
have been cloned.

1. Revoke or rotate any exposed credential immediately.
2. Remove the data from the history with `git filter-repo` and force-push. Contact GitHub
   Support to purge cached views if necessary.
3. Treat any exposed source code as public.
