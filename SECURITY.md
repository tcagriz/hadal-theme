# Security policy

## Supported versions

Security fixes target the current `main` branch and the latest published release
of the affected Hadal package. Older package versions may remain available but
are not guaranteed to receive fixes.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability, exposed credential or
working exploit. Report it through
[private vulnerability reporting](https://github.com/tcagriz/hadal-theme/security/advisories/new)
in the `hadal-theme` source repository, including reports that affect a
standalone package mirror.

Include:

- The affected package and version.
- Operating system and application version.
- Reproduction steps and the expected security boundary.
- A minimal proof of concept, if one is safe to share.
- Observed impact and any proposed mitigation.
- Whether a credential, token or registry account may be affected.

Do not include unrelated personal data, full private configuration files or
live credentials in the report.

## Report triage

The maintainer will review the report, request missing details when needed and
coordinate a fix before public disclosure. A response-time guarantee is not
provided.

Visual inconsistencies, contrast problems, parsing errors and normal installation
failures without a security impact should use the standard bug form instead.

## Credential exposure

If a publishing or registry credential may be exposed:

1. Revoke or rotate it before continuing the investigation.
2. Review access and publication logs for unexpected use.
3. State the credential type and exposure window in the private report, but do
   not paste the credential value.
4. Leave the affected publishing workflow disabled until the maintainer has
   confirmed that the replacement is isolated in the protected `production`
   environment.
