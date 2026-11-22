# Setup instructions for Muse

These instructions are for Muse (the AI agent). People should read [README.md](README.md).

## Rules (apply throughout)

- **Language:** talk to the user in the language they normally use with you, even though the
  setup request is in English. Keep messages short.
- **Tokens:** run only the commands named here or printed by `next`, and read only their output.
  Never open, print or paste `snapshot.json` or files under `dist/`; upload them by path.
  Do not write scripts and do not build the page yourself; it is already made.
- **Privacy:** keep the space private and never create a public link. Never ask the user for a
  password or token. Clone only repositories the user chooses.

## Steps

1. Get the tool. If `~/workspace/muse-repo-explorer` exists, run
   `git -C ~/workspace/muse-repo-explorer pull --ff-only`. Otherwise run
   `git clone https://github.com/masato-umeno/muse-repo-explorer ~/workspace/muse-repo-explorer`.
2. Run `python3 ~/workspace/muse-repo-explorer/tools/repo_explorer.py next`.
3. Do exactly what the line starting with `NEXT` says, then run `next` again.
   Repeat until the output starts with `DONE`, then follow the `DONE` instructions.
   If the output starts with `STOP`, report it to the user and stop.

`next` decides every step from the current state (installation, sign-in, repository selection,
creating or updating the space), so the same instructions serve the first setup, later refreshes
and updates to a new version of the tool. When an existing space must change because the tool was
updated, `next` lists exactly which files to upload or delete; update the existing space and do
not create a new one.
