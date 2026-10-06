---
description: "ycli next to Yandex's own MCP servers and CLI and the community servers: services, tool counts, write access, install, licence. Facts with sources."
type: explanation
---

# ycli and the other tools

Several tools connect an agent or a terminal to Yandex Tracker, Wiki and Forms. This page puts their published facts side by side so you can pick the one that fits. Every figure was checked on **2026-10-03** and has its source below; a cell says "not documented" where the project's own pages do not answer.

## What each one covers

| Project | Services | MCP tools | Writes | Reads-only mode | Tools that carry read / write hints |
|---|---|---|---|---|---|
--8<-- "docs/examples/services/comparison.row.en.md"
| Yandex Tracker MCP server | Tracker | 72 | yes | not documented | 72 of 72 |
| Yandex Wiki MCP server | Wiki | 33 | yes | not documented; a token with only the `wiki:read` scope cannot write | 0 of 33 |
| Yandex Forms MCP server | Forms | 18 | yes | not documented | 0 of 18 |
| `ytracker`, the Tracker CLI | Tracker | not an MCP server | yes | not documented | not applicable |
| aikts/yandex-tracker-mcp 0.10.0 | Tracker | 55 by default, 94 with `TRACKER_ENTITIES_ENABLED` | yes | `TRACKER_READ_ONLY`, 35 tools | 55 of 55 |
| n-r-w/yandex-mcp v1.0.3 | Tracker, Wiki | 23: Tracker 18, Wiki 5 | no | always | not checked |

--8<-- "docs/examples/services/comparison.operations.en.md"

## How you get and run it

| Project | Other surfaces | Where it runs | Install | Licence | Latest release |
|---|---|---|---|---|---|
| ycli | CLI, Python SDK, Claude Code plugin | your machine (stdio), or your own server (HTTP) | `uv tool install 'yandex-cli[mcp]'`, Docker image | MIT | on every merge: see [PyPI](https://pypi.org/project/yandex-cli/#history) |
| Yandex Tracker MCP server | none documented | Yandex's server | nothing to install: a URL and two headers | no source published on its page | hosted, no versions |
| Yandex Wiki MCP server | none documented | Yandex's server | nothing to install: a URL and two headers | no source published on its page | hosted, no versions |
| Yandex Forms MCP server | none documented | Yandex's server | nothing to install: a URL and two headers | no source published on its page | hosted, no versions |
| `ytracker`, the Tracker CLI | CLI only | your machine | install script (shell, or PowerShell on Windows) | not stated on its page | not checked: not installed |
| aikts/yandex-tracker-mcp | none documented | your machine (stdio), or your own server (HTTP, with OAuth) | `uvx yandex-tracker-mcp@latest`, Docker image, `.mcpb` for Claude Desktop | Apache-2.0 | 0.10.0, 2026-09-06 |
| n-r-w/yandex-mcp | none documented | your machine | binaries, Homebrew, `go install` | MIT | v1.0.3, 2026-09-17 |

## Sources

| Project | Source | How the figure was taken |
|---|---|---|
| ycli | [README, Coverage](https://github.com/bim-ba/ycli#coverage) | generated from the code on every change, and a test keeps this page equal to it |
| Yandex Tracker MCP server | [yandex.ru/support/tracker/en/user/mcp-server](https://yandex.ru/support/tracker/en/user/mcp-server) | the page, and the server's own `tools/list` answer |
| Yandex Wiki MCP server | [yandex.ru/support/wiki/en/mcp](https://yandex.ru/support/wiki/en/mcp) | the page, and the server's own `tools/list` answer |
| Yandex Forms MCP server | [yandex.ru/support/forms/en/mcp](https://yandex.ru/support/forms/en/mcp) | the page, and the server's own `tools/list` answer |
| `ytracker` | [yandex.ru/support/tracker/en/user/cli](https://yandex.ru/support/tracker/en/user/cli) | the page only; the tool was not installed |
| aikts/yandex-tracker-mcp | [github.com/aikts/yandex-tracker-mcp](https://github.com/aikts/yandex-tracker-mcp) | the README, the GitHub release, and `tools/list` of release 0.10.0 started locally with each setting |
| n-r-w/yandex-mcp | [github.com/n-r-w/yandex-mcp](https://github.com/n-r-w/yandex-mcp) | the README and the GitHub release; the server was not run |

Yandex's servers answer `tools/list` without a token, so anyone can repeat the count:

```bash
curl -s -X POST https://mcp.tracker.yandex.net/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

The Wiki and Forms servers take the same request at `https://mcp.wiki.yandex.net` and `https://mcp.forms.yandex.net`. A tool "carries hints" when its entry has `annotations` such as `readOnlyHint` or `destructiveHint`, which a client uses to ask before a write.

Found a figure that is out of date? [Open an issue](https://github.com/bim-ba/ycli/issues/new) with the source, and the page is corrected.
