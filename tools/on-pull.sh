#!/bin/sh
# git pull (post-merge フック) に引っ掛けてスナップショットを再生成し、
# 「ページ未反映の変化あり」フラグ (.snapshot-dirty) を立てる。
# pull 自体は行わない (--no-pull) ので再帰しない。スクリプト処理のみで完結する。
HOME_DIR="${REPO_EXPLORER_HOME:-$HOME/workspace/repo-explorer}"
cd "$HOME_DIR" || exit 0
python3 "$(dirname "$0")/update_snapshot.py" --no-pull >> snapshot-hook.log 2>&1
touch .snapshot-dirty
