---
description: "Run the Yandex 360 MCP server: choose which tools an agent gets, serve only reads, connect a client."
type: how-to
---

# Serve the MCP server

`ycli mcp start` serves every operation as an MCP tool over stdio. It needs the `mcp` extra
(`uv tool install 'yandex-cli[mcp]'`) and the [credentials](authenticate.md) in its environment.

## Choose the tools

Serving every tool makes `tools/list` large, and some hosts cap the number of tools (VS Code
accepts 128). Pick what the session needs:

| Flag | Serves |
|---|---|
| `--toolsets tracker,wiki` | only those services (`tracker`, `wiki`, `forms`); the default is `all` |
| `--toolsets core` | a curated everyday profile of about 40 tools: issues, comments, transitions, worklog, wiki pages and search, form reads |
| `--tools a,b` / `--exclude-tools a,b` | add or hide single tools by name; an unknown name fails at start |
| `--read-only` | no write tools; always wins over the flags above |
| `--tool-search` | a search tool and a call proxy instead of the tools, for a large set |

`status_get` is always served. To see which tools a set of flags gives without starting the
server:

```bash
ycli mcp methods --toolsets core --read-only
```

## Trust the hints

Every tool says what it does: reads carry `readOnlyHint`, writes say whether they are destructive
or idempotent. A host can auto-approve reads and ask before a destructive call. `--read-only`
removes every write, for a deployment where the agent must not change anything.

## Connect a client

Most MCP clients take a command and an environment:

```json
{
  "mcpServers": {
    "yandex-360": {
      "command": "uvx",
      "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start", "--toolsets", "core"],
      "env": {
        "YANDEX_ID_OAUTH_TOKEN": "...",
        "YANDEX_ID_ORGANIZATION_ID": "..."
      }
    }
  }
}
```

The exact file and keys for each harness are in [Install in your harness](install-in-your-harness.md).
To serve many users over HTTP, see [Self-host over HTTP](self-host-over-http.md). Every tool and
its parameters are in the [MCP tools reference](../reference/mcp/tracker.md).
