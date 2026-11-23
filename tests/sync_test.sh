#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SYNC="$ROOT/scripts/sync.sh"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/hadal-sync-test.XXXXXX")"
trap 'rm -rf -- "$TMP"' EXIT

fail() {
  echo "not ok: $*" >&2
  exit 1
}

assert_eq() {
  [ "$1" = "$2" ] || fail "expected '$2', got '$1'"
}

assert_contains() {
  grep -Fq "$2" "$1" || {
    cat "$1" >&2
    fail "expected output to contain: $2"
  }
}

commit_all() {
  git -C "$1" add -A
  git -C "$1" commit -qm "$2"
}

make_fixture() {
  FIXTURE="$TMP/$1"
  SOURCE="$FIXTURE/source"
  TARGET="$FIXTURE/target"
  PACKAGE="${2:-vscode}"
  case "$PACKAGE" in
    inkdrop|vscode|zed) PREFIX="$PACKAGE"; MIRROR_REPO="tcagriz/hadal-$PACKAGE" ;;
    nvim) PREFIX="neovim"; MIRROR_REPO="tcagriz/hadal.nvim" ;;
    *) fail "unknown fixture package: $PACKAGE" ;;
  esac
  mkdir -p "$SOURCE/scripts" "$SOURCE/$PREFIX" "$TARGET"

  cp "$SYNC" "$SOURCE/scripts/sync.sh"
  chmod +x "$SOURCE/scripts/sync.sh"
  cat > "$SOURCE/scripts/build.py" <<'EOF'
#!/usr/bin/env python3
raise SystemExit(0)
EOF
  chmod +x "$SOURCE/scripts/build.py"
  printf 'theme-v1\n' > "$SOURCE/$PREFIX/theme.txt"

  git init -q "$SOURCE"
  git -C "$SOURCE" symbolic-ref HEAD refs/heads/main
  git -C "$SOURCE" config user.name "Hadal Test"
  git -C "$SOURCE" config user.email "hadal-test@example.invalid"
  commit_all "$SOURCE" "Initial source"

  cp -R "$SOURCE/$PREFIX/." "$TARGET/"
  git init -q "$TARGET"
  git -C "$TARGET" symbolic-ref HEAD refs/heads/main
  git -C "$TARGET" config user.name "Hadal Test"
  git -C "$TARGET" config user.email "hadal-test@example.invalid"
  commit_all "$TARGET" "Initial mirror"
}

expect_failure() {
  expected="$1"
  shift
  output="$FIXTURE/output.txt"
  if "$@" >"$output" 2>&1; then
    cat "$output" >&2
    fail "command unexpectedly succeeded"
  fi
  assert_contains "$output" "$expected"
}

test_refuses_main() {
  make_fixture "refuses-main"
  before="$(git -C "$TARGET" rev-parse HEAD)"

  expect_failure "refusing to sync while target mirror is on main" \
    "$SOURCE/scripts/sync.sh" vscode "$TARGET"

  assert_eq "$(git -C "$TARGET" rev-parse HEAD)" "$before"
  assert_eq "$(git -C "$TARGET" branch --show-current)" "main"
  echo "ok - refuses target main"
}

test_refuses_source_as_target() {
  make_fixture "source-as-target"
  git -C "$SOURCE" switch -q -c sync/source
  before="$(git -C "$SOURCE" rev-parse HEAD)"

  expect_failure "target mirror cannot be the source monorepo" \
    "$SOURCE/scripts/sync.sh" vscode "$SOURCE"

  assert_eq "$(git -C "$SOURCE" rev-parse HEAD)" "$before"
  echo "ok - refuses the source repository as its own target"
}

test_refuses_dirty_source() {
  make_fixture "dirty-source"
  git -C "$TARGET" switch -q -c sync/vscode
  before="$(git -C "$TARGET" rev-parse HEAD)"
  printf 'dirty\n' > "$SOURCE/unrelated.txt"

  expect_failure "source monorepo worktree is not clean" \
    "$SOURCE/scripts/sync.sh" vscode "$TARGET"

  assert_eq "$(git -C "$TARGET" rev-parse HEAD)" "$before"
  echo "ok - refuses dirty source monorepo"
}

test_refuses_dirty_target() {
  make_fixture "dirty-target"
  git -C "$TARGET" switch -q -c sync/vscode
  printf 'dirty\n' > "$TARGET/local.txt"
  before="$(git -C "$TARGET" rev-parse HEAD)"

  expect_failure "target mirror worktree is not clean" \
    "$SOURCE/scripts/sync.sh" vscode "$TARGET"

  assert_eq "$(git -C "$TARGET" rev-parse HEAD)" "$before"
  echo "ok - refuses dirty target mirror"
}

test_refuses_stale_branch() {
  make_fixture "stale-branch"
  git -C "$TARGET" switch -q -c sync/vscode
  branch_head="$(git -C "$TARGET" rev-parse HEAD)"
  git -C "$TARGET" switch -q main
  printf 'new-main\n' > "$TARGET/main.txt"
  commit_all "$TARGET" "Advance mirror main"
  git -C "$TARGET" switch -q sync/vscode

  expect_failure "target feature branch is not based on refs/heads/main" \
    "$SOURCE/scripts/sync.sh" vscode "$TARGET"

  assert_eq "$(git -C "$TARGET" rev-parse HEAD)" "$branch_head"
  echo "ok - refuses feature branch behind main"
}

test_syncs_and_updates_feature_branch() {
  make_fixture "sync-feature"
  target_main="$(git -C "$TARGET" rev-parse main)"
  git -C "$TARGET" switch -q -c sync/vscode

  printf 'theme-v2\n' > "$SOURCE/vscode/theme.txt"
  commit_all "$SOURCE" "Update VS Code theme"
  first_source="$(git -C "$SOURCE" rev-parse HEAD)"
  first_output="$FIXTURE/first-output.txt"

  "$SOURCE/scripts/sync.sh" vscode "$TARGET" >"$first_output"

  assert_contains "$first_output" "source  $first_source"
  assert_contains "$first_output" "branch  sync/vscode"
  assert_contains "$first_output" "gh pr create --repo tcagriz/hadal-vscode --base main --head sync/vscode"
  assert_eq "$(git -C "$TARGET" rev-parse main)" "$target_main"
  assert_eq "$(git -C "$TARGET" branch --show-current)" "sync/vscode"
  assert_eq "$(git -C "$TARGET" rev-list --count main..sync/vscode)" "1"
  diff -qr --exclude=.git "$TARGET" "$SOURCE/vscode" >/dev/null
  git -C "$TARGET" merge-base --is-ancestor main sync/vscode
  git -C "$TARGET" show -s --format=%B HEAD | grep -Fq "$first_source"
  [ -z "$(git -C "$TARGET" remote)" ]

  printf 'theme-v3\n' > "$SOURCE/vscode/theme.txt"
  commit_all "$SOURCE" "Update VS Code theme again"
  second_source="$(git -C "$SOURCE" rev-parse HEAD)"
  second_output="$FIXTURE/second-output.txt"

  "$SOURCE/scripts/sync.sh" vscode "$TARGET" >"$second_output"

  assert_contains "$second_output" "source  $second_source"
  assert_eq "$(git -C "$TARGET" rev-list --count main..sync/vscode)" "2"
  diff -qr --exclude=.git "$TARGET" "$SOURCE/vscode" >/dev/null

  branch_head="$(git -C "$TARGET" rev-parse HEAD)"
  third_output="$FIXTURE/third-output.txt"
  "$SOURCE/scripts/sync.sh" vscode "$TARGET" >"$third_output"

  assert_contains "$third_output" "already matches"
  assert_eq "$(git -C "$TARGET" rev-parse HEAD)" "$branch_head"
  assert_eq "$(git -C "$TARGET" rev-list --count main..sync/vscode)" "2"
  echo "ok - syncs, updates, and reruns idempotently"
}

test_refuses_divergent_mirror() {
  make_fixture "divergent-mirror"
  git -C "$TARGET" switch -q -c sync/vscode
  printf 'mirror-only\n' > "$TARGET/mirror-only.txt"
  commit_all "$TARGET" "Mirror-only change"
  branch_head="$(git -C "$TARGET" rev-parse HEAD)"

  printf 'theme-v2\n' > "$SOURCE/vscode/theme.txt"
  commit_all "$SOURCE" "Update VS Code theme"

  expect_failure "does not match any commit in the vscode subtree history" \
    "$SOURCE/scripts/sync.sh" vscode "$TARGET"

  assert_eq "$(git -C "$TARGET" rev-parse HEAD)" "$branch_head"
  [ -f "$TARGET/mirror-only.txt" ]
  echo "ok - refuses divergent mirror state"
}

test_reproducible_commit() {
  make_fixture "reproducible"
  second_target="$FIXTURE/second-target"
  git clone -q --no-hardlinks "$TARGET" "$second_target"
  git -C "$second_target" remote remove origin
  git -C "$TARGET" switch -q -c sync/vscode
  git -C "$second_target" switch -q -c sync/vscode

  printf 'theme-v2\n' > "$SOURCE/vscode/theme.txt"
  commit_all "$SOURCE" "Update VS Code theme"

  "$SOURCE/scripts/sync.sh" vscode "$TARGET" >"$FIXTURE/first.txt"
  "$SOURCE/scripts/sync.sh" vscode "$second_target" >"$FIXTURE/second.txt"

  assert_eq "$(git -C "$TARGET" rev-parse HEAD)" \
    "$(git -C "$second_target" rev-parse HEAD)"
  echo "ok - creates reproducible sync commits"
}

test_package_routes() {
  for package in vscode inkdrop zed nvim; do
    make_fixture "route-$package" "$package"
    git -C "$TARGET" switch -q -c "sync/$package"
    printf 'theme-v2\n' > "$SOURCE/$PREFIX/theme.txt"
    commit_all "$SOURCE" "Update $package theme"
    output="$FIXTURE/output.txt"

    "$SOURCE/scripts/sync.sh" "$package" "$TARGET" >"$output"

    assert_contains "$output" "branch  sync/$package"
    assert_contains "$output" "gh pr create --repo $MIRROR_REPO --base main --head sync/$package"
    diff -qr --exclude=.git "$TARGET" "$SOURCE/$PREFIX" >/dev/null
  done
  echo "ok - maps every supported package"
}

test_refuses_main
test_refuses_source_as_target
test_refuses_dirty_source
test_refuses_dirty_target
test_refuses_stale_branch
test_syncs_and_updates_feature_branch
test_refuses_divergent_mirror
test_reproducible_commit
test_package_routes
