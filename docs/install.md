# Install in your harness

Every harness gets the same MCP server under the same key, `yandex-360`, with the same two
variables. Set them once in your shell (see [Configure](../README.md#configure)); no value below
contains a credential.

```bash
export YANDEX_ID_OAUTH_TOKEN=...        # Yandex OAuth token with Tracker/Wiki/Forms access
export YANDEX_ID_ORGANIZATION_ID=...    # Yandex 360 organization id
```

| Harness | How | Needs |
|---|---|---|
| [Claude Code](#claude-code) | plugin (skills + server) or `claude mcp add` | `uv` |
| [Claude Desktop](#claude-desktop) | `.mcpb` bundle from the GitHub release | `uv` |
| [Cursor](#cursor) | `mcp.json` or install link | `uv` |
| [VS Code](#vs-code) | `.vscode/mcp.json` or `code --add-mcp` | `uv` |
| [Codex CLI](#codex-cli) | `~/.codex/config.toml` | `uv` |
| [Gemini CLI](#gemini-cli) | `settings.json` | `uv` |
| [opencode](#opencode) | `opencode.jsonc` | `uv` |
| [ChatGPT](#chatgpt) | local: through Codex; web: not yet | |
| [Docker](#docker) | `ghcr.io/bim-ba/ycli` | Docker |
| [MCP Registry](#mcp-registry) | `io.github.bim-ba/ycli` | |
| [Skills only](#skills-only) | `npx skills add` | `npx` |

Every command below starts the server as `uvx --from 'yandex-cli[mcp]' ycli mcp start`: no prior
install, always the latest release. Pin it with `yandex-cli[mcp]==<version>` if you want a fixed
one. For fewer tools or a reads-only view, see the MCP section of the [README](../README.md).

## Claude Code

Plugin (the skills and the server together, pinned to the plugin's version):

```text
/plugin marketplace add bim-ba/ycli
/plugin install yandex-360@ycli
```

Server only:

```bash
claude mcp add yandex-360 --transport stdio \
  --env YANDEX_ID_OAUTH_TOKEN="$YANDEX_ID_OAUTH_TOKEN" \
  --env YANDEX_ID_ORGANIZATION_ID="$YANDEX_ID_ORGANIZATION_ID" \
  -- uvx --from 'yandex-cli[mcp]' ycli mcp start
```

## Claude Desktop

Download `yandex-360-<version>.mcpb` from the [latest release](https://github.com/bim-ba/ycli/releases/latest)
and open it. Claude Desktop asks for the token (kept in the OS keychain) and the organization id.
The bundle is a `uv`-type MCPB, so it needs `uv` on the machine and a Claude Desktop that supports
that bundle type; if yours does not, use the `uvx` command above in `claude_desktop_config.json`.

## Cursor

`~/.cursor/mcp.json` (or `.cursor/mcp.json` in a project):

```json
{
  "mcpServers": {
    "yandex-360": {
      "command": "uvx",
      "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"],
      "env": {
        "YANDEX_ID_OAUTH_TOKEN": "${env:YANDEX_ID_OAUTH_TOKEN}",
        "YANDEX_ID_ORGANIZATION_ID": "${env:YANDEX_ID_ORGANIZATION_ID}"
      }
    }
  }
}
```

One click: [install in Cursor](cursor://anysphere.cursor-deeplink/mcp/install?name=yandex-360&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyItLWZyb20iLCJ5YW5kZXgtY2xpW21jcF0iLCJ5Y2xpIiwibWNwIiwic3RhcnQiXSwiZW52Ijp7IllBTkRFWF9JRF9PQVVUSF9UT0tFTiI6IiR7ZW52OllBTkRFWF9JRF9PQVVUSF9UT0tFTn0iLCJZQU5ERVhfSURfT1JHQU5JWkFUSU9OX0lEIjoiJHtlbnY6WUFOREVYX0lEX09SR0FOSVpBVElPTl9JRH0ifX0=)
(some viewers block `cursor://` links; paste it into the browser bar). The link is the base64 of the
server object above, regenerated with:

```bash
printf '%s' '{"command":"uvx","args":["--from","yandex-cli[mcp]","ycli","mcp","start"],"env":{"YANDEX_ID_OAUTH_TOKEN":"${env:YANDEX_ID_OAUTH_TOKEN}","YANDEX_ID_ORGANIZATION_ID":"${env:YANDEX_ID_ORGANIZATION_ID}"}}' \
  | base64 -w0   # macOS: base64 -b 0; then cursor://anysphere.cursor-deeplink/mcp/install?name=yandex-360&config=<output>
```

## VS Code

`.vscode/mcp.json` (VS Code prompts for the two values and keeps the token masked):

```json
{
  "inputs": [
    { "type": "promptString", "id": "yandex-oauth-token", "description": "Yandex OAuth token", "password": true },
    { "type": "promptString", "id": "yandex-organization-id", "description": "Yandex 360 organization id" }
  ],
  "servers": {
    "yandex-360": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"],
      "env": {
        "YANDEX_ID_OAUTH_TOKEN": "${input:yandex-oauth-token}",
        "YANDEX_ID_ORGANIZATION_ID": "${input:yandex-organization-id}"
      }
    }
  }
}
```

Or into your user profile from the command line, reading the shell variables:

```bash
code --add-mcp '{"name":"yandex-360","command":"uvx","args":["--from","yandex-cli[mcp]","ycli","mcp","start"],"env":{"YANDEX_ID_OAUTH_TOKEN":"${env:YANDEX_ID_OAUTH_TOKEN}","YANDEX_ID_ORGANIZATION_ID":"${env:YANDEX_ID_ORGANIZATION_ID}"}}'
```

## Codex CLI

`~/.codex/config.toml` (or `.codex/config.toml` in a trusted project). `env_vars` forwards the
variables from your shell, so no value is stored:

```toml
[mcp_servers.yandex-360]
command = "uvx"
args = ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"]
env_vars = ["YANDEX_ID_OAUTH_TOKEN", "YANDEX_ID_ORGANIZATION_ID"]
startup_timeout_sec = 60   # the first uvx run downloads the package
```

## Gemini CLI

`~/.gemini/settings.json` (or `.gemini/settings.json` in a project):

```json
{
  "mcpServers": {
    "yandex-360": {
      "command": "uvx",
      "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"],
      "env": {
        "YANDEX_ID_OAUTH_TOKEN": "$YANDEX_ID_OAUTH_TOKEN",
        "YANDEX_ID_ORGANIZATION_ID": "$YANDEX_ID_ORGANIZATION_ID"
      }
    }
  }
}
```

## opencode

`opencode.jsonc` (project) or `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "yandex-360": {
      "type": "local",
      "command": ["uvx", "--from", "yandex-cli[mcp]", "ycli", "mcp", "start"],
      "environment": {
        "YANDEX_ID_OAUTH_TOKEN": "{env:YANDEX_ID_OAUTH_TOKEN}",
        "YANDEX_ID_ORGANIZATION_ID": "{env:YANDEX_ID_ORGANIZATION_ID}"
      },
      "enabled": true
    }
  }
}
```

## ChatGPT

| Surface | Works | Why |
|---|---|---|
| Codex (CLI, desktop, IDE) | yes | local stdio, see [Codex CLI](#codex-cli) |
| ChatGPT on the web | not yet | it connects to remote HTTPS MCP servers only; ycli serves stdio today, tracked in [#108](https://github.com/bim-ba/ycli/issues/108) |

## Docker

The image runs `ycli mcp start` over stdio. Pass the variables by name so the values stay out of
the command line:

```bash
docker run -i --rm -e YANDEX_ID_OAUTH_TOKEN -e YANDEX_ID_ORGANIZATION_ID ghcr.io/bim-ba/ycli
docker run --rm ghcr.io/bim-ba/ycli --version        # any other command works too
```

As an MCP client entry (same key as everywhere else):

```json
{
  "mcpServers": {
    "yandex-360": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "YANDEX_ID_OAUTH_TOKEN", "-e", "YANDEX_ID_ORGANIZATION_ID", "ghcr.io/bim-ba/ycli"]
    }
  }
}
```

Tags: `<version>` (one per release) and `latest`; `linux/amd64` and `linux/arm64`.

## MCP Registry

Published on every release as `io.github.bim-ba/ycli` in the
[official MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.bim-ba/ycli);
registry-aware clients list it and install the PyPI package or the Docker image from there.

## Skills only

Without the MCP server, the four user skills install into any agent that supports the
[skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add bim-ba/ycli/plugins/yandex-360
```

The path form lists exactly the four `yandex-360*` skills; the repo's own developer skills
(`arch-review`, `new-endpoint`) are marked `internal` and stay hidden.
