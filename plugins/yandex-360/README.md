# yandex-360 — Claude Code plugin

Skills that teach an agent to drive **Yandex 360** services (Tracker, Wiki, Forms) through
the [`ycli`](../../README.md) toolchain — its CLI, its MCP server, or its Python SDK.

## Skills

| Skill | Use for |
|-------|---------|
| `yandex-360` | Entry point — install + auth, pick a surface (CLI/MCP/SDK), route to a domain |
| `yandex-360-tracker` | Issues, epics, comments, transitions, links, worklog, changelog |
| `yandex-360-wiki` | Wiki pages, page tree, comments, attachments, YFM authoring |
| `yandex-360-forms` | Forms, questions/schema, responses, hooks |

The skills cover the read/write commands and — more importantly — the real Yandex API
quirks (epic-vs-parent, transition discovery, permanent wiki slugs, the `fields=` rules,
the Forms host/header traps, …).

## Install

From a marketplace that lists this plugin:

```
/plugin marketplace add <owner>/<repo>
/plugin install yandex-360@ycli
```

Or, working inside this repository, it is registered as a local marketplace in
`.claude/settings.json` (`source: "./"`), so the skills load once the repo is committed to git.

## MCP server (auto-wired)

This plugin bundles `.mcp.json`, so installing it registers the **read-only** Yandex 360
MCP server automatically — no hand-copied config. The server launches via
`uvx --from "yandex-cli[mcp]" ycli mcp`, so you need [`uv`](https://docs.astral.sh/uv/)
on `PATH` but no global `ycli` install. Writes stay on the CLI/SDK; the MCP surface is
read-only.

## Requires

[`uv`](https://docs.astral.sh/uv/) on `PATH` (for the bundled MCP server) and two
environment variables, read from your shell: `YANDEX_ID_OAUTH_TOKEN`,
`YANDEX_ID_ORGANIZATION_ID`. The `yandex-360` skill walks through setup. For direct CLI/SDK
use, install the package with `uv add 'yandex-cli[mcp]'`.
