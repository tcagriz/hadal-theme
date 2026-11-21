# Hadal Theme Suite

A unified **Hadal** color theme (based on the VS Code Abyss theme) for terminal and
development tools, so your editor, shell, multiplexer and file tools all look the same.

- [Supported tools](#supported-tools)
- [Platform support](#platform-support)
- [Palette](#palette)
- [Quick start](#quick-start)
- [Setup per tool](#setup-per-tool)
- [Uninstall](#uninstall)
- [Contributing](#contributing)
- [License](#license)

## Supported tools

Published packages:

| Tool | Install |
| --- | --- |
| [VS Code](https://marketplace.visualstudio.com/items?itemName=tcagriz.hadal-theme) | `code --install-extension tcagriz.hadal-theme` |
| [Inkdrop 6](https://github.com/tcagriz/hadal-inkdrop) | `ipm install hadal` |
| [Neovim](https://github.com/tcagriz/hadal.nvim) | lazy.nvim: `"tcagriz/hadal.nvim"` |

Other ports are installed from this monorepo:

| Tool | Install |
| --- | --- |
| [Zed](https://github.com/tcagriz/hadal-zed) | manual theme file; not yet in the Zed extension catalog |
| herdr-app | `./install.sh herdr-app` |
| Ghostty | `./install.sh ghostty` |
| cmux | `./install.sh ghostty snippets` |
| opencode | `./install.sh opencode` |
| lsd | `./install.sh lsd` |
| zsh, tmux, WezTerm, lazygit, starship, Herdr TUI | `./install.sh snippets` and the setup step below |

## Platform support

The theme definitions contain no platform-specific binaries. The project has been
tested on macOS; Linux and Windows compatibility below is not a visual or end-to-end
verification.

| Component | macOS | Linux | Windows |
| --- | --- | --- | --- |
| VS Code extension | available | available | available |
| Inkdrop theme | tested | Inkdrop 6 supports it; untested | Inkdrop 6 supports it; untested |
| `hadal.nvim` | tested | expected; untested | expected; untested |
| Standalone theme files | available | expected; untested | expected; untested |
| `install.sh` | tested | expected; untested | not native; requires bash and Windows-specific config paths |

- `install.sh` uses `$XDG_CONFIG_HOME` or `~/.config` and plain bash. The documented
  shell commands below target macOS and Linux.
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
git clone https://github.com/tcagriz/hadal-theme.git
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

Hadal is not currently published in the Zed extension catalog. The catalog already
contains a different extension named Hadal, so do not install a theme by search alone.

On macOS or Linux, `./install.sh zed` installs
`~/.config/zed/themes/hadal.json`. On Windows, copy `zed/themes/hadal.json` to
`%USERPROFILE%\AppData\Roaming\Zed\themes\`.

In Zed's `settings.json`:

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

The recommended installation is the standalone
[hadal.nvim](https://github.com/tcagriz/hadal.nvim) plugin:

```lua
{
  "tcagriz/hadal.nvim",
  lazy = false,
  priority = 1000,
  config = function()
    vim.cmd.colorscheme("hadal")
  end,
}
```

Alternatively, `./install.sh neovim` links the same files into `~/.config/nvim/`.
Activate it in `init.lua`, **after** your plugins and any other colorscheme:
`vim.cmd.colorscheme("hadal")`.

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

Install the published Inkdrop 6 theme:

```sh
ipm install hadal
```

Then restart or reload Inkdrop and pick **Hadal** in **Preferences > Themes**. The
package themes the UI, editor and Markdown preview together.

### VS Code

Install the published extension from
[Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=tcagriz.hadal-theme)
or with:

```sh
code --install-extension tcagriz.hadal-theme
```

Then run **Preferences: Color Theme** and select **Hadal**. VSIX files are also
available from [GitHub Releases](https://github.com/tcagriz/hadal-vscode/releases/latest).

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

- VS Code: `code --uninstall-extension tcagriz.hadal-theme`.
- Inkdrop: `ipm uninstall hadal`.
- Neovim: remove the `tcagriz/hadal.nvim` plugin declaration from lazy.nvim.
- Delete `~/.config/ghostty/themes/hadal` (a copy) and the files the installer linked (`hadal.json`, `colors/hadal.lua`,
  `lua/hadal/`, `lua/plugins/hadal-bufferline.lua`, `lsd/colors.yaml`,
  `~/.config/hadal/`).
- If the installer backed up a file, it is next to the original as `<name>.bak`; move it
  back to restore it.
- Remove the one-line includes you added to `.zshrc`, `.tmux.conf`, `.wezterm.lua` and
  the tables you copied into `starship.toml` and the Herdr TUI config.

## Contributing

Development setup, generated-file rules, publishing workflows and the cross-platform
roadmap are in [CONTRIBUTING.md](CONTRIBUTING.md). Please make source changes in this
monorepo; the dedicated package repositories are synchronized mirrors.

## License

MIT, see [LICENSE](LICENSE).
