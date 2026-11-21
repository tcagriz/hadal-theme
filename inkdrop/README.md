# Hadal for Inkdrop

Dark theme for Inkdrop 6, based on the VS Code Abyss color theme.

## Install

```sh
ipm install hadal
```

Then select **Hadal** in Preferences > Themes.

## Development

This package is developed inside the
[Hadal Theme Suite](https://github.com/tcagriz/hadal-theme) monorepo and mirrored here with
`git subtree split`. `styles/palette.css` is generated from the suite's
`palette/palette.json`; do not edit it by hand. Send changes to the monorepo.

## Publishing

Authenticate Inkdrop locally with `ipm configure`, then publish the package from
this repository:

```sh
npm ci
npx generate-palette
ipm publish
```

The installed `ipm` CLI does not currently run the `prepublishOnly` script, so
`npx generate-palette` must run explicitly before publishing.

The `publish.yml` workflow generates `palette.json` automatically and can publish
unattended after adding
`INKDROP_ACCESS_KEY_ID` and `INKDROP_SECRET_ACCESS_KEY` as repository Actions
secrets. The registry package name `hadal` is confirmed and available.

## License

MIT
