#!/usr/bin/env bash
# Mirror a package folder into its standalone repo with git subtree split.
# Usage: scripts/sync.sh <inkdrop|vscode|zed|nvim> [path-to-standalone-repo]
# The default target is ../hadal-<name> (../hadal.nvim for nvim, from the neovim/ folder).
# Never pushes; it only updates the local repo.
set -euo pipefail

name="${1:-}"
case "$name" in
  inkdrop|vscode|zed) prefix="$name"; repo="hadal-$name" ;;
  nvim) prefix="neovim"; repo="hadal.nvim" ;;
  *) echo "usage: $0 <inkdrop|vscode|zed|nvim> [path-to-standalone-repo]" >&2; exit 2 ;;
esac

root="$(cd "$(dirname "$0")/.." && pwd)"
target="${2:-$root/../$repo}"
branch="$name-split"

[ -d "$target/.git" ] || { echo "not a git repo: $target" >&2; exit 1; }

cd "$root"
python3 scripts/build.py --check
if [ -n "$(git status --porcelain -- "$prefix")" ]; then
  echo "commit your $prefix/ changes first" >&2
  exit 1
fi

git subtree split --prefix="$prefix" -b "$branch" >/dev/null 2>&1
git -C "$target" pull --ff-only "$root" "$branch"
echo "synced $target (not pushed)"
