#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL="$ROOT/install.sh"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/hadal-install-test.XXXXXX")"
trap 'rm -rf -- "$TMP"' EXIT

fail() {
  echo "not ok: $*" >&2
  exit 1
}

assert_eq() {
  [ "$1" = "$2" ] || fail "expected '$2', got '$1'"
}

assert_exists() {
  [ -e "$1" ] || [ -L "$1" ] || fail "expected path to exist: $1"
}

assert_missing() {
  [ ! -e "$1" ] && [ ! -L "$1" ] || fail "expected path to be absent: $1"
}

assert_contains() {
  grep -Fq "$2" "$1" || {
    cat "$1" >&2
    fail "expected output to contain: $2"
  }
}

fixture() {
  FIXTURE="$TMP/$1"
  HOME_DIR="$FIXTURE/home"
  CONFIG="$FIXTURE/config"
  mkdir -p "$HOME_DIR"
}

install() {
  HOME="$HOME_DIR" XDG_CONFIG_HOME="$CONFIG" "$INSTALL" "$@"
}

expect_failure() {
  expected="$1"
  shift
  output="$FIXTURE/output.txt"
  if install "$@" >"$output" 2>&1; then
    cat "$output" >&2
    fail "installer unexpectedly succeeded"
  fi
  assert_contains "$output" "$expected"
}

test_dry_run_writes_nothing() {
  fixture dry-run
  output="$FIXTURE/output.txt"
  install --dry-run zed >"$output"
  assert_contains "$output" "[dry-run]"
  assert_missing "$CONFIG"
  echo "ok - dry-run writes nothing"
}

test_symlink_install_is_idempotent() {
  fixture symlink
  first="$FIXTURE/first.txt"
  second="$FIXTURE/second.txt"
  install zed >"$first"
  destination="$CONFIG/zed/themes/hadal.json"
  assert_eq "$(readlink "$destination")" "$ROOT/zed/themes/hadal.json"
  install zed >"$second"
  assert_contains "$second" "ok      $destination"
  assert_missing "$destination.bak"
  echo "ok - symlink install is idempotent"
}

test_copy_install_is_idempotent() {
  fixture copy
  destination="$CONFIG/zed/themes/hadal.json"
  install --copy zed
  [ -f "$destination" ]
  [ ! -L "$destination" ]
  cmp -s "$ROOT/zed/themes/hadal.json" "$destination"
  output="$FIXTURE/output.txt"
  install --copy zed >"$output"
  assert_contains "$output" "ok      $destination"
  assert_missing "$destination.bak"
  echo "ok - copy install is idempotent"
}

test_copy_replaces_existing_symlink() {
  fixture copy-transition
  destination="$CONFIG/zed/themes/hadal.json"
  install zed
  [ -L "$destination" ]

  install --copy zed

  [ -f "$destination" ]
  [ ! -L "$destination" ]
  [ -L "$destination.bak" ]
  assert_eq "$(readlink "$destination.bak")" "$ROOT/zed/themes/hadal.json"
  echo "ok - copy mode replaces an existing symlink"
}

test_existing_file_gets_backup() {
  fixture backup
  destination="$CONFIG/zed/themes/hadal.json"
  mkdir -p "$(dirname "$destination")"
  printf 'user theme\n' >"$destination"
  output="$FIXTURE/output.txt"
  install --copy zed >"$output"
  assert_eq "$(cat "$destination.bak")" "user theme"
  cmp -s "$ROOT/zed/themes/hadal.json" "$destination"
  assert_contains "$output" "backup  $destination.bak"
  echo "ok - existing files get predictable backups"
}

test_existing_backup_is_preserved() {
  fixture preserve-backup
  destination="$CONFIG/zed/themes/hadal.json"
  mkdir -p "$(dirname "$destination")"
  printf 'new user file\n' >"$destination"
  printf 'original backup\n' >"$destination.bak"

  expect_failure "refusing to overwrite existing backup: $destination.bak" --copy zed

  assert_eq "$(cat "$destination")" "new user file"
  assert_eq "$(cat "$destination.bak")" "original backup"
  echo "ok - existing backups are never overwritten"
}

test_broken_symlink_is_backed_up() {
  fixture broken-symlink
  destination="$CONFIG/zed/themes/hadal.json"
  mkdir -p "$(dirname "$destination")"
  ln -s "$FIXTURE/missing-source" "$destination"

  install --copy zed

  [ -f "$destination" ]
  [ -L "$destination.bak" ]
  assert_eq "$(readlink "$destination.bak")" "$FIXTURE/missing-source"
  echo "ok - broken symlinks are backed up"
}

test_ghostty_copy_backs_up_and_is_idempotent() {
  fixture ghostty-copy
  destination="$CONFIG/ghostty/themes/hadal"
  mkdir -p "$(dirname "$destination")"
  printf 'user ghostty theme\n' >"$destination"

  install ghostty

  cmp -s "$ROOT/ghostty/hadal" "$destination"
  assert_eq "$(cat "$destination.bak")" "user ghostty theme"
  output="$FIXTURE/output.txt"
  install ghostty >"$output"
  assert_contains "$output" "ok      $destination"
  assert_eq "$(cat "$destination.bak")" "user ghostty theme"
  echo "ok - Ghostty copy mode backs up and reruns safely"
}

test_ghostty_broken_symlink_preserves_backup() {
  fixture ghostty-link
  destination="$CONFIG/ghostty/themes/hadal"
  mkdir -p "$(dirname "$destination")"
  ln -s "$FIXTURE/missing-source" "$destination"

  install ghostty

  [ -f "$destination" ]
  [ -L "$destination.bak" ]
  assert_eq "$(readlink "$destination.bak")" "$FIXTURE/missing-source"
  echo "ok - Ghostty broken symlinks are backed up"
}

test_default_uses_isolated_home() {
  fixture default
  install zed
  assert_exists "$CONFIG/zed/themes/hadal.json"
  assert_missing "$HOME_DIR/.config/zed/themes/hadal.json"
  echo "ok - installer respects XDG_CONFIG_HOME"
}

test_dry_run_writes_nothing
test_symlink_install_is_idempotent
test_copy_install_is_idempotent
test_copy_replaces_existing_symlink
test_existing_file_gets_backup
test_existing_backup_is_preserved
test_broken_symlink_is_backed_up
test_ghostty_copy_backs_up_and_is_idempotent
test_ghostty_broken_symlink_preserves_backup
test_default_uses_isolated_home
