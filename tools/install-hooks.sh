#!/bin/sh
# ghq配下の全cloneに post-merge フックを入れる。
# pull でリポジトリが進むたびに on-pull.sh が走り、スナップショットが再生成される。
set -eu
GHQ_ROOT_DIR="${GHQ_ROOT:-$(ghq root)}"
# フックは、運用コピー置き場 (REPO_EXPLORER_HOME) の on-pull.sh を指す。
# 事前に tools/ の中身を REPO_EXPLORER_HOME へコピーしておくこと。
ON_PULL="${REPO_EXPLORER_HOME:-$HOME/workspace/repo-explorer}/on-pull.sh"
count=0
for d in "$GHQ_ROOT_DIR"/*/*/*/; do
    [ -d "$d.git" ] || continue
    hook="$d.git/hooks/post-merge"
    printf '#!/bin/sh\nexec "%s"\n' "$ON_PULL" > "$hook"
    chmod +x "$hook"
    count=$((count + 1))
    echo "hook -> $d"
done
echo "installed post-merge hooks: $count"
