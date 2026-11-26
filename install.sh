#!/usr/bin/env bash
# Install the Hadal theme files.
#
# Usage: ./install.sh [--copy] [--dry-run] [tool ...]
#   --copy      copy files instead of symlinking them into place
#   --dry-run   print what would happen without changing anything
#   tool        herdr-app, zed, ghostty, opencode, neovim, lsd, snippets (default: all)
#
# Files owned entirely by the theme (herdr-app, zed, ghostty, neovim colorscheme, lsd colors)
# are installed into the tool's config directory. Existing different files are
# moved to <name>.bak first.
#
# Configs you probably already customized (starship, tmux, zsh, wezterm, herdr-tui,
# lazygit, cmux) are never modified. They are placed in $XDG_CONFIG_HOME/hadal/<tool>/
# and the include instructions are printed.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"
MODE="link"
DRY=0
TOOLS=()

for arg in "$@"; do
  case "$arg" in
    --copy) MODE=copy ;;
    --dry-run) DRY=1 ;;
    -h|--help) sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    herdr-app|zed|ghostty|opencode|neovim|lsd|snippets) TOOLS+=("$arg") ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done
[ ${#TOOLS[@]} -eq 0 ] && TOOLS=(herdr-app zed ghostty opencode neovim lsd snippets)

run() {
  if [ "$DRY" = 1 ]; then echo "  [dry-run] $*"; else "$@"; fi
}

place() {
  local src="$1" dest="$2" placement_mode="${3:-$MODE}" backup="${2}.bak"
  if [ ! -e "$src" ]; then echo "  missing source: $src" >&2; return 1; fi
  run mkdir -p "$(dirname "$dest")"
  if [ "$placement_mode" = link ] && [ -L "$dest" ] &&
    [ "$(readlink "$dest")" = "$src" ]; then
    echo "  ok      $dest"; return
  fi
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    if [ "$placement_mode" = copy ] && [ ! -L "$dest" ] && [ -f "$dest" ] &&
      cmp -s "$src" "$dest"; then
      echo "  ok      $dest"; return
    fi
    if [ -e "$backup" ] || [ -L "$backup" ]; then
      echo "  refusing to overwrite existing backup: $backup" >&2
      return 1
    fi
    run mv -n "$dest" "$backup"
    if [ "$DRY" = 0 ] && { [ -e "$dest" ] || [ -L "$dest" ]; }; then
      echo "  another installer created the backup: $backup" >&2
      return 1
    fi
    echo "  backup  $backup"
  fi
  if [ "$placement_mode" = link ]; then
    run ln -s "$src" "$dest"
  else
    run cp "$src" "$dest"
  fi
  echo "  $placement_mode    $dest"
}

for tool in "${TOOLS[@]}"; do
  echo "[$tool]"
  case "$tool" in
    herdr-app)
      place "$ROOT/herdr-app/hadal.json" "$CONFIG/herdr-app/themes/hadal.json"
      echo "  select the 'hadal' theme in herdr-app settings"
      ;;
    zed)
      place "$ROOT/zed/themes/hadal.json" "$CONFIG/zed/themes/hadal.json"
      echo "  set \"theme\": { \"dark\": \"Hadal\" } in Zed settings.json"
      ;;
    ghostty)
      # Always a real file: cmux does not list symlinked themes. Re-run to update it.
      dest="$CONFIG/ghostty/themes/hadal"
      place "$ROOT/ghostty/hadal" "$dest" copy
      echo "  set 'theme = hadal' in your Ghostty config (cmux: cmux themes set hadal)"
      ;;
    opencode)
      place "$ROOT/opencode/hadal.json" "$CONFIG/opencode/themes/hadal.json"
      echo "  opencode 2.x: set \"theme\": {\"name\": \"hadal\", \"mode\": \"dark\"} in $CONFIG/opencode/cli.json"
      ;;
    neovim)
      place "$ROOT/neovim/colors/hadal.lua" "$CONFIG/nvim/colors/hadal.lua"
      place "$ROOT/neovim/lua/hadal/palette.lua" "$CONFIG/nvim/lua/hadal/palette.lua"
      place "$ROOT/neovim/lua/hadal/bufferline.lua" "$CONFIG/nvim/lua/hadal/bufferline.lua"
      place "$ROOT/neovim/lazy.lua" "$CONFIG/nvim/lua/plugins/hadal-bufferline.lua"
      echo "  add 'vim.cmd.colorscheme(\"hadal\")' to your init.lua"
      echo "  bufferline.nvim: applied via lazy.nvim spec; without lazy use"
      echo "    require('bufferline').setup({ highlights = require('hadal.bufferline') })"
      ;;
    lsd)
      place "$ROOT/lsd/colors.yaml" "$CONFIG/lsd/colors.yaml"
      if [ -e "$CONFIG/lsd/config.yaml" ]; then
        echo "  keep existing config.yaml; make sure it contains: color: { theme: custom }"
      else
        place "$ROOT/lsd/config.yaml" "$CONFIG/lsd/config.yaml"
      fi
      ;;
    snippets)
      for t in starship tmux zsh wezterm herdr-tui lazygit cmux; do
        for f in "$ROOT/$t"/*; do
          place "$f" "$CONFIG/hadal/$t/$(basename "$f")"
        done
      done
      cat <<EOF
  Include them from your own configs:
    zsh       source $CONFIG/hadal/zsh/hadal.zsh        (after your plugins)
    tmux      source-file $CONFIG/hadal/tmux/hadal.conf   (before catppuccin loads)
    starship  copy the [palettes.hadal] table into starship.toml, set palette = 'hadal'
    wezterm   config.colors = dofile("$CONFIG/hadal/wezterm/hadal.lua")
    herdr-tui merge $CONFIG/hadal/herdr-tui/theme.toml into ~/.config/herdr/config.toml
    cmux      merge $CONFIG/hadal/cmux/hadal.json into ~/.config/cmux/cmux.json (or: cmux config set)
    lazygit   merge the gui.theme block of $CONFIG/hadal/lazygit/config.yml into your lazygit config
EOF
      ;;
  esac
done
