# Hadal Theme Suite

A unified **Hadal** color theme (based on the VS Code Abyss theme) for terminal and
development tools, so your editor, shell, multiplexer and file tools all look the same.

- [Supported tools](#supported-tools)
- [Platform support](#platform-support)
- [Palette](#palette)
- [Quick start](#quick-start)
- [Setup per tool](#setup-per-tool)
- [Uninstall](#uninstall)
- [Development](#development)
- [Status](#status)
- [TODO](#todo)

## Supported tools

| Tool | Files | How it is applied |
| --- | --- | --- |
| herdr-app | `herdr-app/hadal.json` | installed, select the theme in settings |
| Zed | `zed/themes/hadal.json` | installed, select the theme in settings |
| Ghostty | `ghostty/hadal` | installed, set `theme = hadal` |
| cmux | `ghostty/hadal`, `cmux/hadal.json` | Ghostty theme plus a settings snippet to merge |
| opencode | `opencode/hadal.json` | installed, set the theme in `cli.json` |
| Neovim (Treesitter, LSP, plugins) | `neovim/` | installed, activate with `:colorscheme hadal` |
| Inkdrop 6 | `inkdrop/` | link into the packages folder, select the theme in Preferences |
| VS Code | `vscode/` | install the extension, select the theme |
| lsd | `lsd/` | installed, needs `color.theme: custom` |
| zsh (syntax highlighting, autosuggestions, fzf) | `zsh/hadal.zsh` | one `source` line |
| tmux (catppuccin/tmux) | `tmux/hadal.conf` | one `source-file` line |
| WezTerm | `wezterm/hadal.lua` | one `dofile` line |
| lazygit | `lazygit/config.yml` | symlink or `LG_CONFIG_FILE` |
| starship | `starship/hadal.toml` | **copy the palette table** (no include support) |
| Herdr TUI | `herdr-tui/theme.toml` | **copy the theme table** (no include support) |

## Platform support

Only macOS has been tested so far. Linux and Windows status is based on reading the code.

| Part | macOS | Linux | Windows |
| --- | --- | --- | --- |
| Theme files (JSON, Lua, TOML, CSS) | ✅ | ✅ | ✅ |
| VS Code, Zed and Inkdrop packages | ✅ | ✅ | ✅ |
| `hadal.nvim` (lazy.nvim) | ✅ | ✅ | ✅ |
| `install.sh` | ✅ tested | ⚠️ expected to work, untested | ❌ needs bash (WSL or Git Bash) and different paths |
| `build.py` and `sync.sh` | ✅ | ⚠️ untested | ⚠️ untested (line endings, bash) |

- `install.sh` uses `$XDG_CONFIG_HOME` or `~/.config` and plain bash.
- lazygit uses `~/Library/Application Support/lazygit/` on macOS and `~/.config/lazygit/` on Linux.
- Platform support of the apps themselves depends on each app: cmux is macOS only,
  Ghostty runs on macOS and Linux, and WezTerm, Zed, VS Code, Neovim, tmux, starship
  and lsd run on all three.

## Palette

| Role | Color |
| --- | --- |
| background | `#000c18` |
| foreground | `#6688cc` |
| selection | `#770811` |
| cursor | `#ddbb88` |
| sidebar | `#060621` |
| border | `#2b2b4a` |
| comment | `#384887` |
| string | `#22aa44` |

Background, foreground, selection, cursor and the 16 terminal ANSI colors come from
[microsoft/vscode](https://github.com/microsoft/vscode) (`extensions/theme-abyss`, MIT).
Colors that have no VS Code equivalent (agent status colors, markdown headings,
plugin-specific groups, diagnostic tints) were chosen for this project.
The full list is in [`palette/palette.json`](palette/palette.json).

## Quick start

```sh
git clone <repo-url> hadal-theme
cd hadal-theme
./install.sh --dry-run        # preview, changes nothing
./install.sh                  # symlink everything (add --copy to copy instead)
./install.sh zed neovim       # only some tools: herdr-app, zed, opencode, neovim, lsd, snippets
```

What the installer does:

- **Theme-owned files** (herdr-app, Zed, Neovim colorscheme, lsd colors) are placed in
  the tool's config directory. If a different file already exists there it is moved to
  `<name>.bak` first. Running the installer again is safe.
- **Your own configs are never modified.** Files that you probably customized
  (starship, tmux, zsh, WezTerm, Herdr TUI, lazygit) are placed in
  `~/.config/hadal/<tool>/` and the installer prints how to include them.
- `$XDG_CONFIG_HOME` is respected (default `~/.config`).
- Symlinks point into this clone. If you move or delete the clone, run the installer
  again or use `--copy`.

After installing, finish the one-time steps for each tool below.

## Setup per tool

In the examples, `~/.config/hadal/` is where `./install.sh snippets` puts the files.

### herdr-app

`./install.sh herdr-app` installs `~/.config/herdr-app/themes/hadal.json`.
Open the herdr-app settings and select the theme named **hadal**.

### Zed

`zed/` is also a ready-to-publish Zed extension (`extension.toml` + `themes/`).
`./install.sh zed` installs `~/.config/zed/themes/hadal.json`. In Zed's `settings.json`:

```json
"theme": {
  "mode": "dark",
  "light": "One Light",
  "dark": "Hadal"
}
```

Use any light theme you like for `light`.

### Ghostty

`./install.sh ghostty` installs `~/.config/ghostty/themes/hadal`. In your Ghostty config
(`~/.config/ghostty/config`):

```
theme = hadal
```

Reload with the *Reload Configuration* shortcut or restart Ghostty.

### cmux

cmux renders the terminal with Ghostty config, so the **Ghostty theme** above colors the
terminal. `./install.sh ghostty` copies the theme as a real file because cmux does not
list symlinked themes. Select it with:

```sh
cmux themes set hadal
```

(this writes cmux's own `config.ghostty`, which takes precedence over the Ghostty config).

`cmux/hadal.json` themes the cmux chrome: accent color, sidebar selection and badge,
pane borders, pane flash and the named workspace colors. `./install.sh snippets` places
it in `~/.config/hadal/cmux/`. cmux has no include support, so merge its keys into
`~/.config/cmux/cmux.json`, then run `cmux config check` and `cmux reload-config`.
To remove the overrides, delete those keys again.

### opencode

`./install.sh opencode` links `opencode/hadal.json` to `~/.config/opencode/themes/hadal.json`.
Select it in `~/.config/opencode/cli.json`:

```json
{ "theme": { "name": "hadal", "mode": "dark" } }
```

This is the opencode 2.x format (verified with opencode 2.3.2). The theme is dark only.

For opencode 1.x, copy `opencode/v1/hadal.json` to `~/.config/opencode/themes/hadal.json`
and set `"theme": "hadal"` in `tui.json` (verified with 1.19.6).

### Neovim

The same files are also published as the standalone plugin `hadal.nvim` (see
`neovim/README.md` for lazy.nvim installation); `./install.sh neovim` is the
alternative that links the files from this checkout.

`./install.sh neovim` places these files in `~/.config/nvim/`:

| File | Purpose |
| --- | --- |
| `colors/hadal.lua` | colorscheme: UI, Treesitter, LSP, diagnostics, diff, terminal colors, plugin groups |
| `lua/hadal/palette.lua` | generated color table used by everything below |
| `lua/hadal/bufferline.lua` | highlights for bufferline.nvim |
| `lazy.lua` (installed as `lua/plugins/hadal-bufferline.lua`) | lazy.nvim spec that applies those highlights |

Activate it in `init.lua`, **after** your plugins and any other colorscheme are loaded:

```lua
vim.cmd.colorscheme("hadal")
```

Plugin groups covered: rainbow-delimiters, indent-blankline, nvim-tree, telescope,
render-markdown, todo-comments, snacks and bufferline.

**bufferline.nvim** is themed automatically when you use lazy.nvim. The spec is marked
`optional = true`, so it only merges the Hadal `highlights` into your own bufferline spec
and never installs the plugin. Your other bufferline options stay untouched.
Without lazy.nvim, pass the highlights yourself:

```lua
require("bufferline").setup({ highlights = require("hadal.bufferline") })
```

### Inkdrop

Inkdrop 6 theme package in `inkdrop/` (`palette.css` is generated; `ui.css`,
`syntax.css`, `preview.css` map Inkdrop variables to `--hadal-*` colors).

```sh
cd inkdrop && ipm link
```

Restart or reload Inkdrop, then pick **Hadal** in Preferences > Themes (UI, editor and
preview). For live editing, use the dev-tools plugin's "Start hot reloading themes".
Note: `inkdrop/package.json` runs Inkdrop's own `generate-palette` on publish; that
output is unrelated to `palette/palette.json`.

### VS Code

Extension in `vscode/` (`themes/hadal-color-theme.json` is generated). Build and install it
locally:

```sh
cd vscode && npx @vscode/vsce package --allow-missing-repository
code --install-extension hadal-theme-0.1.0.vsix
```

Then run **Preferences: Color Theme** and select **Hadal**. To try it without installing,
open `vscode/` in VS Code and press `F5` (Extension Development Host).

### lsd

`./install.sh lsd` installs `~/.config/lsd/colors.yaml`. lsd only reads it when
`config.yaml` selects the custom theme. If you have no `config.yaml`, the installer
creates one. If you already have one, add this to it:

```yaml
color:
  theme: custom
```

### zsh (syntax highlighting, autosuggestions, fzf)

Requires zsh-syntax-highlighting and/or zsh-autosuggestions if you want those colors.
Add this to `~/.zshrc`, **after** the plugins are sourced:

```zsh
source "$HOME/.config/hadal/zsh/hadal.zsh"
```

It sets `ZSH_HIGHLIGHT_STYLES`, `ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE` and `FZF_DEFAULT_OPTS`.
Note that it overwrites an existing `FZF_DEFAULT_OPTS`; append your other fzf flags after
the `source` line. Open a new shell (or `source ~/.zshrc`) to apply.

### tmux (catppuccin/tmux)

Requires the [catppuccin/tmux](https://github.com/catppuccin/tmux) plugin. It reads the
`@thm_*` colors only if they are not set yet, so Hadal must be sourced **before** the
plugin loads. In `~/.tmux.conf`:

```tmux
set -g @plugin 'catppuccin/tmux'
set -g @catppuccin_flavor "mocha"

source-file ~/.config/hadal/tmux/hadal.conf   # before the plugin is run/loaded

# ... then TPM (run '~/.tmux/plugins/tpm/tpm') or your own `run` line for the plugin
```

Reload with `tmux source ~/.tmux.conf` (or kill the tmux server for a clean start).

### WezTerm

In `~/.wezterm.lua`:

```lua
config.colors = dofile(os.getenv("HOME") .. "/.config/hadal/wezterm/hadal.lua")
```

WezTerm reloads the config automatically.

### lazygit

`lazygit/config.yml` contains only `gui.theme`. Pick one:

- **No existing lazygit config:** symlink it into lazygit's config directory
  (macOS: `~/Library/Application Support/lazygit/config.yml`, Linux:
  `~/.config/lazygit/config.yml`):

  ```sh
  ln -s ~/.config/hadal/lazygit/config.yml ~/.config/lazygit/config.yml
  ```

- **Existing config:** load both files with `LG_CONFIG_FILE` (later files override earlier ones):

  ```sh
  export LG_CONFIG_FILE="$HOME/.config/lazygit/config.yml,$HOME/.config/hadal/lazygit/config.yml"
  ```

  Or copy the `gui.theme` block into your own file.

### starship

starship cannot include other files, so the palette has to live inside your
`~/.config/starship.toml`. One-time steps:

1. Open `~/.config/hadal/starship/hadal.toml`.
2. Copy the whole `[palettes.hadal]` table into `~/.config/starship.toml`.
3. Set `palette = 'hadal'` as a **top-level** key, above any `[table]` header.

The palette uses Catppuccin color names (`red`, `peach`, `surface0`, `text`, ...), as many
starship presets do. Modules that reference a palette name, for example
`fg:peach` or `bg:surface0`, change automatically. Modules that use literal hex colors or
the 16 ANSI names are not affected.
Check the result with `starship explain` or just open a new prompt.

If you copy the table, it will not follow later changes in this repo. Re-copy it after you
update the repo.

### Herdr TUI

Herdr TUI cannot include other files either. One-time steps:

1. Open `~/.config/hadal/herdr-tui/theme.toml`.
2. Copy the `[theme.custom]` table into `~/.config/herdr/config.toml`.
3. Keep or add the `[theme]` section (`name = "catppuccin"` is the base the custom colors
   are applied on; `auto_switch = false`).
4. Apply with `herdr server reload-config`, or restart Herdr. If no server is running
   the command reports `server_not_running`; just start `herdr`.

This is separate from **herdr-app** (the GUI), which uses `herdr-app/hadal.json`.

## Uninstall

- Delete `~/.config/ghostty/themes/hadal` (a copy) and the files the installer linked (`hadal.json`, `colors/hadal.lua`,
  `lua/hadal/`, `lua/plugins/hadal-bufferline.lua`, `lsd/colors.yaml`,
  `~/.config/hadal/`).
- If the installer backed up a file, it is next to the original as `<name>.bak`; move it
  back to restore it.
- Remove the one-line includes you added to `.zshrc`, `.tmux.conf`, `.wezterm.lua` and
  the tables you copied into `starship.toml` and the Herdr TUI config.

## Development

`palette/palette.json` is the single source of truth for colors. These files are
**generated** from it and must not be edited by hand:

`herdr-app/hadal.json`, `herdr-tui/theme.toml`, `wezterm/hadal.lua`, `ghostty/hadal`, `cmux/hadal.json`, `opencode/hadal.json`, `opencode/v1/hadal.json`, `tmux/hadal.conf`,
`starship/hadal.toml`, `zsh/hadal.zsh`, `lsd/colors.yaml`, `lazygit/config.yml`,
`zed/themes/hadal.json`, `neovim/lua/hadal/palette.lua`, `inkdrop/styles/palette.css`, `vscode/themes/hadal-color-theme.json`
```sh
python3 scripts/build.py          # regenerate after editing the palette
python3 scripts/build.py --check  # verify nothing is stale (also run in CI)
```

Workflow for changing a color: edit `palette/palette.json`, run `scripts/build.py`,
commit both the palette and the regenerated files. Requires Python 3 only.

These files are **hand-written** because they hold mapping logic or a static setting
rather than color data:

- `neovim/colors/hadal.lua`: maps highlight groups to palette roles. It contains no hex
  values and reads every color from the generated `hadal/palette.lua`.
- `neovim/lua/hadal/bufferline.lua`, `neovim/lazy.lua`, `neovim/README.md`
- `inkdrop/package.json`, `inkdrop/styles/{ui,syntax,preview}.css` (no hex, only `var(--hadal-*)`)
- `vscode/package.json`
- `zed/extension.toml`, `zed/README.md`
- `lsd/config.yaml`
- `install.sh`, `scripts/build.py`

Standalone repos: `inkdrop/`, `vscode/`, `zed/` and `neovim/` are mirrored into `../hadal-inkdrop`,
`../hadal-vscode`, `../hadal-zed` and `../hadal.nvim` with `scripts/sync.sh <inkdrop|vscode|zed|nvim>`
(`git subtree split`, never pushes). Commit your changes in the package folder first.

CI (`.github/workflows/check.yml`) runs `scripts/build.py --check` and validates the JSON files.

## Status

Early work in progress. Verified: the generated files match the original hand-made ones,
`install.sh` was tested against a temporary config directory, and Neovim, tmux, zsh,
lsd and WezTerm load the theme without errors. Not yet verified visually or end to end:
lazygit, Zed, Ghostty, cmux, Herdr TUI, starship and Inkdrop on a clean machine.

## TODO

Cross-platform work, in rough priority order:

- [ ] Run `install.sh` on Linux (container or VM) and fix any path or tool differences.
- [ ] Run `build.py --check` and `sync.sh` on Linux and Windows (WSL).
- [ ] Add a GitHub Actions matrix (ubuntu, macos, windows) for `build.py --check` and the JSON checks.
- [ ] Make `build.py` write files with `\n` line endings on Windows, so `--check` is stable with CRLF checkouts.
- [ ] Add `.gitattributes` to force LF for generated files.
- [ ] Make `install.sh` detect lazygit's config directory per OS instead of documenting it.
- [ ] Write a Windows installer (`install.ps1`) with the right config paths (`%APPDATA%`, `%LOCALAPPDATA%`) and a copy fallback when symlinks are not allowed.
- [ ] Document per-tool config locations on Linux and Windows (Zed, Ghostty, WezTerm, Neovim, lsd, starship, tmux).
- [ ] Verify Inkdrop, VS Code, Zed and Neovim themes on Linux and Windows.
- [ ] Mark cmux (macOS only) and Ghostty (no Windows build) clearly in the tool table.
- [ ] Update the Status section once each platform has been verified.

## License

MIT, see [LICENSE](LICENSE).
