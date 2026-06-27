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

## Requires

The [`ycli`](../../README.md) package on `PATH` (`uv add 'yandex-cli[mcp]'`) and two environment variables:
`YANDEX_ID_OAUTH_TOKEN`, `YANDEX_ID_ORGANIZATION_ID`. The `yandex-360` skill walks through setup.
