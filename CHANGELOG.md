# Changelog

All notable changes to this project are documented here, newest first, following
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). From v0.2.0 on, every
entry below is generated automatically by
[python-semantic-release](https://python-semantic-release.readthedocs.io/) from the
[Conventional Commits](https://www.conventionalcommits.org/) on `main` — do not edit
released sections by hand.

<!-- version list -->

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
