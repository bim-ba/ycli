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

## Architecture invariants (enforced)

The repo's structure is enforced by executable checks — see [`ARCHITECTURE.md`](ARCHITECTURE.md)
for the six invariants (ARCH-1..6). They are verified by `tests/test_architecture.py`,
import-linter (`uv run lint-imports`), and `tests/test_snapshots.py`. Do **not** route around
them: HTTP only in `client.py`; CLI output only via `ycli.output.render`; MCP tools read-only;
new resources via `/new-endpoint`. To change an invariant, edit `ARCHITECTURE.md` **and** its
enforcing check in the **same** PR and flag it.
