# ycli

> Baseline agent behavior is provided by spark/core (injected each session via the SessionStart hook); add only project-specific rules here.

## Project Overview

`ycli` interacts with Yandex 360 services (Tracker, Wiki, Forms; more to come) and exposes
the same SDK four ways: a Typer **CLI** (`ycli` / `yandex-cli`), a FastMCP **server**
(`ycli mcp`, optional `[mcp]` extra), an importable **Python SDK** (`ycli.yandex.*`), and a
Claude Code **plugin** under `plugins/yandex-360/`. Published on PyPI as `yandex-cli`.

- **Stack:** Python ≥3.12, managed with `uv`. `requests` + `uplink` (HTTP/SDK), `typer`
  (CLI), `fastmcp` (MCP), `pydantic` (models), `loguru` (logging).
- **Layout:** root entry points `src/ycli/cli.py` (CLI) and `src/ycli/mcp.py` (MCP); per-domain SDK
  under `src/ycli/yandex/<domain>/` (each has `client.py`, `cli.py`, `mcp.py`, models). Vendored
  Yandex API docs live in `docs/references/yandex/`. The distributable plugin (skills +
  instructions) lives in `plugins/yandex-360/`, listed by the repo-root `.claude-plugin/marketplace.json`.
- **Output:** every CLI command honors a global `--format/-o` flag (`auto` · `json` · `yaml`
  · `pretty`); rendering goes through `ycli.output.render` (ARCH-4). No output surface
  hardcodes a service UI URL (ARCH-5); a general per-model deeplink mechanism is deferred.
- **Typing:** the package ships a PEP 561 `py.typed` marker, so downstream type checkers
  see ycli's types. The MCP server is the `ycli mcp` subcommand (optional `[mcp]` extra).

## Project-Specific Conventions

- **Dependencies:** add with `uv add <pkg>` (runtime) / `uv add --dev <pkg>` (dev) — never
  hand-edit `pyproject.toml` dependency lists.
- **Tests:** `uv run pytest`. Async MCP tests rely on `asyncio_mode = "auto"`; HTTP is stubbed
  with `responses` (no live network). Mark CLI/MCP wiring tests with `@pytest.mark.integration`.
- **Auth:** clients read `YANDEX_ID_OAUTH_TOKEN` / `YANDEX_ID_ORGANIZATION_ID` from the env
  (DI via `session_from_env()`); never hardcode credentials. Header casing differs per service
  (Tracker `X-Org-ID`, Wiki/Forms `X-Org-Id`).
- **MCP server is read-only;** writes are CLI/SDK only.
- **Secrets:** `.env` and `.mcp.json` are gitignored — keep real tokens out of committed files
  (`.env.example` / `.mcp.example.json` hold placeholders).

## Release & safety

- **Auto-release on push to main.** Every push to `main` runs python-semantic-release,
  which versions from Conventional Commits and publishes to PyPI. Use `feat:` / `fix:` /
  `docs:` / `chore:` … prefixes; the squash-merge title becomes the release.
- **Never write a skip-ci token.** `[skip ci]` / `[ci skip]` / `[no ci]` / `[skip actions]` /
  `[actions skip]`, or a `skip-checks: true` commit trailer, anywhere in a commit **or
  squash-merge** message makes GitHub silently cancel the workflow run — and with it the
  release. The `git_guard` PreToolUse hook (`.claude/hooks/`) blocks all of these in the
  `git`/`gh` commit/merge command string (its one blind spot: a message passed via file,
  e.g. `git commit -F`); the `no-skip-ci` pre-commit hook additionally catches `[skip ci]` /
  `[ci skip]` written into staged file *content*; this rule covers what neither can see (a
  message typed in the GitHub UI).
- **Secrets never reach a commit.** gitleaks runs in pre-commit and CI. Credentials come
  from the env (`YANDEX_ID_OAUTH_TOKEN` / `YANDEX_ID_ORGANIZATION_ID`); the root `.env` /
  `.mcp.json` are gitignored. The one committed `.mcp.json` (the bundled plugin config)
  holds only `${VAR}` references — config and tests never embed literal values.
- **Reproducible artifacts.** Generated demos/tables come from a committed source —
  regenerate, never hand-author (the `demo.svg` incident).
- **Branch → PR → explicit approval before merge.** No direct pushes to `main`.
- **100% coverage gate.** `uv run pytest` enforces `--cov-fail-under=100`; new code ships
  with tests that keep it green.
- **New resources via `/new-endpoint`**, respecting the invariants in
  [`ARCHITECTURE.md`](ARCHITECTURE.md) and the model/naming/import conventions in
  [`docs/conventions/resources.md`](docs/conventions/resources.md). Authoring skills/commands follows
  [`docs/conventions/skills-and-commands.md`](docs/conventions/skills-and-commands.md).

## Working notes

- **Drift log:** when a session reveals a convention the codebase doesn't yet enforce, capture it via `core:creating-drift-logs` before ending.

## Architecture invariants (enforced)

The repo's structure is enforced by executable checks — see [`ARCHITECTURE.md`](ARCHITECTURE.md)
for the six invariants (ARCH-1..6). They are verified by `tests/test_architecture.py`,
import-linter (`uv run lint-imports`), and `tests/test_snapshots.py`. Do **not** route around
them: HTTP only in `client.py`; CLI output only via `ycli.output.render`; MCP tools read-only;
new resources via `/new-endpoint`. To change an invariant, edit `ARCHITECTURE.md` **and** its
enforcing check in the **same** PR and flag it.
