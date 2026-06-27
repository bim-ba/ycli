# Security Policy

## Reporting a vulnerability

Please report security issues **privately** — do not open a public issue.

Use GitHub's [private vulnerability reporting](https://github.com/bim-ba/ycli/security/advisories/new)
(repository **Security** tab → *Report a vulnerability*). Expect an acknowledgement
within 72 hours and a coordinated disclosure once a fix is available.

## Scope

`ycli` reads `YANDEX_ID_OAUTH_TOKEN` and `YANDEX_ID_ORGANIZATION_ID` from the
environment (`session_from_env()`) and sends them only to the official Yandex 360
API endpoints — never logged, never written to disk, never transmitted elsewhere.

In scope:

- Credential handling and accidental token/PII leakage (logs, error output, the demo shims).
- The read-only MCP boundary — the MCP server must expose **no** write tools.
- Dependency or supply-chain issues in the published `yandex-cli` distribution.

Out of scope: vulnerabilities in the Yandex 360 services themselves (report those to
Yandex), and issues that require a pre-compromised local environment.

## Supported versions

Security fixes target the latest released `0.x` line on PyPI
([`yandex-cli`](https://pypi.org/project/yandex-cli/)). Pin to a recent version and
upgrade promptly.
