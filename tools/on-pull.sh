#!/bin/sh
# Called from the post-merge / post-rewrite hooks of each clone.
# Regenerates the snapshot after a pull; if any HEAD changed, update_snapshot.py
# creates .snapshot-dirty ("page not yet updated").
# It never pulls (--no-pull), so it cannot recurse. Script-only: no tokens used.
#
# Usage: on-pull.sh <hook-name> [arguments git passed to the hook...]

# When update_snapshot.py itself is pulling, do nothing: it regenerates once at the end.
[ -n "${REPO_EXPLORER_NO_HOOK:-}" ] && exit 0

# post-rewrite runs for both rebase and amend; only react to rebase (= pull --rebase).
case "${1:-}" in
    post-rewrite) [ "${2:-}" = "rebase" ] || exit 0 ;;
esac

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOME_DIR="${REPO_EXPLORER_HOME:-$HOME/workspace/repo-explorer}"
cd "$HOME_DIR" 2>/dev/null || exit 0

# Inside a hook, GIT_DIR etc. point at the repository being pulled.
# Clear them before reading other repositories.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_PREFIX GIT_OBJECT_DIRECTORY \
      GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_COMMON_DIR

# Run in the background so the pull is not slowed down; never fail the pull.
nohup python3 "$SCRIPT_DIR/update_snapshot.py" --no-pull --quiet \
    >> snapshot-hook.log 2>&1 &
exit 0
