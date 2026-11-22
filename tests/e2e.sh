#!/bin/sh
# Offline end-to-end test: fake ghq root with local repositories, no network, no GitHub.
# Usage: sh tests/e2e.sh
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
export GHQ_ROOT="$T/ghq" REPO_EXPLORER_HOME="$T/home"
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@example.com GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@example.com
RX="python3 $ROOT/tools/repo_explorer.py"
fail() { echo "FAIL: $*" >&2; exit 1; }
expect() { echo "$1" | grep -q -- "$2" || { echo "$1" >&2; fail "expected: $2"; }; }

# upstream with tricky content
U="$T/up"; git init -q "$U"
mkdir -p "$U/src" "$U/日本語"
printf 'print("</script><img src=x onerror=alert(1)>")\n' > "$U/src/a.py"
echo hi > "$U/日本語/メモ.md"
printf 'a\0b' > "$U/bin.dat"
echo SECRET > "$U/.env"
echo outside-secret > "$T/outside"; ln -s "$T/outside" "$U/link"
git -C "$U" add -A; git -C "$U" commit -qm init
git clone -q "$U" "$GHQ_ROOT/github.com/your-org/your-repo"
mkdir -p "$REPO_EXPLORER_HOME"; echo '.env' > "$REPO_EXPLORER_HOME/exclude.txt"

out="$($RX refresh)"; expect "$out" "PAGE_UPDATE_NEEDED"; expect "$out" "first time"
S="$REPO_EXPLORER_HOME/snapshot.json"
grep -q outside-secret "$S" && fail "symlink target leaked"
grep -q SECRET "$S" && fail "excluded file leaked"
grep -q '"skipped":"symlink"' "$S" || fail "symlink not marked"
grep -q 'メモ.md' "$S" || fail "non-ASCII path quoted"
grep -q '<img' "$REPO_EXPLORER_HOME/dist/explorer.html" && fail "unescaped < in single-file page"
[ "$(stat -c %a "$S")" = 600 ] || fail "snapshot not mode 600"
[ -f "$GHQ_ROOT/github.com/your-org/your-repo/.git/hooks/post-merge" ] || fail "hook missing"

$RX mark-synced >/dev/null 2>&1 && fail "mark-synced without --mode should fail"
out="$($RX mark-synced --mode two-file)"; expect "$out" "marked 1 repos"
out="$($RX refresh)"; expect "$out" "UP_TO_DATE"

# a pull through the hook rebuilds in the background
echo more >> "$U/src/a.py"; git -C "$U" commit -qam 2
git -C "$GHQ_ROOT/github.com/your-org/your-repo" pull -q
i=0; until [ -f "$REPO_EXPLORER_HOME/.snapshot-dirty" ] || [ $i -ge 20 ]; do sleep 0.5; i=$((i+1)); done
[ -f "$REPO_EXPLORER_HOME/.snapshot-dirty" ] || fail "hook did not rebuild"
out="$($RX refresh --no-pull)"; expect "$out" "replace the page asset snapshot.json"

# refusing to write into an unignored git work tree
git init -q "$T/pub"
REPO_EXPLORER_HOME="$T/pub" python3 "$ROOT/tools/update_snapshot.py" --no-pull 2>/dev/null && fail "wrote into git work tree"

echo "e2e OK"
