# Contributing to Hadal

Make source changes in this repository. `hadal-vscode`, `hadal-inkdrop`,
`hadal-zed` and `hadal.nvim` are synchronized mirrors and are not the source of
truth.

## Protected branch policy

The `main` branch is protected in all five repositories.

- Every change to `main` must come through a pull request; direct pushes are
  blocked.
- Pull requests from contributors require one approval from `@tcagriz`, the code
  owner, and all required checks must pass.
- Pull requests opened by `@tcagriz` may use the repository ruleset's
  **pull request only** bypass. This keeps the pull request and audit trail
  without requiring `@tcagriz` to approve their own pull request.
- The Marketplace and Inkdrop publish jobs target the protected `production`
  environment. They cannot publish until `@tcagriz` approves the deployment.

## Development

`palette/palette.json` is the single source of truth for colors. These files are
generated from it and must not be edited by hand:

- `herdr-app/hadal.json`
- `herdr-tui/theme.toml`
- `wezterm/hadal.lua`
- `ghostty/hadal`
- `cmux/hadal.json`
- `opencode/hadal.json`
- `opencode/v1/hadal.json`
- `tmux/hadal.conf`
- `starship/hadal.toml`
- `zsh/hadal.zsh`
- `lsd/colors.yaml`
- `lazygit/config.yml`
- `zed/themes/hadal.json`
- `neovim/lua/hadal/palette.lua`
- `inkdrop/styles/palette.css`
- `vscode/themes/hadal-color-theme.json`

Regenerate and verify them with Python 3:

```sh
python3 scripts/build.py
python3 scripts/build.py --check
```

When changing a color, commit both the palette and every regenerated file.

The following hand-written files contain mappings or tool-specific settings rather
than generated color data:

- `neovim/colors/hadal.lua`
- `neovim/lua/hadal/bufferline.lua`
- `neovim/lazy.lua`
- `inkdrop/package.json` and `inkdrop/styles/{ui,syntax,preview}.css`
- `vscode/package.json`
- `zed/extension.toml`
- `lsd/config.yaml`
- `install.sh` and `scripts/build.py`

## Validation

Run the smallest relevant checks before committing:

```sh
python3 scripts/build.py --check
python3 -m json.tool palette/palette.json > /dev/null
python3 -m json.tool zed/themes/hadal.json > /dev/null
python3 -m json.tool vscode/themes/hadal-color-theme.json > /dev/null
```

The `vscode/` and `inkdrop/` package directories also have their own CI workflows.

## Standalone mirrors

After committing package changes, synchronize the dedicated repository:

```sh
scripts/sync.sh vscode
scripts/sync.sh inkdrop
scripts/sync.sh zed
scripts/sync.sh nvim
```

The script uses `git subtree split`, refuses dirty package directories and never
pushes. Create a feature branch in the mirror before syncing, push that branch and
open a pull request; direct pushes to a mirror's `main` branch are blocked.

## Publishing

Do not commit access tokens or other credentials.

- **VS Code:** update `vscode/package.json` and `vscode/CHANGELOG.md`, then run the
  `Publish to VS Code Marketplace` workflow in `hadal-vscode` and approve the
  `production` deployment.
- **Inkdrop:** update `inkdrop/package.json` and `inkdrop/CHANGELOG.md`, explicitly
  run `npx generate-palette`, then run `ipm publish` with local credentials or the
  maintained GitHub Actions workflow. The workflow pauses for the same
  `production` deployment approval.
- **Zed:** not published yet. The extension ID and registry name must be resolved
  before submitting to the Zed registry.

## Cross-platform work

- [ ] Run `install.sh` on Linux (container or VM) and fix any path or tool differences.
- [ ] Run `build.py --check` and `sync.sh` on Linux and Windows (WSL).
- [ ] Add a GitHub Actions matrix for Linux, macOS and Windows.
- [ ] Make generated-file line endings stable with Windows CRLF checkouts.
- [ ] Add `.gitattributes` for generated files.
- [ ] Detect lazygit's config directory per operating system.
- [ ] Add a native Windows installer with `%APPDATA%` and `%LOCALAPPDATA%` paths.
- [ ] Verify the ports on Linux and Windows.
