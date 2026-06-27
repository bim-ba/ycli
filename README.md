<div align="center">

# ycli

**One Yandex 360 toolkit — four ways to use it.**
Drive **Tracker**, **Wiki**, and **Forms** from a CLI, an MCP server, a Python SDK,
or a Claude Code plugin. Built for AI agents first — pleasant for humans too.

[![CI](https://img.shields.io/github/actions/workflow/status/bim-ba/ycli/ci.yml?branch=main&style=for-the-badge)](https://github.com/bim-ba/ycli/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?style=for-the-badge)](https://github.com/bim-ba/ycli)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-compatible-7c3aed?style=for-the-badge)](https://modelcontextprotocol.io/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-d97757?style=for-the-badge)](plugins/yandex-360/)

<img src="https://raw.githubusercontent.com/bim-ba/ycli/main/docs/assets/demo.gif" alt="ycli in action" width="760">

</div>

## Why ycli

- 🧩 **One SDK, four surfaces** — write logic once, use it as a CLI, an MCP server, a Python
  library, or a Claude Code plugin.
- 🤖 **Agent-native** — the MCP server exposes read-only `tracker_*`, `wiki_*`, `forms_*`
  tools so agents explore safely; writes stay in the CLI/SDK.
- 🛡️ **Trustworthy** — typed pydantic models, the real Yandex API quirks handled for you,
  and a test suite kept at **100% coverage**.
- ⚡ **Zero-friction start** — `uv sync`, two env vars, go.

## Quick start

Pick the surface that fits how you work.

<details open>
<summary><b>CLI</b></summary>

```bash
uv sync
uv run ycli --help
uv run ycli tracker issues get TRACKER-1
uv run ycli wiki pages get onboarding
```
</details>

<details>
<summary><b>MCP server</b> (read-only)</summary>

Run it over stdio:

```bash
uv run ycli-mcp
```

Point an MCP client at it (tools are namespaced `tracker_*`, `wiki_*`, `forms_*`):

```json
{
  "mcpServers": {
    "ycli": {
      "command": "uv",
      "args": ["run", "ycli-mcp"],
      "cwd": "/path/to/ycli",
      "env": {
        "YANDEX_ID_OAUTH_TOKEN": "...",
        "YANDEX_ID_ORGANIZATION_ID": "..."
      }
    }
  }
}
```
</details>

<details>
<summary><b>Python SDK</b></summary>

```python
from ycli.yandex.tracker.client import TrackerClient

tracker = TrackerClient.from_env()
issue = tracker.issues.get("TRACKER-1")
print(issue.summary)
```
</details>

<details>
<summary><b>Claude Code plugin</b></summary>

```
/plugin marketplace add bim-ba/ycli
/plugin install yandex-360@ycli
```

Teaches an agent to drive Yandex 360 through `ycli` — including the real API quirks.
See [`plugins/yandex-360/`](plugins/yandex-360/).
</details>

## Skills (Claude Code plugin)

| Skill | Use for |
|-------|---------|
| `yandex-360` | Entry point — install + auth, pick a surface (CLI/MCP/SDK), route to a domain |
| `yandex-360-tracker` | Issues, epics, comments, transitions, links, worklog, changelog |
| `yandex-360-wiki` | Wiki pages, page tree, comments, attachments, YFM authoring |
| `yandex-360-forms` | Forms, questions/schema, responses, pagination |

The skills encode the read/write commands **and** the gnarly Yandex API quirks
(epic-vs-parent, transition discovery, permanent wiki slugs, `fields=` rules, Forms
host/header traps, answers pagination).

## What's covered

Reads ship across **SDK + CLI + MCP**; writes across **SDK + CLI** only (the MCP server is
read-only by design).

### Tracker

| Resource | Operations | SDK | CLI | MCP |
|----------|-----------|:---:|:---:|:---:|
| issues | get · full · search · list · count | ✅ | ✅ | ✅ |
| issues | create · update | ✅ | ✅ | — |
| comments | list | ✅ | ✅ | ✅ |
| comments | add | ✅ | ✅ | — |
| links | list | ✅ | ✅ | ✅ |
| links | add | ✅ | ✅ | — |
| transitions | list | ✅ | ✅ | ✅ |
| transitions | execute | ✅ | ✅ | — |
| worklog · changelog · priorities · issuetypes · linktypes | list | ✅ | ✅ | ✅ |

### Wiki

| Resource | Operations | SDK | CLI | MCP |
|----------|-----------|:---:|:---:|:---:|
| pages | get · descendants | ✅ | ✅ | ✅ |
| pages | meta (metadata-only) | — | — | ✅ |
| pages | create · update | ✅ | ✅ | — |
| comments | list | ✅ | ✅ | ✅ |
| attachments | list | ✅ | ✅ | ✅ |

### Forms (read-only today)

| Resource | Operations | SDK | CLI | MCP |
|----------|-----------|:---:|:---:|:---:|
| me | get (whoami) | ✅ | ✅ | ✅ |
| surveys | list · get | ✅ | ✅ | ✅ |
| questions | list | ✅ | ✅ | ✅ |
| answers | list (drains all pages) | ✅ | ✅ | ✅ |

> **Mail and more — coming.** See [`docs/api-coverage.md`](docs/api-coverage.md) for the full
> gap analysis and prioritized roadmap.

## Configure

```bash
cp .env.example .env
```

```bash
YANDEX_ID_OAUTH_TOKEN=...        # get one at https://oauth.yandex.ru/
YANDEX_ID_ORGANIZATION_ID=...    # from the Yandex 360 admin panel
```

Header casing differs per service (Tracker `X-Org-ID`, Wiki/Forms `X-Org-Id`) — ycli
handles it for you.

## Project layout

```text
src/ycli/
├── cli.py              # root Typer CLI  → `ycli`
├── mcp.py              # root FastMCP server → `ycli-mcp` (read-only)
├── log.py              # central loguru config
└── yandex/
    ├── tracker/        # per-domain SDK …
    ├── wiki/           #   each resource group has:
    └── forms/          #   client.py · cli.py · mcp.py · models.py
plugins/yandex-360/     # distributable Claude Code plugin (skills + instructions)
docs/references/        # vendored Yandex API reference docs
```

## Development

```bash
uv sync
uv run pytest          # 100% coverage gate; HTTP stubbed with `responses` (no live network)
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for conventions. Contributions welcome — the
[coverage roadmap](docs/api-coverage.md) is a good place to find a first issue.

## License

[MIT](LICENSE) © 2026 Sava Znatnov
