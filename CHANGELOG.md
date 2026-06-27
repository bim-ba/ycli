# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
From v0.1.0 on, releases are cut automatically by
[python-semantic-release](https://python-semantic-release.readthedocs.io/) from
Conventional Commits — new entries are inserted below.

<!-- version list -->

## [0.1.0] — 2026-06-27

### Added
- Initial release: Yandex 360 toolkit for **Tracker**, **Wiki**, and **Forms**.
- Four surfaces from one codebase: Typer **CLI** (`ycli` / `yandex-cli`), FastMCP **server**
  (`ycli mcp`, read-only, `[mcp]` extra), importable **Python SDK** (`ycli.yandex.*`), and a
  **Claude Code plugin** (`plugins/yandex-360/`).
- Published on PyPI as **`yandex-cli`** (`uv add yandex-cli`, or `yandex-cli[mcp]` for the server).
- Test suite at 100% coverage with `responses`-stubbed HTTP.
