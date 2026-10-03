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

## Prompts and resources

Besides tools, the server offers a few prompts and resources. A client shows a prompt as a ready request (in Claude Code, `/yandex-360:tracker_issue_brief DE-7`) and lets you attach a resource to the conversation (`@yandex-360:ycli://tracker/issue/DE-7`).

| Prompt | What it asks for |
|---|---|
| `tracker_queue_digest` | the open issues of a queue: how many, what is stuck, who holds what |
| `tracker_issue_brief` | one issue: where it stands, what was decided, what blocks it |
| `tracker_sprint_review` | a sprint of a board: what was done, what slipped |
| `wiki_page_from_issue` | a Wiki page drafted from an issue, created after you approve the draft |
| `forms_answers_table` | the answers of a form as a table, with a summary |

| Resource | Content |
|---|---|
| `ycli://tracker/issue/{key}` | the issue, as `tracker_issues_get` returns it |
| `ycli://wiki/page/{slug}` | the page's Markdown |
| `ycli://forms/survey/{survey_id}` | the form's settings, as `forms_surveys_get` returns them |
| `ycli://tracker/guide`, `ycli://wiki/guide`, `ycli://forms/guide`, `ycli://guide` | how to work with the service through these tools: the text of the plugin's skills, for a client without the plugin |

A prompt or a resource is offered only when the server serves the tools it is made of: with `--read-only` there is no `wiki_page_from_issue`, with `--toolsets wiki` no Tracker prompt. `ycli mcp methods --kind prompts` and `--kind resources` list what a server with the same flags offers. The arguments are in the [reference](../reference/mcp/prompts-and-resources.md).

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
