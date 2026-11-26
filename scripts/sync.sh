#!/usr/bin/env bash
# Mirror a package folder into its standalone repo with git subtree split.
# Usage: scripts/sync.sh <inkdrop|vscode|zed|nvim> [path-to-standalone-repo]
# The default target is ../hadal-<name> (../hadal.nvim for nvim, from the neovim/ folder).
# The target must be on a feature branch. Never pushes or updates its protected main branch.
set -euo pipefail

die() {
  printf '%s\n' "$*" >&2
  exit 1
}

git_common_dir() {
  repository="$1"
  common_dir="$(git -C "$repository" rev-parse --git-common-dir)"
  case "$common_dir" in
    /*) cd "$common_dir" ;;
    *) cd "$repository/$common_dir" ;;
  esac
  pwd -P
}

if [ "$#" -gt 2 ]; then
  echo "usage: $0 <inkdrop|vscode|zed|nvim> [path-to-standalone-repo]" >&2
  exit 2
fi

name="${1:-}"
case "$name" in
  inkdrop|vscode|zed)
    prefix="$name"
    repo="hadal-$name"
    mirror_repo="tcagriz/$repo"
    ;;
  nvim)
    prefix="neovim"
    repo="hadal.nvim"
    mirror_repo="tcagriz/hadal.nvim"
    ;;
  *)
    echo "usage: $0 <inkdrop|vscode|zed|nvim> [path-to-standalone-repo]" >&2
    exit 2
    ;;
esac

root="$(cd "$(dirname "$0")/.." && pwd)"
target="${2:-$root/../$repo}"

[ -d "$target" ] || die "not a directory: $target"
if [ "$(git -C "$target" rev-parse --is-inside-work-tree 2>/dev/null || true)" != "true" ]; then
  die "not a git worktree: $target"
fi
[ "$(git_common_dir "$root")" != "$(git_common_dir "$target")" ] ||
  die "target mirror cannot be the source monorepo"

target_branch="$(git -C "$target" symbolic-ref --quiet --short HEAD 2>/dev/null || true)"
[ -n "$target_branch" ] || die "target mirror has a detached HEAD; switch to a feature branch"
if [ "$target_branch" = "main" ]; then
  die "refusing to sync while target mirror is on main; create a feature branch first"
fi

if git -C "$target" show-ref --verify --quiet refs/remotes/origin/HEAD; then
  default_ref="$(git -C "$target" symbolic-ref --quiet --short refs/remotes/origin/HEAD)"
  default_branch="${default_ref#origin/}"
  [ "$target_branch" != "$default_branch" ] ||
    die "refusing to sync while target mirror is on its default branch: $target_branch"
fi

target_status="$(git -C "$target" status --porcelain --untracked-files=all)"
[ -z "$target_status" ] || die "target mirror worktree is not clean: commit or remove its changes"

cd "$root"
source_status="$(git status --porcelain --untracked-files=all)"
[ -z "$source_status" ] ||
  die "source monorepo worktree is not clean: commit or remove all changes before syncing"

python3 scripts/build.py --check
source_status="$(git status --porcelain --untracked-files=all)"
[ -z "$source_status" ] || die "source monorepo worktree changed during generated-file validation"

source_commit="$(git rev-parse --verify 'HEAD^{commit}')"
source_short="$(git rev-parse --short=12 "$source_commit")"
target_head="$(git -C "$target" rev-parse --verify 'HEAD^{commit}')"

if git -C "$target" show-ref --verify --quiet refs/heads/main; then
  protected_ref="refs/heads/main"
elif git -C "$target" show-ref --verify --quiet refs/remotes/origin/main; then
  protected_ref="refs/remotes/origin/main"
else
  die "target mirror has no local or origin/main ref; fetch main before syncing"
fi

protected_head="$(git -C "$target" rev-parse "$protected_ref^{commit}")"
if ! git -C "$target" merge-base --is-ancestor "$protected_head" "$target_head"; then
  die "target feature branch is not based on $protected_ref; rebase it onto main before syncing"
fi

split_output=""
if ! split_output="$(git subtree split --quiet --prefix="$prefix" "$source_commit" 2>&1)"; then
  printf '%s\n' "$split_output" >&2
  die "failed to create the $prefix subtree split"
fi
split_commit="$split_output"
git rev-parse --verify "$split_commit^{commit}" >/dev/null

target_tree="$(git -C "$target" rev-parse "$target_head^{tree}")"
split_tree="$(git rev-parse "$split_commit^{tree}")"
baseline_commit=""

for candidate in $(git rev-list "$split_commit"); do
  candidate_tree="$(git rev-parse "$candidate^{tree}")"
  if [ "$candidate_tree" = "$target_tree" ]; then
    baseline_commit="$candidate"
    break
  fi
done

[ -n "$baseline_commit" ] ||
  die "target mirror does not match any commit in the $prefix subtree history; reconcile it before syncing"

git merge-base --is-ancestor "$baseline_commit" "$split_commit" ||
  die "subtree history is not a fast-forward of the target mirror state"

if [ "$target_tree" = "$split_tree" ]; then
  sync_commit="$target_head"
  echo "ok      $target already matches $prefix at $source_commit"
else
  git -C "$target" fetch --quiet --no-tags "$root" "$split_commit"

  author_name="$(git show -s --format=%an "$source_commit")"
  author_email="$(git show -s --format=%ae "$source_commit")"
  author_date="$(git show -s --format=%aI "$source_commit")"
  committer_name="$(git show -s --format=%cn "$source_commit")"
  committer_email="$(git show -s --format=%ce "$source_commit")"
  committer_date="$(git show -s --format=%cI "$source_commit")"

  sync_commit="$(
    printf 'Sync %s from hadal-theme %s\n\nSource commit: %s\nSource package: %s/\nSource: https://github.com/tcagriz/hadal-theme/commit/%s\n' \
      "$name" "$source_short" "$source_commit" "$prefix" "$source_commit" |
      GIT_AUTHOR_NAME="$author_name" \
      GIT_AUTHOR_EMAIL="$author_email" \
      GIT_AUTHOR_DATE="$author_date" \
      GIT_COMMITTER_NAME="$committer_name" \
      GIT_COMMITTER_EMAIL="$committer_email" \
      GIT_COMMITTER_DATE="$committer_date" \
        git -C "$target" commit-tree "${split_commit}^{tree}" -p "$target_head"
  )"

  [ "$(git -C "$target" rev-parse "$sync_commit^{tree}")" = "$split_tree" ] ||
    die "generated mirror commit has an unexpected tree"
  [ "$(git -C "$target" rev-parse "$sync_commit^1")" = "$target_head" ] ||
    die "generated mirror commit is not a fast-forward"

  git -C "$target" update-ref "refs/heads/$target_branch" "$sync_commit" "$target_head"
  git -C "$target" reset --hard "$sync_commit" >/dev/null
  echo "synced  $target from $prefix at $source_commit"
fi

[ "$(git -C "$target" rev-parse "$protected_ref")" = "$protected_head" ] ||
  die "protected main branch changed unexpectedly during sync"
[ "$(git -C "$target" rev-parse "$target_branch")" = "$sync_commit" ] ||
  die "target feature branch does not point to the generated sync commit"
[ -z "$(git -C "$target" status --porcelain --untracked-files=all)" ] ||
  die "target mirror worktree is not clean after sync"
[ -z "$(git status --porcelain --untracked-files=all)" ] ||
  die "source monorepo worktree changed unexpectedly during sync"

echo "source  $source_commit"
echo "branch  $target_branch"
echo "commit  $sync_commit"
echo "push    git -C $(printf '%q' "$target") push --set-upstream origin $(printf '%q' "$target_branch")"
echo "pr      gh pr create --repo $mirror_repo --base main --head $(printf '%q' "$target_branch")"
echo "not pushed; rerun the push command to update an existing mirror PR"
