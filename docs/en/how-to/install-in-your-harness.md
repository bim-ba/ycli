---
description: "Connect the Yandex Tracker, Wiki and Forms MCP server to Claude, Cursor, VS Code, Windsurf, Zed, Codex, Gemini CLI or opencode."
type: how-to
---

# Install in your AI client

Connect ycli's MCP server to the client you already use. Every client gets the same server, named `yandex-360`, and the same two values.

## Before you start

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/): every snippet below starts the server with `uvx`, which downloads ycli on first use.
2. Get the two values (see [Authenticate](authenticate.md)):

    | Variable | What it is |
    |---|---|
    | `YANDEX_ID_OAUTH_TOKEN` | a Yandex OAuth token with Tracker, Wiki and Forms access |
    | `YANDEX_ID_ORGANIZATION_ID` | your Yandex 360 organization id |

3. A client that reads them from your environment needs them exported in the shell that starts it:

    ```bash
    export YANDEX_ID_OAUTH_TOKEN=...
    export YANDEX_ID_ORGANIZATION_ID=...
    ```

No snippet on this page stores a value: each one references a variable or asks you for it.

## Pick your client

| Client | One click | Config file | Command |
|---|---|---|---|
| [Claude Code](#claude-code) | plugin | `.mcp.json` | `claude mcp add` |
| [Claude Desktop](#claude-desktop) | `.mcpb` bundle | `claude_desktop_config.json` | |
| [Cursor](#cursor) | [install link](cursor://anysphere.cursor-deeplink/mcp/install?name=yandex-360&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyItLWZyb20iLCJ5YW5kZXgtY2xpW21jcF0iLCJ5Y2xpIiwibWNwIiwic3RhcnQiXSwiZW52Ijp7IllBTkRFWF9JRF9PQVVUSF9UT0tFTiI6IiR7ZW52OllBTkRFWF9JRF9PQVVUSF9UT0tFTn0iLCJZQU5ERVhfSURfT1JHQU5JWkFUSU9OX0lEIjoiJHtlbnY6WUFOREVYX0lEX09SR0FOSVpBVElPTl9JRH0ifX0=) | `mcp.json` | |
| [VS Code](#vs-code) | [install link](https://insiders.vscode.dev/redirect/mcp/install?name=yandex-360&inputs=%5B%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22yandex-oauth-token%22%2C%22description%22%3A%22Yandex%20OAuth%20token%22%2C%22password%22%3Atrue%7D%2C%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22yandex-organization-id%22%2C%22description%22%3A%22Yandex%20360%20organization%20id%22%7D%5D&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22yandex-cli%5Bmcp%5D%22%2C%22ycli%22%2C%22mcp%22%2C%22start%22%5D%2C%22env%22%3A%7B%22YANDEX_ID_OAUTH_TOKEN%22%3A%22%24%7Binput%3Ayandex-oauth-token%7D%22%2C%22YANDEX_ID_ORGANIZATION_ID%22%3A%22%24%7Binput%3Ayandex-organization-id%7D%22%7D%7D) | `.vscode/mcp.json` | `code --add-mcp` |
| [Windsurf (Devin Desktop)](#windsurf-devin-desktop) | | `mcp_config.json` | `devin mcp add` |
| [Zed](#zed) | | `settings.json` | |
| [Codex](#codex) | | `config.toml` | `codex mcp add` |
| [Gemini CLI](#gemini-cli) | | `settings.json` | |
| [opencode](#opencode) | | `opencode.json` | |
| [ChatGPT](#chatgpt) | | | |
| [Any other client](#any-other-client) | | the client's own | |

Prefer a container to `uv`? See [Docker](#docker). Something not working? See [If it does not work](#if-it-does-not-work).

## Claude Code

=== "One click"

    The plugin installs the server and the five skills together, pinned to the plugin's version:

    ```text
    /plugin marketplace add bim-ba/ycli
    /plugin install yandex-360@ycli
    ```

=== "Config file"

    `.mcp.json` in the project root (shared with the team; Claude Code expands `${VAR}` when it starts the server):

    ```json
    {
      "mcpServers": {
        "yandex-360": {
          "type": "stdio",
          "command": "uvx",
          "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"],
          "env": {
            "YANDEX_ID_OAUTH_TOKEN": "${YANDEX_ID_OAUTH_TOKEN}",
            "YANDEX_ID_ORGANIZATION_ID": "${YANDEX_ID_ORGANIZATION_ID}"
          }
        }
      }
    }
    ```

=== "Command"

    ```bash
    claude mcp add yandex-360 --transport stdio \
      --env YANDEX_ID_OAUTH_TOKEN='${YANDEX_ID_OAUTH_TOKEN}' \
      --env YANDEX_ID_ORGANIZATION_ID='${YANDEX_ID_ORGANIZATION_ID}' \
      -- uvx --from 'yandex-cli[mcp]' ycli mcp start
    ```

    Keep the single quotes: with double quotes your shell would put the real token into the config. Add `--scope project` to write `.mcp.json` instead of your own settings.

Check it: `claude mcp get yandex-360` shows `Connected`. *Checked with Claude Code 2.1.285 on 2026-10-03: the command and the file connect.*

## Claude Desktop

=== "One click"

    Download `yandex-360-<version>.mcpb` from the [latest release](https://github.com/bim-ba/ycli/releases/latest) and open it, or pick it in **Settings → Extensions → Advanced settings → Extension Developer → Install Extension…**. Claude Desktop asks for the token (kept in the system keychain) and the organization id.

=== "Config file"

    | System | File |
    |---|---|
    | macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
    | Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

    Claude Desktop does not read your shell's variables, so this file holds the values themselves. Prefer the bundle, which keeps the token in the keychain.

    ```json
    {
      "mcpServers": {
        "yandex-360": {
          "command": "uvx",
          "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"],
          "env": {
            "YANDEX_ID_OAUTH_TOKEN": "<your token>",
            "YANDEX_ID_ORGANIZATION_ID": "<your organization id>"
          }
        }
      }
    }
    ```

Quit Claude Desktop completely and start it again after either change. *Checked against Claude's documentation on 2026-10-03; not run.*

## Cursor

=== "One click"

    [Install in Cursor](cursor://anysphere.cursor-deeplink/mcp/install?name=yandex-360&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyItLWZyb20iLCJ5YW5kZXgtY2xpW21jcF0iLCJ5Y2xpIiwibWNwIiwic3RhcnQiXSwiZW52Ijp7IllBTkRFWF9JRF9PQVVUSF9UT0tFTiI6IiR7ZW52OllBTkRFWF9JRF9PQVVUSF9UT0tFTn0iLCJZQU5ERVhfSURfT1JHQU5JWkFUSU9OX0lEIjoiJHtlbnY6WUFOREVYX0lEX09SR0FOSVpBVElPTl9JRH0ifX0=). Some viewers block `cursor://` links: copy the link into the browser's address bar.

=== "Config file"

    `~/.cursor/mcp.json` for every project, or `.cursor/mcp.json` in one:

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

The link installs exactly the object in the file tab (base64 of it). *Checked against Cursor's documentation on 2026-10-03; not run.*

## VS Code

=== "One click"

    [Install in VS Code](https://insiders.vscode.dev/redirect/mcp/install?name=yandex-360&inputs=%5B%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22yandex-oauth-token%22%2C%22description%22%3A%22Yandex%20OAuth%20token%22%2C%22password%22%3Atrue%7D%2C%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22yandex-organization-id%22%2C%22description%22%3A%22Yandex%20360%20organization%20id%22%7D%5D&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22yandex-cli%5Bmcp%5D%22%2C%22ycli%22%2C%22mcp%22%2C%22start%22%5D%2C%22env%22%3A%7B%22YANDEX_ID_OAUTH_TOKEN%22%3A%22%24%7Binput%3Ayandex-oauth-token%7D%22%2C%22YANDEX_ID_ORGANIZATION_ID%22%3A%22%24%7Binput%3Ayandex-organization-id%7D%22%7D%7D). VS Code asks for the two values on first start and keeps the token masked.

=== "Config file"

    `.vscode/mcp.json` in the workspace (for your user profile, run **MCP: Open User Configuration**):

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

=== "Command"

    Into your user profile, with the same prompts:

    ```bash
    code --add-mcp '{"name":"yandex-360","command":"uvx","args":["--from","yandex-cli[mcp]","ycli","mcp","start"],"env":{"YANDEX_ID_OAUTH_TOKEN":"${input:yandex-oauth-token}","YANDEX_ID_ORGANIZATION_ID":"${input:yandex-organization-id}"},"inputs":[{"type":"promptString","id":"yandex-oauth-token","description":"Yandex OAuth token","password":true},{"type":"promptString","id":"yandex-organization-id","description":"Yandex 360 organization id"}]}'
    ```

VS Code sends at most 128 tools in one request, and ycli has more: start with `--toolsets core` (add `"--toolsets", "core"` to `args`), see [Serve the MCP server](serve-the-mcp-server.md). *Checked with VS Code 1.139.1 on 2026-10-03: the command writes the server and both prompts into the user profile. The link and a chat session were not run.*

## Windsurf (Devin Desktop)

Windsurf is now Devin Desktop; both of its agents read the same file.

=== "Config file"

    | System | File |
    |---|---|
    | macOS, Linux | `~/.config/devin/mcp_config.json` |
    | Windows | `%APPDATA%\devin\mcp_config.json` |

    ```json
    {
      "mcpServers": {
        "yandex-360": {
          "command": "uvx",
          "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start", "--toolsets", "core"],
          "env": {
            "YANDEX_ID_OAUTH_TOKEN": "${env:YANDEX_ID_OAUTH_TOKEN}",
            "YANDEX_ID_ORGANIZATION_ID": "${env:YANDEX_ID_ORGANIZATION_ID}"
          }
        }
      }
    }
    ```

=== "Command"

    ```bash
    devin mcp add -s user yandex-360 -- uvx --from 'yandex-cli[mcp]' ycli mcp start --toolsets core
    ```

    Then add the `env` block above to the entry it wrote.

The Cascade agent accepts 100 tools in total, which is why the snippet serves the `core` set. An older Windsurf keeps the file at `~/.codeium/windsurf/mcp_config.json`. *Checked against Devin's documentation on 2026-10-03; not run. The older path is not in the current documentation.*

## Zed

=== "Config file"

    Open the settings file (**zed: open settings file**), or add the server in **Settings → AI → MCP Servers → Add Server → Add Local Server**:

    ```json
    {
      "context_servers": {
        "yandex-360": {
          "command": "uvx",
          "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start", "--toolsets", "core"],
          "env": {
            "YANDEX_ID_OAUTH_TOKEN": "<your token>",
            "YANDEX_ID_ORGANIZATION_ID": "<your organization id>"
          }
        }
      }
    }
    ```

Zed's documentation shows no way to reference a variable here, so the file holds the values. *Checked against Zed's documentation on 2026-10-03; not run.*

## Codex

=== "Config file"

    `~/.codex/config.toml`, or `.codex/config.toml` in a trusted project. `env_vars` forwards the variables from your shell:

    ```toml
    [mcp_servers.yandex-360]
    command = "uvx"
    args = ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"]
    env_vars = ["YANDEX_ID_OAUTH_TOKEN", "YANDEX_ID_ORGANIZATION_ID"]
    startup_timeout_sec = 60   # the first uvx run downloads the package
    ```

=== "Command"

    ```bash
    codex mcp add yandex-360 -- uvx --from 'yandex-cli[mcp]' ycli mcp start
    ```

    Then add the `env_vars` and `startup_timeout_sec` lines above to the entry it wrote: `--env` would store the token itself.

Check it: `codex mcp list` shows `yandex-360` as `enabled`. Restart Codex after a change. *Checked with Codex 0.159.2 on 2026-10-03: it accepts the file, and the command writes the entry. A session was not run.*

## Gemini CLI

=== "Config file"

    `~/.gemini/settings.json`, or `.gemini/settings.json` in a project:

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

    Keep the `env` block: Gemini CLI hides inherited variables whose name contains `TOKEN` unless the server lists them.

*Checked against Gemini CLI's documentation on 2026-10-03; not run.*

## opencode

=== "Config file"

    `opencode.json` in the project, or `~/.config/opencode/opencode.json`:

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
          "timeout": 60000,
          "enabled": true
        }
      }
    }
    ```

    Keep `timeout`: opencode waits 5 seconds by default, too short for the server's start.

Check it: `opencode mcp list` shows `yandex-360` as `connected`. *Checked with opencode 2.0.20 on 2026-10-03: the file connects; without `timeout` it stayed `pending`. A session was not run.*

## ChatGPT

| Where | Works | How |
|---|---|---|
| Codex (CLI, desktop, IDE) | yes | local server, see [Codex](#codex) |
| ChatGPT on the web | with your own server | it connects only to remote HTTPS servers: see [Self-host over HTTP](self-host-over-http.md). There is no public ycli instance |

## Any other client

A client that speaks MCP over stdio needs three things, whatever its file is called: the command, its arguments and the two variables.

```json
{
  "mcpServers": {
    "yandex-360": {
      "command": "uvx",
      "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"],
      "env": {
        "YANDEX_ID_OAUTH_TOKEN": "<your token>",
        "YANDEX_ID_ORGANIZATION_ID": "<your organization id>"
      }
    }
  }
}
```

If the client limits how many tools it accepts, add `"--toolsets", "core"` to `args`. Registry-aware clients also find the server as `io.github.bim-ba/ycli` in the [official MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.bim-ba/ycli), published on every release.

## Docker

The image `ghcr.io/bim-ba/ycli` is ycli itself: with no arguments it serves MCP over stdio, with arguments it runs that command. Use it in any client instead of `uvx`; `-e NAME` without a value passes the variable from your environment:

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

As a plain CLI, with the two variables in a file:

```bash
docker run --rm --env-file .env ghcr.io/bim-ba/ycli tracker issues get TRACKER-1
docker run --rm ghcr.io/bim-ba/ycli --version
```

Tags: `<version>` for each release and `latest`; `linux/amd64` and `linux/arm64`. For pipelines see [Use in CI](use-in-ci.md). *Checked with Docker on 2026-10-03: both commands run.*

## Skills only

Without the MCP server, the five skills install into any agent that supports the [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add bim-ba/ycli/plugins/yandex-360
```

## Update or pin the version

`uvx` downloads the latest release the first time and then reuses that copy.

| You want | Write |
|---|---|
| the newest release on every start | `uvx --from 'yandex-cli[mcp]@latest' ycli mcp start` |
| one fixed version | `uvx --from 'yandex-cli[mcp]==0.90.0' ycli mcp start` |
| to refresh the copy once | `uvx --refresh-package yandex-cli --from 'yandex-cli[mcp]' ycli --version` |

## If it does not work

| Symptom | Cause and fix |
|---|---|
| The client cannot find `uvx` | An app started from the Dock or a launcher does not see your shell's `PATH`. Put the full path in `command`: `which uvx` prints it |
| Every call answers that `YANDEX_ID_OAUTH_TOKEN` or `YANDEX_ID_ORGANIZATION_ID` is not set | The client did not pass the two variables. A desktop app does not read your shell's exports: use its prompt or bundle, or write the values where its section says so |
| Nothing changes after you edit the config | Restart the client; Claude Desktop must be quit completely |
| The first start times out | The first `uvx` run downloads the package. Run `uvx --from 'yandex-cli[mcp]' ycli --version` once in a terminal, or raise the client's start timeout |
| The client rejects the server or hides tools | It limits the number of tools (VS Code 128, Cascade 100). Serve fewer: `--toolsets core`, see [Serve the MCP server](serve-the-mcp-server.md) |
| A call answers 401 or 403 | The token is wrong or lacks a permission: run `ycli doctor` with the same two values: it names the check that fails and the fix |

To see what the server does, start it by hand and read the error it prints:

```bash
uvx --from 'yandex-cli[mcp]' ycli mcp methods --toolsets core   # lists tools, needs no credentials
uvx --from 'yandex-cli[mcp]' ycli auth status                   # checks the two values
```

A command that runs these checks for you is planned: follow [#206](https://github.com/bim-ba/ycli/issues/206).
