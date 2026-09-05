---
name: yandex-360
description: Use first for any Yandex 360 task — Yandex Tracker, Yandex Wiki, Yandex Forms, a Yandex issue key, or the `ycli` command — to set up auth, pick a surface (CLI / MCP / SDK), and route to the right domain skill.
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
Every service takes the org id in one canonical header, `X-Org-Id` (HTTP header names are
case-insensitive per RFC 9110, so casing never matters — even in raw HTTP). The clients set
it for you.

## 3. Pick a surface

| Surface | Use when | How |
|---------|----------|-----|
| **CLI** | Interactive / shell / scripting | `uv run ycli <domain> <group> <cmd>` (e.g. `uv run ycli tracker issues get KEY`) |
| **MCP server** | An LLM agent needs Yandex 360 tools | Run `ycli mcp start` (stdio; needs the `[mcp]` extra); **222 read/write tools** namespaced `tracker_*` (151), `wiki_*` (42), `forms_*` (28), plus `status_get`. `ycli mcp start --read-only` serves the reads-only view |
| **Python SDK** | Programmatic use inside Python | `from ycli.yandex.tracker.client import TrackerClient` → `TrackerClient(oauth_token=…, organization_id=…)` |

Registering the MCP server with a client (e.g. Claude Code `.mcp.json`):

```json
{
  "mcpServers": {
    "yandex": { "command": "uvx", "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"] }
  }
}
```

> **Reads vs writes on MCP:** the server is **read/write** with honest annotations.
> Reads carry `readOnlyHint=True`; writes carry `readOnlyHint=False` plus an explicit
> `destructiveHint` (`true` on delete/clear/abort-class tools) and `idempotentHint` on
> PATCH-style edits. Treat `destructiveHint=true` tools with care — prefer confirming
> with the user before calling them. For cautious deployments, `ycli mcp start
> --read-only` hides every write tool. Binary **downloads** (attachments, exports,
> keyset files) are CLI/SDK-only — MCP excludes raw-bytes output.

## 4. Route to a domain skill

| Task is about… | Load |
|----------------|------|
| Issues, epics, comments, transitions, links, worklog, changelog | **`yandex-360-tracker`** |
| Wiki pages, page tree, comments, attachments, YFM authoring | **`yandex-360-wiki`** |
| Forms, questions/schema, responses, publishing | **`yandex-360-forms`** |

Each domain skill documents its CLI commands, MCP tools, SDK client, and the API quirks
that matter for that service.

## Guardrails

- **Never hardcode the token or org id** — always read them from the environment.
- **Respect the MCP annotations** — write tools declare `readOnlyHint=False`; anything
  with `destructiveHint=true` deletes data, so confirm intent before calling it. If the
  session must not write at all, run the server with `ycli mcp start --read-only`.
- **Binary payloads stay on the CLI/SDK** — attachment/export/keyset downloads are not
  MCP tools; fetch them with `ycli … download` commands.
- **One token, three services** — the same OAuth token works for Tracker, Wiki, and Forms
  provided it carries the needed scopes (Forms needs `forms:read` / `forms:write`; MCP
  writes need the write scopes too).
