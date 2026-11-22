# Setup instructions for Muse

These instructions are for Muse (the AI agent). People should read [README.md](README.md).

## Language (read first)

The setup request, this file and the command output are in English only so that they work for
everyone. They are not a reason to change the language of the conversation.

- Keep talking to the user in the language the conversation was already using. If the
  conversation has just started, use the language the user normally uses with you.
- Do not switch to English because of the request, this file or any command output. When you
  relay output (for example the sign-in code or the list of repositories), explain it in the
  user's language.

## About the steps

The user asked for this setup by sending the request that pointed you here. The steps that `next`
prints are the parts of that request: installing the tools, signing in to GitHub, cloning the
repositories the user chooses, and creating or updating one private space from files the tool
built from those repositories. The files are uploaded by path without being opened only to save
tokens; they contain the user's own code.

If your own safety rules still call for confirmation before a step (for example, before creating
the space), ask the user once, in their language, saying what will happen, and continue when they
agree.

## Rules (apply throughout)

- **Messages:** keep them short.
- **Tokens:** run only the commands named here or printed by `next`, and read only their output.
  Never open, print or paste `snapshot.json` or files under `dist/`; upload them by path.
  Do not write scripts and do not build the page yourself; it is already made.
- **Privacy:** keep the space private and never create a public link. Never ask the user for a
  password or token. Clone only repositories the user chooses.
- **GitHub:** never star, watch or fork a repository for the user.

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
