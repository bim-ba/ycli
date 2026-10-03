---
description: "Install ycli, sign in to Yandex 360 and read a Tracker issue from the terminal, from Python and through an AI agent."
type: tutorial
---

# First steps

In about ten minutes you install ycli, sign in to Yandex 360, read a Tracker issue from the
terminal and from Python, and let an AI agent do the same through MCP. You need
[uv](https://docs.astral.sh/uv/) and a Yandex 360 organization with Tracker.

## 1. Install

```bash
uv tool install 'yandex-cli[mcp]'
ycli --version
```

The `mcp` extra adds the MCP server; the CLI and the SDK work without it.

## 2. Sign in

Yandex hands out tokens only to a registered app, so register one first:

1. Open [oauth.yandex.ru/client/new](https://oauth.yandex.ru/client/new), create an app and grant it
   the Tracker, Wiki and Forms permissions (read and write).
2. Copy its **ClientID** and **Client secret** into a `.env` file in your working directory:

    ```bash
    YANDEX_OAUTH_CLIENT_ID=...
    YANDEX_OAUTH_CLIENT_SECRET=...
    ```

3. Run the login and follow the link it prints:

    ```bash
    ycli auth login
    ```

    ycli shows a code and a `https://ya.ru/device` link; approve there, and ycli writes your
    token and organization id into `.env`.

4. Check that every service accepts the token:

    ```bash
    ycli auth status
    ```

## 3. Read an issue from the terminal

Pick an issue key you can see in Tracker, for example `TEST-1`:

```bash
ycli tracker issues get TEST-1
ycli tracker issues get TEST-1 -o json | jq .summary
ycli --jq .summary tracker issues get TEST-1
```

At a terminal the first command prints a table; piped, ycli prints JSON. `--jq` filters the
JSON without a separate `jq`; it needs the `jq` extra (`uv tool install 'yandex-cli[jq]'`).

## 4. Read the same issue from Python

```python
from ycli.yandex.tracker.client import TrackerClient

with TrackerClient(oauth_token="...", organization_id="...") as tracker:
    issue = tracker.issues.get("TEST-1")
    print(issue.summary)
```

Use the two values `ycli auth login` wrote into `.env`. The method has the same name as the
command: `ycli tracker issues get` is `tracker.issues.get`.

## 5. Let an agent do it

Add the server to an MCP client. For Claude Code, export the two values `ycli auth login` wrote
into `.env` (`YANDEX_ID_OAUTH_TOKEN`, `YANDEX_ID_ORGANIZATION_ID`), then:

```bash
claude mcp add yandex-360 --transport stdio \
  --env YANDEX_ID_OAUTH_TOKEN='${YANDEX_ID_OAUTH_TOKEN}' \
  --env YANDEX_ID_ORGANIZATION_ID='${YANDEX_ID_ORGANIZATION_ID}' \
  -- uvx --from 'yandex-cli[mcp]' ycli mcp start
```

Ask the agent to read `TEST-1`: it calls the `tracker_issues_get` tool, the MCP name of the same
operation.

## What next

- Other harnesses: [Install in your harness](../how-to/install-in-your-harness.md).
- Give the agent fewer tools or only reads: [Serve the MCP server](../how-to/serve-the-mcp-server.md).
- Every command, tool and method: the [reference](../reference/configuration.md).
