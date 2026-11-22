#!/bin/sh
# For people who edit THIS repository: run the public-safety check before every commit.
# Usage: sh scripts/install-dev-hooks.sh
set -eu
root="$(git rev-parse --show-toplevel)"
hooks="$(git -C "$root" rev-parse --git-path hooks)"
case "$hooks" in /*) ;; *) hooks="$root/$hooks" ;; esac
mkdir -p "$hooks"
cat > "$hooks/pre-commit" <<'EOF'
#!/bin/sh
exec python3 "$(git rev-parse --show-toplevel)/scripts/check_public_safety.py" --staged
EOF
chmod +x "$hooks/pre-commit"
mkdir -p "$HOME/.config/muse-repo-explorer"
touch "$HOME/.config/muse-repo-explorer/denylist.txt"
echo "pre-commit hook installed."
echo "Add real org / repo / person names that must never be published to:"
echo "  $HOME/.config/muse-repo-explorer/denylist.txt"
