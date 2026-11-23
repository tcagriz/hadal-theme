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

## Roadmap

Track planned work in the public
[Hadal Roadmap](https://github.com/users/tcagriz/projects/3). Issues remain the
source of truth and should live in this monorepo even when the work later changes a
standalone package mirror.

- Use the **Roadmap task** issue form for proposed work.
- Add priority, area, package and release-impact metadata before work starts.
- Link pull requests with `Closes #<issue-number>`.
- Move mirror-specific bug reports into the monorepo and link the original report.
- Keep implementation checklists on the linked issue instead of duplicating them
  in multiple README or project files.

## AI-assisted contributions

AI-assisted work is welcome. The contributor opening the pull request remains
responsible for every changed line, including generated output.

- Do not send credentials, registry keys, personal configuration or other
  confidential data to an AI tool.
- Review the complete diff. Do not accept generated code, commands, package
  versions or license claims without checking them.
- Verify behavior with the relevant local checks and report the commands you
  actually ran in the pull request.
- Follow the palette and generated-file rules below. Never hand-edit generated
  output as a substitute for changing its source.
- Keep contributions licensed compatibly with this repository and do not add
  copied code without preserving required attribution and license notices.
- AI use does not bypass code-owner review, protected branches, required checks
  or deployment approvals.

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
Run the mirror synchronization regression tests when `scripts/sync.sh` changes:

```sh
bash tests/sync_test.sh
```

## Bug and security reports

Use the issue forms in this repository for bugs and planned work, including bugs
that affect a standalone package mirror. Do not split implementation discussion
between the monorepo and mirror issue trackers.

Do not open public issues for suspected vulnerabilities or credential exposure.
Follow [SECURITY.md](SECURITY.md) and use private vulnerability reporting.

## Standalone mirrors

After the package change is committed in `hadal-theme`, synchronize the dedicated
repository from a clean monorepo:

1. Update the mirror's local `main` branch without making package changes in it.
2. Create a feature branch whose name identifies the source commit.
3. Run `scripts/sync.sh` from the monorepo.

For example, for VS Code:

```sh
source_sha="$(git rev-parse --short=12 HEAD)"
git -C ../hadal-vscode switch main
git -C ../hadal-vscode pull --ff-only
git -C ../hadal-vscode switch -c "sync/vscode-$source_sha"
scripts/sync.sh vscode ../hadal-vscode
```

Use the same flow for `inkdrop` at `../hadal-inkdrop`, `zed` at `../hadal-zed`
and `nvim` at `../hadal.nvim`.

`sync.sh` requires both worktrees to be clean. It refuses to run on a mirror's
`main` or other default branch, requires the feature branch to contain the current
local mirror `main`, and verifies that the mirror's current tree corresponds to
the prior source subtree history. It then creates a deterministic, fast-forward
sync commit on the current feature branch and reports the full monorepo source
commit. The script never pushes.

Push the branch with the command printed by the script, then open a pull request
to the mirror's `main` branch:

```sh
gh pr create --repo tcagriz/hadal-vscode --base main --head "sync/vscode-$source_sha"
```

Use the mirror's `gh` pull-request template. In **Source change**, link the
monorepo pull request or commit so both reviews remain connected. To update an
existing mirror PR after another source commit, keep the same feature branch,
rerun `scripts/sync.sh`, then push that branch again. Direct pushes to `main` are
not part of the sync workflow.

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

## Roadmap source of truth

Do not add a second long-lived TODO list here. The roadmap project and its linked
issues contain the current priorities, milestones, acceptance criteria and status.
