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
ipm publish
```

The `publish.yml` workflow can publish unattended after adding
`INKDROP_ACCESS_KEY_ID` and `INKDROP_SECRET_ACCESS_KEY` as repository Actions
secrets. Keep the first local release manual until the credentials and registry
name are confirmed.

## License

MIT
