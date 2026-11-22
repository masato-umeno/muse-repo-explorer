#!/bin/sh
# Install post-merge / post-rewrite hooks into every clone under ghq.
# Each time a pull moves a repository forward, on-pull.sh regenerates the snapshot.
#
# - Existing hooks that were not written by this script are backed up to
#   <hook>.bak-repo-explorer before being replaced (never silently overwritten).
# - Re-running is safe (idempotent).
#
# Copy the contents of tools/ to REPO_EXPLORER_HOME first.
set -eu

MARKER="# installed-by: muse-repo-explorer"
GHQ_ROOT_DIR="${GHQ_ROOT:-$(ghq root 2>/dev/null || echo "$HOME/ghq")}"
ON_PULL="${REPO_EXPLORER_HOME:-$HOME/workspace/repo-explorer}/on-pull.sh"

if [ ! -x "$ON_PULL" ]; then
    echo "error: $ON_PULL not found or not executable (copy tools/ there first)" >&2
    exit 1
fi

count=0
for d in "$GHQ_ROOT_DIR"/*/*/*/; do
    [ -e "$d.git" ] || continue
    hooks_dir="$(git -C "$d" rev-parse --git-path hooks)"
    case "$hooks_dir" in /*) ;; *) hooks_dir="$d$hooks_dir" ;; esac
    mkdir -p "$hooks_dir"
    for name in post-merge post-rewrite; do
        hook="$hooks_dir/$name"
        if [ -f "$hook" ] && ! grep -q "$MARKER" "$hook"; then
            cp "$hook" "$hook.bak-repo-explorer"
            echo "backed up existing hook: $hook"
        fi
        printf '#!/bin/sh\n%s\nexec "%s" %s "$@"\n' "$MARKER" "$ON_PULL" "$name" > "$hook"
        chmod +x "$hook"
    done
    count=$((count + 1))
    echo "hooks -> $d"
done
echo "installed hooks in $count repositories"
