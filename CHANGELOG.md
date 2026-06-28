# Changelog

All notable changes to this project are documented here, newest first, following
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). From v0.2.0 on, every
entry below is generated automatically by
[python-semantic-release](https://python-semantic-release.readthedocs.io/) from the
[Conventional Commits](https://www.conventionalcommits.org/) on `main` — do not edit
released sections by hand.

<!-- version list -->

## v0.6.0 (2026-06-28)

### Build System

- Sync uv.lock project version to 0.5.0
  ([`e2f63de`](https://github.com/bim-ba/ycli/commit/e2f63de7348b9343a0c3c8e71bdd96470f72a2ce))

### Features

- Internals cleanup — env settings, transport, output strategies, multi-service auth, wiki me,
  config fixes
  ([`5d45127`](https://github.com/bim-ba/ycli/commit/5d451274f3798a85cb9061ab36af35dc9b3630a1))


## v0.5.0 (2026-06-28)

### Build System

- Sync uv.lock project version to 0.4.0
  ([`ddb8dfe`](https://github.com/bim-ba/ycli/commit/ddb8dfe40b144dc7aa54f06eb632ecf652af50ed))

### Features

- Track C — UX quick-wins (typed errors, MCP metadata, completion, tracker me, auth status, key
  links)
  ([`a19cad7`](https://github.com/bim-ba/ycli/commit/a19cad7484dc22dc8883928d8e2f3a20a3f45747))


## v0.4.0 (2026-06-27)

### Features

- Track B — AI-infra hardening (CI-skip guard, gitleaks, bundled plugin MCP, release/conventions
  docs)
  ([`5ae61ad`](https://github.com/bim-ba/ycli/commit/5ae61ad938631c76daf6202e1318bbbd6f1d5623))


## v0.3.0 (2026-06-27)

### Features

- Architecture guardrails enforcing the six ARCH invariants
  ([`6bbc381`](https://github.com/bim-ba/ycli/commit/6bbc38148a9a0b930171210351166a7cac51b128))


## v0.2.1 (2026-06-27)

### Bug Fixes

- Ship PEP 561 py.typed marker so type checkers see ycli's types
  ([`22986e4`](https://github.com/bim-ba/ycli/commit/22986e4c0992e580112e99a16f0bc1d8492eea29))

### Continuous Integration

- Re-trigger release pipeline for the pending py.typed fix
  ([`69458c1`](https://github.com/bim-ba/ycli/commit/69458c1a3b91661aa798f16eb4d86f31d9469084))


## v0.2.0 (2026-06-27)

### Continuous Integration

- Automate releases with python-semantic-release
  ([`982256e`](https://github.com/bim-ba/ycli/commit/982256e98baf3df3023ef0bfca7ffa39ae1ff617))

### Features

- Global --format/-o for CLI output (auto/json/yaml/pretty)
  ([`ccab9a3`](https://github.com/bim-ba/ycli/commit/ccab9a3ebffcde5752a2a580bce23439abf13f02))


## [0.1.0] — 2026-06-27

### Added
- Initial release: Yandex 360 toolkit for **Tracker**, **Wiki**, and **Forms**.
- Four surfaces from one codebase: Typer **CLI** (`ycli` / `yandex-cli`), FastMCP **server**
  (`ycli mcp`, read-only, `[mcp]` extra), importable **Python SDK** (`ycli.yandex.*`), and a
  **Claude Code plugin** (`plugins/yandex-360/`).
- Published on PyPI as **`yandex-cli`** (`uv add yandex-cli`, or `yandex-cli[mcp]` for the server).
- Test suite at 100% coverage with `responses`-stubbed HTTP.
