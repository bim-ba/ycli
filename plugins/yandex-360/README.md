# yandex-360 — Claude Code plugin

Skills that teach an agent to drive **Yandex 360** services (Tracker, Wiki, Forms) through
the [`ycli`](../../README.md) toolchain — its CLI, its MCP server, or its Python SDK.

## Skills

| Skill | Use for |
|-------|---------|
| `yandex-360` | Entry point — install + auth, pick a surface (CLI/MCP/SDK), route to a domain |
| `yandex-360-tracker` | Issues, epics, comments, transitions, links, worklog, changelog |
| `yandex-360-wiki` | Wiki pages, full-text search, page tree, page moves, revisions, backlinks, comments, attachments, page access, YFM authoring |
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
`uvx --from "yandex-cli[mcp]==<plugin version>" ycli mcp start` (pinned to the release, so a plugin update is what moves the server), so you need [`uv`](https://docs.astral.sh/uv/)
on `PATH` but no global `ycli` install. It serves the `tracker_*`, `wiki_*` and `forms_*`
tools plus `status_get` (list them with `ycli mcp methods`) with honest annotations: reads carry `readOnlyHint=True`,
writes declare an explicit `destructiveHint`/`idempotentHint`. Add `--read-only` to the
start command to serve only the read tools; binary downloads stay CLI/SDK-only.

The full set is 322 tools. A host that caps a request (VS Code: 128 tools) or a session that
only needs part of it can narrow the server with `--toolsets core` (a curated everyday
profile of about 40 tools) or a service subset such as `--toolsets tracker,wiki`; see the
[main README](../../README.md#quick-start) for every flag.

## Requires

[`uv`](https://docs.astral.sh/uv/) on `PATH` (for the bundled MCP server) and two
environment variables, read from your shell: `YANDEX_ID_OAUTH_TOKEN`,
`YANDEX_ID_ORGANIZATION_ID`. The `yandex-360` skill walks through setup. For direct CLI/SDK
use, install the package with `uv add 'yandex-cli[mcp]'`.
