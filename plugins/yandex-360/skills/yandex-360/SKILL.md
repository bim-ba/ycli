---
name: yandex-360
description: Use first for any Yandex 360 task — setting up ycli (install + auth), choosing between the CLI / MCP server / Python SDK, or deciding which domain skill (Tracker, Wiki, Forms) to load. Reach for it whenever a task mentions Yandex Tracker, Wiki, Forms, a Yandex issue key, an org token, or the `ycli` command, and you have not yet configured access.
category: workflow
---

# Yandex 360 (ycli)

`ycli` talks to Yandex 360 services through one codebase exposed three ways. This skill
gets access configured and routes you to the right domain skill.

## When to use

- Before the first Yandex 360 call in a session — to set up auth and pick a surface.
- To decide **which surface** (CLI / MCP / SDK) fits the task.
- To decide **which domain skill** to load next.

## When NOT to use

- Once access is configured and you know the domain — load the domain skill directly
  (`yandex-360-tracker`, `yandex-360-wiki`, `yandex-360-forms`).

## 1. Install

`ycli` is published on PyPI as **`yandex-cli`** (managed with `uv`):

```bash
uv add yandex-cli           # into a project (CLI + SDK)
uv add 'yandex-cli[mcp]'    # …with the MCP server
# or run ad-hoc:
uvx yandex-cli --help
```

## 2. Authenticate (required before any call)

Both variables must be set in the environment:

```bash
export YANDEX_ID_OAUTH_TOKEN=...        # OAuth token — https://oauth.yandex.ru/
export YANDEX_ID_ORGANIZATION_ID=...    # Yandex 360 organization id (admin panel)
```

A missing/empty variable makes every client raise `ValueError` naming the variable.
Header casing differs per service (Tracker `X-Org-ID`, Wiki/Forms `X-Org-Id`) — the
clients handle this for you; it only matters if you fall back to raw HTTP.

## 3. Pick a surface

| Surface | Use when | How |
|---------|----------|-----|
| **CLI** | Interactive / shell / scripting | `uv run ycli <domain> <group> <cmd>` (e.g. `uv run ycli tracker issues get KEY`) |
| **MCP server** | An LLM agent needs Yandex 360 tools | Run `ycli mcp start` (stdio; needs the `[mcp]` extra); tools are namespaced `tracker_*`, `wiki_*`, `forms_*` — **reads only** |
| **Python SDK** | Programmatic use inside Python | `from ycli.yandex.tracker.client import TrackerClient` → `TrackerClient(oauth_token=…, organization_id=…)` |

Registering the MCP server with a client (e.g. Claude Code `.mcp.json`):

```json
{
  "mcpServers": {
    "yandex": { "command": "uvx", "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"] }
  }
}
```

> **Reads vs writes:** the MCP server is **read-only** by design. Writes (create/update
> issues, create/update wiki pages, form mutations) are available via the CLI and SDK only.

## 4. Route to a domain skill

| Task is about… | Load |
|----------------|------|
| Issues, epics, comments, transitions, links, worklog, changelog | **`yandex-360-tracker`** |
| Wiki pages, page tree, comments, attachments, YFM content | **`yandex-360-wiki`** |
| Forms, questions/schema, responses/answers, hooks | **`yandex-360-forms`** |

Each domain skill documents its CLI commands, MCP tools, SDK client, and the API quirks
that matter for that service.

## Guardrails

- **Never hardcode the token or org id** — always read them from the environment.
- **The MCP server is read-only** — don't expect write tools there; use the CLI/SDK.
- **One token, three services** — the same OAuth token works for Tracker, Wiki, and Forms
  provided it carries the needed scopes (Forms needs `forms:read` / `forms:write`).
