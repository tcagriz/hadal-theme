# Hadal for Inkdrop instructions

## Mirror policy

- This repository is a synchronized mirror of the `inkdrop/` directory in
  [tcagriz/hadal-theme](https://github.com/tcagriz/hadal-theme).
- Make primary source changes in `hadal-theme/inkdrop/`, sync them with
  `scripts/sync.sh inkdrop`, and submit mirror changes through a pull request.
- Never push directly to `main`.
- Bug reports and feature requests belong in the `hadal-theme` monorepo.
  Suspected vulnerabilities must use its private vulnerability report.
- `styles/palette.css` is generated from the monorepo palette. Do not
  hand-edit it; update the source palette and regenerate through the monorepo.
- Hand-written package behavior belongs in `styles/ui.css`,
  `styles/syntax.css`, `styles/preview.css`, `package.json` or the README.

## Development rules

- Preserve Inkdrop 6 compatibility unless an issue explicitly changes the
  supported version.
- Keep the package version, changelog, package files and README consistent.
- Theme the Inkdrop UI, Markdown editor and preview together; avoid changing
  one surface without checking the others.
- Reuse shared palette roles instead of adding isolated color literals.
- Never commit Inkdrop access keys or registry credentials. Credentials must
  be scoped to the protected `production` environment.
- Preserve production approval before registry publication and do not treat
  local publishing as the normal release path.

## Validation

Run from the package root:

```sh
npm ci
npx generate-palette
python3 -m json.tool package.json > /dev/null
npm pack --dry-run
```

Before publishing, verify that the manifest version, changelog entry and
release tag agree. Review generated files after `npx generate-palette` and do
not commit unexpected output.
