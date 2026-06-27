# Contributing to ycli

Thanks for helping improve **ycli**! This project wraps Yandex 360 services and exposes
them four ways (CLI, MCP server, Python SDK, Claude Code plugin) from one codebase.

## Setup

```bash
uv sync           # install runtime + dev deps
uv run pytest     # run the test suite
```

You need Python ≥ 3.12. Dependencies are managed with `uv` — add them with
`uv add <pkg>` (runtime) or `uv add --dev <pkg>`; never hand-edit `pyproject.toml`
dependency lists.

## Conventions

- **Tests:** `uv run pytest`. The suite must stay at **100% coverage** (`--cov-fail-under=100`).
  HTTP is stubbed with `responses` — no live network. Mark CLI/MCP wiring tests with
  `@pytest.mark.integration`. Async MCP tests rely on `asyncio_mode = "auto"`.
- **MCP server is read-only.** Writes live in the CLI/SDK only — never add an MCP write tool.
- **New endpoints:** ship reads across SDK + CLI + MCP; ship writes across SDK + CLI only.
  Each surface gets a test (TDD).
- **Auth:** clients read `YANDEX_ID_OAUTH_TOKEN` / `YANDEX_ID_ORGANIZATION_ID` from the
  environment. Never hardcode credentials. Header casing differs per service
  (Tracker `X-Org-ID`, Wiki/Forms `X-Org-Id`) — the transport handles this for you.
- **Secrets:** `.env` and `.mcp.json` are gitignored. Keep real tokens out of commits;
  use `.env.example` / `.mcp.example.json` placeholders.

## Layout

Per-domain SDK lives under `src/ycli/yandex/<domain>/` — each resource group has
`client.py` (uplink SDK), `cli.py` (Typer), `mcp.py` (FastMCP), `models.py` (pydantic).
The distributable Claude Code plugin is under `plugins/yandex-360/`.

See [`docs/api-coverage.md`](docs/api-coverage.md) for the current coverage gap analysis
and roadmap — a great place to find a first contribution.
