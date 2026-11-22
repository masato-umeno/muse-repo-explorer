#!/bin/sh
# Offline end-to-end test: fake ghq root with local repositories, no network, no GitHub.
# Usage: sh tests/e2e.sh
# Set REPO_EXPLORER_MERMAID_FILE to a local mermaid.min.js to also test diagram embedding.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
export GHQ_ROOT="$T/ghq" REPO_EXPLORER_HOME="$T/home" HOME="$T/userhome"
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@example.com GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@example.com
mkdir -p "$HOME"
RX="python3 $ROOT/tools/repo_explorer.py"
fail() { echo "FAIL: $*" >&2; exit 1; }
expect() { echo "$1" | grep -q -- "$2" || { echo "$1" >&2; fail "expected: $2"; }; }
unzip_json() { python3 -c "import gzip,sys; sys.stdout.write(gzip.open(sys.argv[1],'rt').read())" "$1"; }

# ---- `next` walks the agent through setup, one action at a time ----
mkdir -p "$REPO_EXPLORER_HOME"
out="$($RX next)"; expect "$out" "NEXT (1/5 install)"; expect "$out" "setup --lang"
# fake gh / ghq so the remaining states can be reached offline
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/gh" <<'EOS'
#!/bin/sh
[ "$1 $2" = "api user" ] && [ -n "${FAKE_GH_USER:-}" ] && { echo "$FAKE_GH_USER"; exit 0; }
exit 1
EOS
printf '#!/bin/sh\necho "$GHQ_ROOT"\n' > "$HOME/.local/bin/ghq"
chmod +x "$HOME/.local/bin/gh" "$HOME/.local/bin/ghq"
printf 'en' > "$REPO_EXPLORER_HOME/.page-lang"
out="$($RX next)"; expect "$out" "NEXT (2/5 sign in)"; expect "$out" "masato-umeno/muse-repo-explorer"
export FAKE_GH_USER=tester
out="$($RX next)"; expect "$out" "NEXT (3/5 repositories)"

# no repositories yet -> refresh must stop and point to the sample
set +e; out="$($RX refresh)"; rc=$?; set -e
[ $rc -eq 3 ] || fail "refresh without repositories should exit 3"
expect "$out" "NO_REPOSITORIES"; expect "$out" "masato-umeno/muse-repo-explorer"

# page language is stored for the build
printf 'ja' > "$REPO_EXPLORER_HOME/.page-lang"

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
git clone -q "$U" "$GHQ_ROOT/github.com/your-org/second"
echo '.env' > "$REPO_EXPLORER_HOME/exclude.txt"

out="$($RX next)"; expect "$out" "NEXT (4/5 create the space)"; expect "$out" "dist/site/"
out="$($RX refresh)"; expect "$out" "PAGE_UPDATE_NEEDED"; expect "$out" "create a private space"
S="$REPO_EXPLORER_HOME/snapshot.json"; SITE="$REPO_EXPLORER_HOME/dist/site"
grep -q outside-secret "$S" && fail "symlink target leaked"
grep -q SECRET "$S" && fail "excluded file leaked"
grep -q '"skipped":"symlink"' "$S" || fail "symlink not marked"
grep -q 'メモ.md' "$S" || fail "non-ASCII path quoted"
[ "$(stat -c %a "$S")" = 600 ] || fail "snapshot not mode 600"
[ -f "$GHQ_ROOT/github.com/your-org/your-repo/.git/hooks/post-merge" ] || fail "hook missing"

# folder form: small index without content, one content file per repository
[ -f "$SITE/index.html" ] && [ -f "$SITE/data/index.json.gz" ] || fail "folder form incomplete"
[ "$(ls "$SITE"/data/*--*.json.gz | wc -l)" -eq 2 ] || fail "expected one content file per repository"
unzip_json "$SITE/data/index.json.gz" | grep -q 'onerror' && fail "index contains file content"
grep -q 'data-lang="ja"' "$SITE/index.html" || fail "language not built into the page"
grep -q '<img src=x' "$REPO_EXPLORER_HOME/dist/explorer.html" && fail "unescaped content in single-file page"
if [ -n "${REPO_EXPLORER_MERMAID_FILE:-}" ]; then
  $RX setup >/dev/null 2>&1 || true
  $RX refresh --no-pull >/dev/null
  [ -f "$SITE/data/mermaid.js.gz" ] || fail "mermaid not embedded"
fi

$RX mark-synced >/dev/null 2>&1 && fail "mark-synced without --mode should fail"
out="$($RX mark-synced --mode folder)"; expect "$out" "marked as synced"
out="$($RX refresh)"; expect "$out" "UP_TO_DATE"
out="$($RX next)"; expect "$out" "DONE"; expect "$out" "2 repositories"; expect "$out" "tester"

# a pull through the hook rebuilds in the background; only that repository's file changes
echo more >> "$U/src/a.py"; git -C "$U" commit -qam 2
git -C "$GHQ_ROOT/github.com/your-org/your-repo" pull -q
i=0; until [ -f "$REPO_EXPLORER_HOME/.snapshot-dirty" ] || [ $i -ge 20 ]; do sleep 0.5; i=$((i+1)); done
[ -f "$REPO_EXPLORER_HOME/.snapshot-dirty" ] || fail "hook did not rebuild"
sleep 1
out="$($RX refresh --no-pull)"
expect "$out" "data/index.json.gz"
expect "$out" "your-org--your-repo-"
echo "$out" | grep -q "your-org--second-" && fail "unchanged repository listed for upload"
out="$($RX next)"; expect "$out" "NEXT (5/5 update the space)"

# removing a repository lists its file for deletion
$RX mark-synced >/dev/null
rm -rf "$GHQ_ROOT/github.com/your-org/second"
out="$($RX refresh --no-pull)"; expect "$out" "delete from the space"; expect "$out" "your-org--second-"

# refusing to write into an unignored git work tree
git init -q "$T/pub"
REPO_EXPLORER_HOME="$T/pub" python3 "$ROOT/tools/update_snapshot.py" --no-pull 2>/dev/null && fail "wrote into git work tree"

echo "e2e OK"
