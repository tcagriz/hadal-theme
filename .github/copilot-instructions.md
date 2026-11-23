# Hadal development instructions

## Repository model

- This repository is the source of truth for all Hadal packages.
- Make source changes in the relevant monorepo directory: `vscode/`, `inkdrop/`,
  `zed/` or `neovim/`. The standalone `hadal-vscode`, `hadal-inkdrop`,
  `hadal-zed` and `hadal.nvim` repositories are synchronized mirrors.
- Do not edit a mirror-only checkout as the primary source of a feature. Sync
  approved package changes with `scripts/sync.sh` and open a pull request in the
  mirror.
- Keep `main` protected. Work on a feature branch and open a pull request.
- Use the public Hadal Roadmap and its linked issues as the source of truth for
  priority, scope and acceptance criteria. Do not create another long-lived
  roadmap or TODO list in this repository.
- Link implementation pull requests to their roadmap issue with
  `Closes #<issue-number>`.
- Follow the root `CONTRIBUTING.md`, pull request template and issue forms for
  contribution scope, validation and reporting.
- For suspected vulnerabilities or exposed credentials, follow
  `SECURITY.md`; never open a public issue or include secret values.

## Palette and generated files

- `palette/palette.json` is the single source of truth for colors.
- Do not hand-edit generated files. Update the palette or the generator instead,
  then regenerate all outputs:

  ```sh
  python3 scripts/build.py
  python3 scripts/build.py --check
  ```

- Commit the palette, generator and every regenerated output in the same
  change.
- Preserve deterministic output. Do not make incidental formatting or
  line-ending changes to generated files.
- Treat `scripts/build.py` output as authoritative. Use `CONTRIBUTING.md` for
  the current generated-file list and package-specific source rules.
- Changes to hand-written package mappings may require matching changes in
  other ports. Check the palette roles and existing mappings before adding a
  one-off color.

## Implementation rules

- Prefer small, surgical changes that preserve existing public behavior.
- Reuse the palette roles and existing generator helpers before introducing
  duplicated color values or format-specific logic.
- Follow the style and terminology of the surrounding package. Do not add
  unrelated cleanup to feature or release changes.
- Keep installer and configuration changes safe to rerun. Never overwrite a
  user's existing configuration without an explicit backup or clear, opt-in
  replacement behavior.
- Respect `XDG_CONFIG_HOME` in installer changes and use temporary profile
  directories for tests.
- Update the related README or `CONTRIBUTING.md` when commands, installation
  steps or supported behavior change.
- Never commit tokens, access keys, registry credentials or personal machine
  configuration. Keep publishing credentials in the approved `production`
  environment.
- Preserve the required reviewer and environment approval gates for package
  publishing.
- Update a package manifest, changelog and release automation together when a
  versioned package changes.

## Validation

Run the smallest relevant checks, then widen validation if the shared
generator or multiple ports changed.

Root checks:

```sh
python3 scripts/build.py --check
python3 -m json.tool palette/palette.json > /dev/null
python3 -m json.tool zed/themes/hadal.json > /dev/null
python3 -m json.tool cmux/hadal.json > /dev/null
python3 -m json.tool opencode/hadal.json > /dev/null
python3 -m json.tool opencode/v1/hadal.json > /dev/null
python3 -m json.tool vscode/themes/hadal-color-theme.json > /dev/null
python3 -m json.tool vscode/package.json > /dev/null
```

Package checks:

```sh
cd vscode
npx --yes @vscode/vsce@4.1.1 package --out /tmp/hadal-theme.vsix

cd ../inkdrop
npm ci
npx generate-palette
npm pack --dry-run
```

For shell changes, run ShellCheck when available and exercise `install.sh` or
`scripts/sync.sh` against temporary directories. Do not run installer tests
against the real home directory.

For Neovim changes, headless-load the colorscheme when Neovim is available and
verify `vim.g.colors_name` plus the required core highlight groups. Verify that
`lazy.lua` can be evaluated without bufferline.nvim installed.
