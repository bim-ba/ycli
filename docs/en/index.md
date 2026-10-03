# ycli

ycli drives Yandex 360 (**Tracker**, **Wiki** and **Forms**) from one SDK, served four ways:

| Surface | Use it when | Start here |
|---|---|---|
| CLI (`ycli`) | you work in a terminal or a script | [CLI reference](reference/cli/index.md) |
| MCP server (`ycli mcp start`) | an AI agent should read and write Yandex 360 | [Serve the MCP server](how-to/serve-the-mcp-server.md) |
| Python SDK (`ycli.yandex`) | you write Python | [SDK reference](reference/sdk/tracker.md) |
| Claude Code plugin | you use Claude Code and want the skills too | [Install in your harness](how-to/install-in-your-harness.md) |

Every operation is the same on each surface, under one name:

--8<-- "docs/examples/operations/tracker.issues.get.md"

```bash
uv tool install 'yandex-cli[mcp]'
ycli auth login
ycli tracker issues get TRACKER-1
```

## Where to go

| You want to | Read |
|---|---|
| try ycli for the first time | [First steps](tutorials/first-steps.md) |
| get a token and your organization id | [Authenticate](how-to/authenticate.md) |
| connect Claude, Cursor, VS Code, Codex or another harness | [Install in your harness](how-to/install-in-your-harness.md) |
| serve fewer tools or only reads to an agent | [Serve the MCP server](how-to/serve-the-mcp-server.md) |
| run one server for a team | [Self-host over HTTP](how-to/self-host-over-http.md) |
| use ycli in a shell script | [Script the CLI](how-to/script-the-cli.md) |
| call an endpoint ycli does not wrap | [Call an unwrapped endpoint](how-to/call-an-unwrapped-endpoint.md) |
| look up a command, a tool, a method or a setting | [Reference](reference/configuration.md) |
| understand why ycli is built this way | [Design](explanation/design.md) |

ycli is open source under the MIT license: [github.com/bim-ba/ycli](https://github.com/bim-ba/ycli).
