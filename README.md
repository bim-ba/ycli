# ycli

Interact with **Yandex 360** services (Wiki, Tracker, Forms, … — Mail and more to come) from
wherever you work. One codebase, many surfaces — built primarily for AI agents and MCP servers,
but useful to humans too:

- **CLI** — `uv run ycli wiki pages get <slug>`
- **MCP server** — `uv run ycli-mcp` (stdio; tools namespaced `wiki_*`, `tracker_*`, `forms_*`)
- **Python SDK** — `from ycli.yandex.tracker.client import TrackerClient`
- **Claude Code plugin** — installable skills + agent instructions (see [`plugins/yandex-360/`](plugins/yandex-360/))

## Install

```bash
uv sync
```

## Configure

Copy `.env.example` to `.env` and fill in your Yandex 360 credentials:

```bash
YANDEX_ID_OAUTH_TOKEN=...        # https://oauth.yandex.ru/
YANDEX_ID_ORGANIZATION_ID=...    # Yandex 360 admin panel
```

## Usage

```bash
# CLI
uv run ycli --help
uv run ycli tracker issues get TRACKER-1
uv run ycli wiki pages get some-slug

# MCP server (stdio) — point your MCP client at this command
uv run ycli-mcp
```

```python
# Python SDK
from ycli.yandex.tracker.client import TrackerClient

tracker = TrackerClient.from_env()
issue = tracker.issues.get("TRACKER-1")
```

## Development

```bash
uv sync
uv run pytest
```

## Layout

| Path | What |
|------|------|
| `src/ycli/cli.py` | root Typer CLI (`ycli`) |
| `src/ycli/mcp.py` | root FastMCP server (`ycli-mcp`) |
| `src/ycli/yandex/` | per-domain SDK: `tracker/`, `wiki/`, `forms/` (each has `client.py`, `cli.py`, `mcp.py`) |
| `src/ycli/log.py` | central loguru config |
| `plugins/yandex-360/` | distributable Claude Code plugin (skills + instructions) |
| `docs/references/` | vendored Yandex API reference docs |
