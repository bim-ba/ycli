# yandex-360 — Claude Code plugin

Skills that teach an agent to drive **Yandex 360** services (Tracker, Wiki, Forms) through
the [`ycli`](../../README.md) toolchain — its CLI, its MCP server, or its Python SDK.

## Skills

| Skill | Use for |
|-------|---------|
| `yandex-360` | Entry point — install + auth, pick a surface (CLI/MCP/SDK), route to a domain |
| `yandex-360-tracker` | Issues, epics, comments, transitions, links, worklog, changelog |
| `yandex-360-wiki` | Wiki pages, page tree, comments, attachments, YFM authoring |
| `yandex-360-forms` | Forms, questions/schema, responses, publishing |

The skills cover the read/write commands — on all three surfaces (CLI, MCP, SDK) — and,
more importantly, the real Yandex API quirks (epic-vs-parent, transition discovery,
permanent wiki slugs, the `fields=` rules, the Forms host/header traps, …).

## Install

From a marketplace that lists this plugin:

```
/plugin marketplace add <owner>/<repo>
/plugin install yandex-360@ycli
```

Or, working inside this repository, it is registered as a local marketplace in
`.claude/settings.json` (`source: "./"`), so the skills load once the repo is committed to git.

## MCP server (auto-wired)

This plugin bundles `.mcp.json`, so installing it registers the **read/write** Yandex 360
MCP server automatically — no hand-copied config. The server launches via
`uvx --from "yandex-cli[mcp]" ycli mcp start`, so you need [`uv`](https://docs.astral.sh/uv/)
on `PATH` but no global `ycli` install. It serves 240 tools (Tracker 151, Wiki 42,
Forms 46, plus `status_get`) with honest annotations: reads carry `readOnlyHint=True`,
writes declare an explicit `destructiveHint`/`idempotentHint`. Add `--read-only` to the
start command to serve only the read tools; binary downloads stay CLI/SDK-only.

## Requires

[`uv`](https://docs.astral.sh/uv/) on `PATH` (for the bundled MCP server) and two
environment variables, read from your shell: `YANDEX_ID_OAUTH_TOKEN`,
`YANDEX_ID_ORGANIZATION_ID`. The `yandex-360` skill walks through setup. For direct CLI/SDK
use, install the package with `uv add 'yandex-cli[mcp]'`.
