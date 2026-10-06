---
description: "ycli drives Yandex Tracker, Wiki, Forms and DataLens from a command line, an MCP server for AI agents and a Python SDK."
---

# ycli

--8<-- "docs/examples/services/slogan.en.md"

[Get started](tutorials/first-steps.md){ .md-button .md-button--primary }
[Connect your AI client](how-to/install-in-your-harness.md){ .md-button }

--8<-- "docs/examples/services/cards.en.md"

## From install to a working call

--8<-- "docs/examples/terminal/first-call.en.md"

`ycli auth login` signs you in through Yandex ID and saves the token. The first time it needs a Yandex OAuth app of yours: [Authenticate](how-to/authenticate.md) walks you through it.

## One operation, three ways

--8<-- "docs/examples/operations/tracker.issues.get.md"

The command, the tool an agent calls and the Python method are the same operation under the same name. Learn it once.

## What you get

<div class="grid cards" markdown>

-   :material-console: **A command line that scripts well**

    JSON when piped, ready for `jq`, `--dry-run` for every write, and an exit code for each kind of failure.

    [Script the CLI](how-to/script-the-cli.md)

-   :material-robot-outline: **An MCP server agents can trust**

    Every tool says whether it reads, writes or destroys. Serve only reads, or a small everyday set.

    [Serve the MCP server](how-to/serve-the-mcp-server.md)

-   :material-language-python: **A typed Python SDK**

    Pydantic models for every answer, and examples that the test suite runs.

    [SDK reference](reference/sdk/tracker.md)

-   :material-shield-check-outline: **Careful with your data**

    A delete asks first, a write can be previewed, and your token goes only to Yandex's own hosts.

    [Authenticate](how-to/authenticate.md)

-   :material-puzzle-outline: **Every client**

    Claude, Cursor, VS Code, Windsurf, Zed, Codex, Gemini CLI, opencode, Docker: one page, the same order for each.

    [Install in your AI client](how-to/install-in-your-harness.md)

-   :material-source-branch: **Pipelines**

    Comment on an issue after a deploy, or move it along its workflow, from GitHub Actions or GitLab CI.

    [Use in CI](how-to/use-in-ci.md)

</div>

## Where to go

| You want to | Read |
|---|---|
| try ycli for the first time | [First steps](tutorials/first-steps.md) |
| do an everyday task | [Common tasks](how-to/common-tasks.md) |
| get a token and your organization id | [Authenticate](how-to/authenticate.md) |
| connect an AI client | [Install in your AI client](how-to/install-in-your-harness.md) |
| run one server for a team | [Self-host over HTTP](how-to/self-host-over-http.md) |
| call an endpoint ycli does not wrap | [Call an unwrapped endpoint](how-to/call-an-unwrapped-endpoint.md) |
| call the API from asyncio code | [Call the API asynchronously](how-to/call-the-api-asynchronously.md) |
| look up a command, a tool, a method or a setting | [Reference](reference/configuration.md) |
| understand why ycli is built this way | [Design](explanation/design.md) |
| compare ycli with Yandex's own servers and the community ones | [ycli and the other tools](explanation/comparison.md) |

ycli is open source under the MIT license: [github.com/bim-ba/ycli](https://github.com/bim-ba/ycli).
