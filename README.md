<!-- mcp-name: io.github.bim-ba/ycli -->
<div align="center">

# ycli

**Yandex 360 for people and for agents.**

Tracker, Wiki and Forms from a command line, an MCP server and Python: one tool, and one name for each operation everywhere.

**English** · [Русский](README.ru.md)

[![CI](https://img.shields.io/github/actions/workflow/status/bim-ba/ycli/ci.yml?branch=main&logo=githubactions&logoColor=white&label=ci)](https://github.com/bim-ba/ycli/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?logo=pytest&logoColor=white)](https://github.com/bim-ba/ycli)
[![PyPI](https://img.shields.io/pypi/v/yandex-cli?logo=pypi&logoColor=white&label=pypi)](https://pypi.org/project/yandex-cli/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey?logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-ycli.savaznatnov.dev-blue?logo=materialformkdocs&logoColor=white)](https://ycli.savaznatnov.dev/)
[![DeepWiki](https://img.shields.io/badge/deepwiki-ask%20the%20repo-blue?logo=readthedocs&logoColor=white)](https://deepwiki.com/bim-ba/ycli)

<img src="https://raw.githubusercontent.com/bim-ba/ycli/main/docs/assets/demo.gif" alt="ycli in action" width="760">

</div>

- **A command line that scripts well.** JSON when piped, a `--jq` filter, `--dry-run` for every write, an exit code for each kind of failure.
- **An MCP server agents can trust.** Every tool says whether it reads, writes or destroys; serve only reads, or a small everyday set.
- **A typed Python SDK.** Pydantic models for every answer, and examples the test suite runs.
- **Careful with your data.** A delete asks first, and your token goes only to Yandex's own hosts.

Documentation: [ycli.savaznatnov.dev](https://ycli.savaznatnov.dev/).

## Install

```bash
uv tool install 'yandex-cli[mcp]'   # the ycli command, with the MCP server
uvx yandex-cli --help               # or run it once, without installing
pipx install 'yandex-cli[mcp]'      # or with pipx
```

The command is `ycli` (also `yandex-cli`). Then sign in: `ycli auth login` ([how](https://ycli.savaznatnov.dev/how-to/authenticate/)).

Writing Python? Add the SDK to your project: `uv add yandex-cli`.

| Extra | Adds | Install |
|---|---|---|
| `mcp` | the MCP server, `ycli mcp start` | `uv tool install 'yandex-cli[mcp]'` |
| `jq` | the built-in `--jq` filter (a pipe to the `jq` program needs no extra) | `uv tool install 'yandex-cli[mcp,jq]'` |
| `service-account` | the SDK's `ServiceAccountAuth` for a Yandex Cloud service-account key | `uv add 'yandex-cli[service-account]'` |

### Connect your AI client

Every client gets the same MCP server, `uvx --from 'yandex-cli[mcp]' ycli mcp start`, and the same two variables.

| Client | Fastest way |
|---|---|
| Claude Code | `/plugin marketplace add bim-ba/ycli`, then `/plugin install yandex-360@ycli` |
| Claude Desktop | open the `.mcpb` bundle from the [latest release](https://github.com/bim-ba/ycli/releases/latest) |
| Cursor | [one-click install](https://ycli.savaznatnov.dev/how-to/install-in-your-harness/#cursor) |
| VS Code | [one-click install](https://ycli.savaznatnov.dev/how-to/install-in-your-harness/#vs-code) |
| Windsurf (Devin Desktop) | [config file](https://ycli.savaznatnov.dev/how-to/install-in-your-harness/#windsurf-devin-desktop) |
| Zed | [config file](https://ycli.savaznatnov.dev/how-to/install-in-your-harness/#zed) |
| Codex | [config file](https://ycli.savaznatnov.dev/how-to/install-in-your-harness/#codex) |
| Gemini CLI | [config file](https://ycli.savaznatnov.dev/how-to/install-in-your-harness/#gemini-cli) |
| opencode | [config file](https://ycli.savaznatnov.dev/how-to/install-in-your-harness/#opencode) |
| Any other MCP client | [three values to copy](https://ycli.savaznatnov.dev/how-to/install-in-your-harness/#any-other-client) |

Also: a Docker image, `ghcr.io/bim-ba/ycli` ([as a server or a plain CLI](https://ycli.savaznatnov.dev/how-to/install-in-your-harness/#docker)), [pipelines](https://ycli.savaznatnov.dev/how-to/use-in-ci/), and the [official MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.bim-ba/ycli) entry `io.github.bim-ba/ycli`.

Something not working? [If it does not work](https://ycli.savaznatnov.dev/how-to/install-in-your-harness/#if-it-does-not-work).

## Use it

### Command line

```bash
ycli tracker issues get TRACKER-1                  # a table at a terminal
ycli tracker issues get TRACKER-1 | jq .summary    # JSON when piped
ycli -o yaml wiki pages get onboarding             # or pick: -o json | yaml | pretty
ycli tracker boards delete 7 --dry-run             # print the request a write would send
ycli tracker boards delete 7 --yes                 # a delete asks first; --yes answers
ycli api issues/TRACKER-1 --service tracker        # an endpoint ycli does not wrap
```

More: [Script the CLI](https://ycli.savaznatnov.dev/how-to/script-the-cli/), [Call an unwrapped endpoint](https://ycli.savaznatnov.dev/how-to/call-an-unwrapped-endpoint/), the [CLI reference](https://ycli.savaznatnov.dev/reference/cli/).

### MCP server

```bash
ycli mcp start                     # every tool, reads and writes
ycli mcp start --read-only         # reads only
ycli mcp start --toolsets core     # about 40 everyday tools, for a client that caps the count
ycli mcp methods --toolsets core   # list the tool names without starting the server
```

More: [Serve the MCP server](https://ycli.savaznatnov.dev/how-to/serve-the-mcp-server/), [Self-host over HTTP](https://ycli.savaznatnov.dev/how-to/self-host-over-http/) for a team, the [tool reference](https://ycli.savaznatnov.dev/reference/mcp/tracker/).

### Python

```python
from ycli.yandex.tracker.client import TrackerClient

tracker = TrackerClient(oauth_token="…", organization_id="…")
print(tracker.issues.get("TRACKER-1").summary)
```

More: the [SDK reference](https://ycli.savaznatnov.dev/reference/sdk/tracker/).

### Claude Code plugin

```
/plugin marketplace add bim-ba/ycli
/plugin install yandex-360@ycli
```

It adds the MCP server and four skills (`yandex-360`, `yandex-360-tracker`, `yandex-360-wiki`, `yandex-360-forms`) that teach an agent the commands and the API's quirks. Source: [`plugins/yandex-360/`](plugins/yandex-360/).

## Configure

```bash
ycli auth login     # gets a token through Yandex ID, finds your organization, saves both to .env
ycli auth status    # whose token it is, and whether each service accepts it
ycli doctor         # something not working? every check in order, with the fix
```

`ycli auth login` needs a Yandex OAuth app of your own the first time: [Authenticate](https://ycli.savaznatnov.dev/how-to/authenticate/) walks you through it. ycli reads two variables, from the environment or a `.env` file:

```bash
YANDEX_ID_OAUTH_TOKEN=...        # a Yandex OAuth token with Tracker, Wiki and Forms access
YANDEX_ID_ORGANIZATION_ID=...    # your Yandex 360 organization id
```

Timeouts, retries, limits, logging and the exit codes are in the [configuration reference](https://ycli.savaznatnov.dev/reference/configuration/).

<!-- COVERAGE:START (generated by scripts/gen_coverage.py — do not edit by hand) -->
## Coverage

<img src="https://raw.githubusercontent.com/bim-ba/ycli/main/docs/assets/coverage.svg" alt="334 operations across 62 resources: Tracker 190, Wiki 58, Forms 86" width="760">

`ycli` wraps **334 operations across 62 resources** of the Tracker, Wiki, and Forms REST API. Every one is reachable from the **Python SDK** and the **CLI**, and 322 **MCP** tools serve them to agents (321 per service plus `status_get`).

> **Legend.** ✅ in **CLI** or **MCP** means the resource is reachable on that surface; MCP tools carry honest hints (reads are `readOnlyHint`, writes say whether they are destructive or idempotent), and `ycli mcp start --read-only` serves only the reads. Resource and operation names link to the official **Yandex API reference**. A ✅ says ycli wraps the operation; where it differs from what Yandex publishes is listed under [Against the published API](#against-the-published-api). Generated from the code by [`scripts/gen_coverage.py`](scripts/gen_coverage.py); do not edit by hand.

### Tracker

<details>
<summary><b>35 resources · 190 operations · 187 MCP tools</b></summary>

**Issues & work items**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [issues](https://yandex.ru/support/tracker/en/api/issues/get-issue) | [get](https://yandex.ru/support/tracker/en/api/issues/get-issue) · [search](https://yandex.ru/support/tracker/en/api/issues/search-issues) · [count](https://yandex.ru/support/tracker/en/api/issues/count-issues) · [create](https://yandex.ru/support/tracker/en/api/issues/create-issue) · [update](https://yandex.ru/support/tracker/en/api/issues/patch-issue) · [move](https://yandex.ru/support/tracker/en/api/issues/move-issue) · [suggest](https://yandex.ru/support/tracker/en/api/issues/get-suggest) · [scroll_clear](https://yandex.ru/support/tracker/en/api/issues/search-release) | ✅ | ✅ |
| [comments](https://yandex.ru/support/tracker/en/api/issues/get-comments) | [list](https://yandex.ru/support/tracker/en/api/issues/get-comments) · [get](https://yandex.ru/support/tracker/en/api/issues/get-comment) · [add](https://yandex.ru/support/tracker/en/api/issues/add-comment) · [edit](https://yandex.ru/support/tracker/en/api/issues/edit-comment) · [delete](https://yandex.ru/support/tracker/en/api/issues/delete-comment) · [react](https://yandex.ru/support/tracker/en/api/issues/add-reaction-to-comment) | ✅ | ✅ |
| [links](https://yandex.ru/support/tracker/en/api/issues/get-links) | [list](https://yandex.ru/support/tracker/en/api/issues/get-links) · [search](https://yandex.ru/support/tracker/en/api/issues/get-links-paginate) · [add](https://yandex.ru/support/tracker/en/api/issues/link-issue) · [delete](https://yandex.ru/support/tracker/en/api/issues/delete-link-issue) | ✅ | ✅ |
| [transitions](https://yandex.ru/support/tracker/en/api/issues/get-transitions) | [list](https://yandex.ru/support/tracker/en/api/issues/get-transitions) · [execute](https://yandex.ru/support/tracker/en/api/issues/new-transition) | ✅ | ✅ |
| [worklog](https://yandex.ru/support/tracker/en/api/issues/issue-worklog) | [list](https://yandex.ru/support/tracker/en/api/issues/issue-worklog) · [search](https://yandex.ru/support/tracker/en/api/issues/get-worklog) · [global_list](https://yandex.ru/support/tracker/en/api/issues/get-worklog) · [create](https://yandex.ru/support/tracker/en/api/issues/new-worklog) · [edit](https://yandex.ru/support/tracker/en/api/issues/patch-worklog) · [delete](https://yandex.ru/support/tracker/en/api/issues/delete-worklog) | ✅ | ✅ |
| [changelog](https://yandex.ru/support/tracker/en/api/issues/get-changelog) | [list](https://yandex.ru/support/tracker/en/api/issues/get-changelog) | ✅ | ✅ |
| [checklists](https://yandex.ru/support/tracker/en/api/issues/get-checklist) | [get](https://yandex.ru/support/tracker/en/api/issues/get-checklist) · [create](https://yandex.ru/support/tracker/en/api/issues/add-checklist-item) · [edit](https://yandex.ru/support/tracker/en/api/issues/edit-checklist) · [delete](https://yandex.ru/support/tracker/en/api/issues/delete-checklist-item) · [clear](https://yandex.ru/support/tracker/en/api/issues/delete-checklist) | ✅ | ✅ |
| [attachments](https://yandex.ru/support/tracker/en/api/issues/get-attachments-list) | [list](https://yandex.ru/support/tracker/en/api/issues/get-attachments-list) · [download](https://yandex.ru/support/tracker/en/api/issues/get-attachment) · [download_thumbnail](https://yandex.ru/support/tracker/en/api/issues/get-attachment-preview) · [get](https://yandex.ru/support/tracker/en/api/issues/get-attachment-info) · [delete](https://yandex.ru/support/tracker/en/api/issues/delete-attachment) · [upload](https://yandex.ru/support/tracker/en/api/issues/post-attachment) · [upload_temp](https://yandex.ru/support/tracker/en/api/issues/temp-attachment) | ✅ | ✅ |
| [remotelinks](https://yandex.ru/support/tracker/en/api/issues/get-external-links) | [list](https://yandex.ru/support/tracker/en/api/issues/get-external-links) · [create](https://yandex.ru/support/tracker/en/api/issues/add-external-link) · [delete](https://yandex.ru/support/tracker/en/api/issues/delete-external-link) | ✅ | ✅ |

**Agile boards**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [boards](https://yandex.ru/support/tracker/en/api/boards/get-boards) | [list](https://yandex.ru/support/tracker/en/api/boards/get-boards) · [get](https://yandex.ru/support/tracker/en/api/boards/get-board) · [create](https://yandex.ru/support/tracker/en/api/boards/post-board) · [edit](https://yandex.ru/support/tracker/en/api/boards/patch-board) · [delete](https://yandex.ru/support/tracker/en/api/boards/delete-board) | ✅ | ✅ |
| [sprints](https://yandex.ru/support/tracker/en/api/boards/get-sprints) | [list](https://yandex.ru/support/tracker/en/api/boards/get-sprints) · [get](https://yandex.ru/support/tracker/en/api/boards/get-sprint) · [create](https://yandex.ru/support/tracker/en/api/boards/post-sprint) · [edit](https://yandex.ru/support/tracker/en/api/boards/patch-sprint) · [delete](https://yandex.ru/support/tracker/en/api/boards/delete-sprint) · [start](https://yandex.ru/support/tracker/en/api/boards/start-sprint) · [archive](https://yandex.ru/support/tracker/en/api/boards/archive-sprint) | ✅ | ✅ |
| [columns](https://yandex.ru/support/tracker/en/api/boards/get-columns) | [list](https://yandex.ru/support/tracker/en/api/boards/get-columns) · [get](https://yandex.ru/support/tracker/en/api/boards/get-column) · [create](https://yandex.ru/support/tracker/en/api/boards/post-column) · [edit](https://yandex.ru/support/tracker/en/api/boards/patch-column) · [delete](https://yandex.ru/support/tracker/en/api/boards/delete-column) | ✅ | ✅ |

**Dictionaries**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [priorities](https://yandex.ru/support/tracker/en/api/admin/get-priorities) | [list](https://yandex.ru/support/tracker/en/api/admin/get-priorities) · [create](https://yandex.ru/support/tracker/en/api/admin/create-priority) · [edit](https://yandex.ru/support/tracker/en/api/admin/patch-priority) | ✅ | ✅ |
| [statuses](https://yandex.ru/support/tracker/en/api/admin/get-statuses) | [list](https://yandex.ru/support/tracker/en/api/admin/get-statuses) · [create](https://yandex.ru/support/tracker/en/api/admin/create-status) · [edit](https://yandex.ru/support/tracker/en/api/admin/patch-status) | ✅ | ✅ |
| [resolutions](https://yandex.ru/support/tracker/en/api/admin/get-resolutions) | [list](https://yandex.ru/support/tracker/en/api/admin/get-resolutions) · [create](https://yandex.ru/support/tracker/en/api/admin/create-resolution) · [edit](https://yandex.ru/support/tracker/en/api/admin/patch-resolution) | ✅ | ✅ |
| [issuetypes](https://yandex.ru/support/tracker/en/api/admin/get-issue-types) | [list](https://yandex.ru/support/tracker/en/api/admin/get-issue-types) · [create](https://yandex.ru/support/tracker/en/api/admin/create-issue-type) · [edit](https://yandex.ru/support/tracker/en/api/admin/patch-issue-type) | ✅ | ✅ |
| linktypes | list | ✅ | ✅ |

**Fields, queues & structure**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [fields](https://yandex.ru/support/tracker/en/api/issues/get-global-fields) | [list](https://yandex.ru/support/tracker/en/api/issues/get-global-fields) · [get](https://yandex.ru/support/tracker/en/api/issues/get-issue-fields) · [create](https://yandex.ru/support/tracker/en/api/issues/create-field) · [edit](https://yandex.ru/support/tracker/en/api/issues/patch-issue-field-name) · [category_create](https://yandex.ru/support/tracker/en/api/issues/create-issue-field-category) · [category_edit](https://yandex.ru/support/tracker/en/api/issues/patch-issue-field-category) | ✅ | ✅ |
| [localfields](https://yandex.ru/support/tracker/en/api/queues/get-local-fields) | [list](https://yandex.ru/support/tracker/en/api/queues/get-local-fields) · [get](https://yandex.ru/support/tracker/en/api/queues/get-info-local-field) · [create](https://yandex.ru/support/tracker/en/api/queues/create-local-field) · [edit](https://yandex.ru/support/tracker/en/api/queues/edit-local-field) | ✅ | ✅ |
| [components](https://yandex.ru/support/tracker/en/api/queues/get-components) | [list](https://yandex.ru/support/tracker/en/api/queues/get-components) · [create](https://yandex.ru/support/tracker/en/api/queues/post-component) · [edit](https://yandex.ru/support/tracker/en/api/queues/patch-component) · [list_for_queue](https://yandex.ru/support/tracker/en/api/queues/get-queue-components) · [get](https://yandex.ru/support/tracker/en/api/queues/get-component) · [delete](https://yandex.ru/support/tracker/en/api/queues/delete-component) · [user_permissions](https://yandex.ru/support/tracker/en/api/queues/get-component-user-access) · [group_permissions](https://yandex.ru/support/tracker/en/api/queues/get-component-group-access) | ✅ | ✅ |
| [queues](https://yandex.ru/support/tracker/en/api/queues/get-queues) | [list](https://yandex.ru/support/tracker/en/api/queues/get-queues) · [get](https://yandex.ru/support/tracker/en/api/queues/get-queue) · [tags](https://yandex.ru/support/tracker/en/api/queues/get-tags) · [versions](https://yandex.ru/support/tracker/en/api/queues/get-versions) · [fields](https://yandex.ru/support/tracker/en/api/queues/get-fields) · [create](https://yandex.ru/support/tracker/en/api/queues/create-queue) · [delete](https://yandex.ru/support/tracker/en/api/queues/delete-queue) · [restore](https://yandex.ru/support/tracker/en/api/queues/restore-queue) · [set_permissions](https://yandex.ru/support/tracker/en/api/queues/manage-access) · [tag_remove](https://yandex.ru/support/tracker/en/api/queues/delete-tag) · [version_create](https://yandex.ru/support/tracker/en/api/queues/create-version) · [version_get](https://yandex.ru/support/tracker/en/api/queues/get-version) · [version_edit](https://yandex.ru/support/tracker/en/api/queues/update-version) · [version_delete](https://yandex.ru/support/tracker/en/api/queues/delete-version) · [user_permissions](https://yandex.ru/support/tracker/en/api/queues/get-user-access) · [group_permissions](https://yandex.ru/support/tracker/en/api/queues/get-group-access) | ✅ | ✅ |
| [workflows](https://yandex.ru/support/tracker/en/api/queues/workflows/get-workflows) | [list](https://yandex.ru/support/tracker/en/api/queues/workflows/get-workflows) · [get](https://yandex.ru/support/tracker/en/api/queues/workflows/get-workflow) · [for_queue](https://yandex.ru/support/tracker/en/api/queues/workflows/get-queue-workflows) · [create](https://yandex.ru/support/tracker/en/api/queues/workflows/post-workflow) · [edit](https://yandex.ru/support/tracker/en/api/queues/workflows/patch-workflow) · [edit_action](https://yandex.ru/support/tracker/en/api/queues/workflows/patch-workflow-action) · [delete](https://yandex.ru/support/tracker/en/api/queues/workflows/delete-workflow) | ✅ | ✅ |
| [projects](https://yandex.ru/support/tracker/en/api/projects/get-projects) | [list](https://yandex.ru/support/tracker/en/api/projects/get-projects) · [get](https://yandex.ru/support/tracker/en/api/projects/get-project) · [queues](https://yandex.ru/support/tracker/en/api/projects/get-project-queues) · [create](https://yandex.ru/support/tracker/en/api/projects/create-project) · [edit](https://yandex.ru/support/tracker/en/api/projects/update-project) · [delete](https://yandex.ru/support/tracker/en/api/projects/delete-project) | ✅ | ✅ |

**Automation & bulk**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [macros](https://yandex.ru/support/tracker/en/api/get-macroses) | [list](https://yandex.ru/support/tracker/en/api/get-macroses) · [get](https://yandex.ru/support/tracker/en/api/get-macros) · [create](https://yandex.ru/support/tracker/en/api/post-macros) · [edit](https://yandex.ru/support/tracker/en/api/patch-macros) · [delete](https://yandex.ru/support/tracker/en/api/delete-macros) | ✅ | ✅ |
| [triggers](https://yandex.ru/support/tracker/en/api/queues/get-trigger) | [list](https://yandex.ru/support/tracker/en/api/queues/get-triggers) · [get](https://yandex.ru/support/tracker/en/api/queues/get-trigger) · [create](https://yandex.ru/support/tracker/en/api/queues/create-trigger) · [edit](https://yandex.ru/support/tracker/en/api/queues/change-trigger) · [webhook_log](https://yandex.ru/support/tracker/en/api/queues/view-trigger-logs) | ✅ | ✅ |
| [autoactions](https://yandex.ru/support/tracker/en/api/queues/get-autoaction) | [get](https://yandex.ru/support/tracker/en/api/queues/get-autoaction) · [create](https://yandex.ru/support/tracker/en/api/queues/create-autoaction) · [logs](https://yandex.ru/support/tracker/en/api/queues/view-autoaction-logs) · [log_detail](https://yandex.ru/support/tracker/en/api/queues/view-autoaction-logs) | ✅ | ✅ |
| [dashboards](https://yandex.ru/support/tracker/en/api/dashboards/create-dashboard) | [create](https://yandex.ru/support/tracker/en/api/dashboards/create-dashboard) · [add_cycle_time_widget](https://yandex.ru/support/tracker/en/api/dashboards/create-widget) | ✅ | ✅ |
| [bulk](https://yandex.ru/support/tracker/en/api/bulkchange/bulk-update-issues) | [update](https://yandex.ru/support/tracker/en/api/bulkchange/bulk-update-issues) · [move](https://yandex.ru/support/tracker/en/api/bulkchange/bulk-move-issues) · [transition](https://yandex.ru/support/tracker/en/api/bulkchange/bulk-transition) · [get](https://yandex.ru/support/tracker/en/api/bulkchange/bulk-move-info) · [issues](https://yandex.ru/support/tracker/en/api/bulkchange/bulk-move-info) | ✅ | ✅ |
| [import](https://yandex.ru/support/tracker/en/api/import/import-ticket) | [task](https://yandex.ru/support/tracker/en/api/import/import-ticket) · [comment](https://yandex.ru/support/tracker/en/api/import/import-comments) · [link](https://yandex.ru/support/tracker/en/api/import/import-links) · [worklog](https://yandex.ru/support/tracker/en/api/import/import-worklogs) · [file](https://yandex.ru/support/tracker/en/api/import/import-attachments) · [comment_file](https://yandex.ru/support/tracker/en/api/import/import-attachments) | ✅ | ✅ |

**Entities, users & search**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [entities](https://yandex.ru/support/tracker/en/api/entities/about-entities) | [create](https://yandex.ru/support/tracker/en/api/entities/create-entity) · [get](https://yandex.ru/support/tracker/en/api/entities/get-entity) · [edit](https://yandex.ru/support/tracker/en/api/entities/update-entity) · [delete](https://yandex.ru/support/tracker/en/api/entities/delete-entity) · [search](https://yandex.ru/support/tracker/en/api/entities/search-entities) · [history](https://yandex.ru/support/tracker/en/api/entities/get-events-relative) · [permissions](https://yandex.ru/support/tracker/en/api/entities/get-access) · [set_permissions](https://yandex.ru/support/tracker/en/api/entities/patch-access) · [direct_permissions](https://yandex.ru/support/tracker/en/api/entities/get-permissions) · [set_direct_permissions](https://yandex.ru/support/tracker/en/api/entities/patch-permissions) · [bulk_update](https://yandex.ru/support/tracker/en/api/entities/bulkchange-entities) · [bulk_status](https://yandex.ru/support/tracker/en/api/entities/bulkchange-entities) · [create_report](https://yandex.ru/support/tracker/en/api/entities/about-entities) · [comments_list](https://yandex.ru/support/tracker/en/api/entities/comments/get-all-comments) · [comments_relative](https://yandex.ru/support/tracker/en/api/entities/comments/get-all-comments) · [comments_get](https://yandex.ru/support/tracker/en/api/entities/comments/get-comment) · [comments_create](https://yandex.ru/support/tracker/en/api/entities/comments/add-comment) · [comments_edit](https://yandex.ru/support/tracker/en/api/entities/comments/patch-comment) · [comments_delete](https://yandex.ru/support/tracker/en/api/entities/comments/delete-comment) · [checklists_create](https://yandex.ru/support/tracker/en/api/entities/checklists/add-checklist) · [checklists_edit](https://yandex.ru/support/tracker/en/api/entities/checklists/patch-checklist) · [checklists_edit_item](https://yandex.ru/support/tracker/en/api/entities/checklists/patch-checklist-item) · [checklists_delete](https://yandex.ru/support/tracker/en/api/entities/checklists/delete-checklist) · [checklists_delete_item](https://yandex.ru/support/tracker/en/api/entities/checklists/delete-checklist-item) · [checklists_move](https://yandex.ru/support/tracker/en/api/entities/checklists/move-checklist-item) · [links_list](https://yandex.ru/support/tracker/en/api/entities/links/get-links) · [links_create](https://yandex.ru/support/tracker/en/api/entities/links/add-links) · [links_delete](https://yandex.ru/support/tracker/en/api/entities/links/delete-link) · [attachments_list](https://yandex.ru/support/tracker/en/api/entities/attachments/get-all-attachments) · [attachments_get](https://yandex.ru/support/tracker/en/api/entities/attachments/get-attachment) · [attachment_download](https://yandex.ru/support/tracker/en/api/entities/about-entities) · [attachments_attach](https://yandex.ru/support/tracker/en/api/entities/attachments/add-attachment) · [attachments_delete](https://yandex.ru/support/tracker/en/api/entities/attachments/delete-attachment) | ✅ | ✅ |
| [users](https://yandex.ru/support/tracker/en/api/users/get-users) | [get](https://yandex.ru/support/tracker/en/api/users/get-user) · [list](https://yandex.ru/support/tracker/en/api/users/get-users) | ✅ | ✅ |
| [applications](https://yandex.ru/support/tracker/en/api/issues/get-applications) | [list](https://yandex.ru/support/tracker/en/api/issues/get-applications) | ✅ | ✅ |
| [filters](https://yandex.ru/support/tracker/en/api/filters/get-filter) | [get](https://yandex.ru/support/tracker/en/api/filters/get-filter) · [create](https://yandex.ru/support/tracker/en/api/filters/create-filter) · [edit](https://yandex.ru/support/tracker/en/api/filters/update-filter) · [delete](https://yandex.ru/support/tracker/en/api/filters/delete-filter) | ✅ | ✅ |
| [gaps](https://yandex.ru/support/tracker/en/api/gaps/post-gaps) | [create](https://yandex.ru/support/tracker/en/api/gaps/post-gaps) · [search](https://yandex.ru/support/tracker/en/api/gaps/search-gaps) · [delete](https://yandex.ru/support/tracker/en/api/gaps/delete-gaps) | ✅ | ✅ |
| [me](https://yandex.ru/support/tracker/en/api/users/get-user-info) | [get](https://yandex.ru/support/tracker/en/api/users/get-user-info) | ✅ | ✅ |

</details>

### Wiki

<details>
<summary><b>11 resources · 58 operations · 56 MCP tools</b></summary>

**Pages**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [pages](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) | [get_by_id](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details_by_id) · [get](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) · [descendants](https://yandex.ru/support/wiki/en/api-ref/pages/pages__descendants_by_slug) · [descendants_by_id](https://yandex.ru/support/wiki/en/api-ref/pages/pages__descendants_by_id) · [grids](https://yandex.ru/support/wiki/en/api-ref/pages/pages__page_grids) · [create](https://yandex.ru/support/wiki/en/api-ref/pages/pages__create_page) · [update](https://yandex.ru/support/wiki/en/api-ref/pages/pages__update_page_details) · [delete](https://yandex.ru/support/wiki/en/api-ref/pages/pages__delete_page) · [append_content](https://yandex.ru/support/wiki/en/api-ref/pages/pages__append_content) · [clone](https://yandex.ru/support/wiki/en/api-ref/pages/pages__clone_page) · [move](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) · [revisions](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) · [backlinks](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) | ✅ | ✅ |
| [resources](https://yandex.ru/support/wiki/en/api-ref/pagesresources/pagesresources__resources) | [list](https://yandex.ru/support/wiki/en/api-ref/pagesresources/pagesresources__resources) | ✅ | ✅ |
| [recovery](https://yandex.ru/support/wiki/en/api-ref/recovery_tokens/recovery_tokens__recover_page_by_token) | [restore](https://yandex.ru/support/wiki/en/api-ref/recovery_tokens/recovery_tokens__recover_page_by_token) | ✅ | ✅ |
| [search](https://yandex.ru/support/wiki/en/api-ref/search/search__search) | [query](https://yandex.ru/support/wiki/en/api-ref/search/search__search) | ✅ | ✅ |

**Collaboration**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [comments](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__comments) | [list](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__comments) · [thread](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__thread_comments) · [thread_get](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__thread_comments) · [create](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__create_comment) · [delete](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__delete_comment) | ✅ | ✅ |
| [attachments](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) | [list](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) · [get](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) · [preview](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) · [download](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__download_by_file_id) · [download_by_url](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__download_by_filename_slug_pair) · [delete](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__delete_attach) · [attach](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attach_file) · [upload](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) | ✅ | ✅ |
| [access](https://yandex.ru/support/wiki/en/api-ref/pages_access/pagesaccess__create_page_access) | [create](https://yandex.ru/support/wiki/en/api-ref/pages_access/pagesaccess__create_page_access) · [update](https://yandex.ru/support/wiki/en/api-ref/pages_access/pagesaccess__update_page_access) · [delete](https://yandex.ru/support/wiki/en/api-ref/pages_access/pagesaccess__delete_page_access) · [clear](https://yandex.ru/support/wiki/en/api-ref/pages_access/pagesaccess__delete_page_accesses) | ✅ | ✅ |

**Grids (dynamic tables)**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [grids](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) | [get](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) · [create](https://yandex.ru/support/wiki/en/api-ref/grids/grids__create_grid) · [update](https://yandex.ru/support/wiki/en/api-ref/grids/grids__update_grid) · [delete](https://yandex.ru/support/wiki/en/api-ref/grids/grids__delete_grid) · [add_rows](https://yandex.ru/support/wiki/en/api-ref/grids/grids__add_rows) · [remove_rows](https://yandex.ru/support/wiki/en/api-ref/grids/grids__remove_rows) · [move_rows](https://yandex.ru/support/wiki/en/api-ref/grids/grids__move_rows) · [add_columns](https://yandex.ru/support/wiki/en/api-ref/grids/grids__add_columns) · [remove_columns](https://yandex.ru/support/wiki/en/api-ref/grids/grids__remove_columns) · [move_columns](https://yandex.ru/support/wiki/en/api-ref/grids/grids__move_columns) · [update_cells](https://yandex.ru/support/wiki/en/api-ref/grids/grids__update_cells) · [clone](https://yandex.ru/support/wiki/en/api-ref/grids/grids__clone_grid) · [suggest_column](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) · [update_column](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) · [update_row](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) | ✅ | ✅ |

**Async & uploads**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [operations](https://yandex.ru/support/wiki/en/api-ref/operations/operations__get_clone_operation_status) | [clone_get](https://yandex.ru/support/wiki/en/api-ref/operations/operations__get_clone_operation_status) · [gridclone_get](https://yandex.ru/support/wiki/en/api-ref/operations/operations__get_clone_inline_grid_operation_status) · [move_get](https://yandex.ru/support/wiki/en/api-ref/operations/operations__get_clone_operation_status) | ✅ | ✅ |
| [uploadsessions](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__create_upload_session) | [create](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__create_upload_session) · [get](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__get_upload_session) · [upload_part](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__upload_part) · [finish](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__complete_multipart_upload) · [abort](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__abort_multipart_upload) · [abort_all](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__abort_all) | ✅ | ✅ |

**Identity**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [me](https://yandex.ru/support/wiki/en/api-ref/users/users__me) | [get](https://yandex.ru/support/wiki/en/api-ref/users/users__me) | ✅ | ✅ |

</details>

### Forms

<details>
<summary><b>16 resources · 86 operations · 78 MCP tools</b></summary>

**Surveys & questions**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [surveys](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_surveys_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_surveys_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_survey_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_create_survey_public_view) · [modify](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_delete_survey_public_view) · [publish](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_publish_survey_public_view) · [unpublish](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_unpublish_survey_public_view) | ✅ | ✅ |
| [questions](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_get_questions_public_view) | [get](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_get_question_public_view) · [list](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_get_questions_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_create_question_public_view) · [modify](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_modify_question_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_delete_question_public_view) · [move](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_move_question_public_view) | ✅ | ✅ |
| [conditions](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_question_conditions_public_view) | [question_list](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_question_conditions_public_view) · [question_get](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_question_condition_public_view) · [question_create](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_create_question_condition_public_view) · [question_modify](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_modify_question_condition_public_view) · [question_delete](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_delete_question_condition_public_view) · [question_set_operator](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_patch_question_conditions_operator_public_view) · [page_list](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_page_conditions_public_view) · [page_get](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_page_condition_public_view) · [page_create](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_create_page_condition_public_view) · [page_modify](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_modify_page_condition_public_view) · [page_delete](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_delete_page_condition_public_view) · [page_set_operator](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_patch_page_conditions_operator_public_view) · [submit_list](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_submit_conditions_public_view) · [submit_get](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_submit_condition_public_view) · [submit_create](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_create_submit_condition_public_view) · [submit_modify](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_modify_submit_condition_public_view) · [submit_delete](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_delete_submit_condition_public_view) · [submit_set_operator](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_patch_submit_conditions_operator_public_view) · [hook_list](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_get_hook_conditions_public_view) · [hook_get](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_get_hook_condition_public_view) · [hook_create](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_create_hook_condition_public_view) · [hook_modify](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_modify_hook_condition_public_view) · [hook_delete](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_delete_hook_condition_public_view) · [hook_set_operator](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_patch_hook_conditions_operator_public_view) | ✅ | ✅ |
| [access](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_permissions_get_access_public_view) | [get](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_permissions_get_access_public_view) · [set](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_permissions_update_access_public_view) · [grant](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_permissions_grant_access_public_view) · [revoke](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_permissions_revoke_access_public_view) | ✅ | ✅ |
| [history](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_survey_history_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_survey_history_public_view) | ✅ | ✅ |

**Responses & export**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [answers](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) | [get](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answer_public_view) · [list](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) · [list_all](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) · [export](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_export_answers_public_view) · [export_results](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_export_answers_results_public_view) · [download_export](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_export_answers_results_public_view) · [integrations_list](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_answers_get_integrations_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) · [restore](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) | ✅ | ✅ |
| [operations](https://yandex.ru/support/forms/en/api-ref/operations/events_v1_views_operations_get_operation_view) | [get](https://yandex.ru/support/forms/en/api-ref/operations/events_v1_views_operations_get_operation_view) | ✅ | ✅ |

**Integrations**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [hooks](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_get_hooks_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_get_hooks_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_get_hook_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_create_hook_public_view) · [modify](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_modify_hook_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_delete_hook_public_view) | ✅ | ✅ |
| [subscriptions](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_get_subscriptions_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_get_subscriptions_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_get_subscription_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_create_subscription_public_view) · [modify](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_modify_subscription_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_delete_subscription_public_view) · [attach](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_save_subscription_attachment_public_view) | ✅ | ✅ |
| [variables](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_get_variables_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_get_variables_public_view) | ✅ | ✅ |
| [notifications](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_get_notifications_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_get_notifications_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_get_notification_public_view) · [status_get](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_get_notification_status_public_view) · [restart](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_restart_notification_public_view) · [cancel](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_cancel_notification_public_view) · [errors_list](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_surveys_get_visible_errors_public_view) | ✅ | ✅ |

**Distribution**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [keysets](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_get_keysets_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_get_keysets_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_get_keyset_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_create_keyset_public_view) · [modify](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_modify_keyset_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_delete_keyset_public_view) · [download](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_download_keyset_public_view) | ✅ | ✅ |
| [filling](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view) | [get](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view) · [submit](https://yandex.ru/support/forms/en/api-ref/filling/events_b2b_v1_views_surveys_submit_form_public_view) · [suggest](https://yandex.ru/support/forms/en/api-ref/filling/events_b2b_v1_views_surveys_get_suggest_public_view) | ✅ | ✅ |

**Media**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [files](https://yandex.ru/support/forms/en/api-ref/files/events_b2b_v1_views_files_get_file_public_view) | [upload](https://yandex.ru/support/forms/en/api-ref/files/events_b2b_v1_views_surveys_save_survey_file_public_view) · [verify](https://yandex.ru/support/forms/en/api-ref/files/events_b2b_v1_views_surveys_verify_file_public_view) · [download](https://yandex.ru/support/forms/en/api-ref/files/events_b2b_v1_views_files_get_file_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/files/events_b2b_v1_views_files_delete_file_public_view) | ✅ | ✅ |
| [images](https://yandex.ru/support/forms/en/api-ref/images/events_b2b_v1_views_surveys_create_image_public_view) | [upload](https://yandex.ru/support/forms/en/api-ref/images/events_b2b_v1_views_surveys_create_image_public_view) · [clone](https://yandex.ru/support/forms/en/api-ref/images/events_b2b_v1_views_surveys_create_image_public_view) | ✅ | ✅ |

**Identity**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [me](https://yandex.ru/support/forms/en/api-ref/users/events_v1_views_users_get_user_view) | [get](https://yandex.ru/support/forms/en/api-ref/users/events_v1_views_users_get_user_view) | ✅ | ✅ |

</details>

Every resource and operation above deep-links to the Yandex API reference: 318 of 334 operations resolve to their own endpoint page and 15 to their resource's page. No public API reference exists yet for `tracker.linktypes`, `tracker.linktypes.list`, shown as plain text. See `CONTRIBUTING.md` for the intentional exclusions (UI-only endpoints with no public REST API) and per-method notes.

### Against the published API

What ycli sends, replayed from its contract tests, compared with what Yandex publishes: the Wiki and Forms OpenAPI documents and Tracker's API reference (prose, so only operations and the query parameters a page lists are compared). A request body is compared only where ycli has a typed model for it and the model is closed; the **Bodies compared** column says how many that is, so an empty list is not read as a match. The published side is the snapshot in [`scripts/api_snapshot/`](scripts/api_snapshot); a [weekly job](.github/workflows/api-drift.yml) fetches it again and opens an issue when Yandex has changed it.

| Service | Published | Wrapped | Not wrapped | Operations that differ | Bodies compared | Source |
|---------|:---------:|:-------:|:-----------:|:----------------------:|:---------------:|--------|
| Tracker | 190 | 188 | 0 (+2 on purpose) | 25 | — | [API reference](https://yandex.ru/support/tracker/en/api/about-api) |
| Wiki | 56 | 56 | 0 | 0 | 20 of 24 | [OpenAPI](https://api.wiki.yandex.net/v1/openapi.json) |
| Forms | 84 | 84 | 0 | 8 | 24 of 30 | [OpenAPI](https://api.forms.yandex.net/v1/openapi.json) |

<details>
<summary><b>Tracker: what differs</b></summary>

**Not wrapped on purpose**

| Operation | Why |
|---|---|
| [`GET /boards`](https://yandex.ru/support/tracker/en/api/boards/get-boards) | `boards list` reads the paginated `GET /boards/_paginate` |
| [`GET /users`](https://yandex.ru/support/tracker/en/api/users/get-users) | `users list` reads the paginated `GET /users/_relative` |

**Sent by ycli, not published**

| ycli | Its request |
|---|---|
| `entities.attachment_download` | `GET /attachments/{file_id}/{filename}` |
| `linktypes.list` | `GET /linktypes` |

**Parameters and fields**

| Operation | ycli | Difference | Why it stays |
|---|---|---|---|
| [`POST /bulkchange/_move`](https://yandex.ru/support/tracker/en/api/bulkchange/bulk-move-issues) | `bulk.move` | query parameters ycli cannot send: `notify` |  |
| [`POST /bulkchange/_transition`](https://yandex.ru/support/tracker/en/api/bulkchange/bulk-transition) | `bulk.transition` | query parameters ycli cannot send: `notify` |  |
| [`POST /bulkchange/_update`](https://yandex.ru/support/tracker/en/api/bulkchange/bulk-update-issues) | `bulk.update` | query parameters ycli cannot send: `notify` |  |
| [`POST /entities/{entity_type}`](https://yandex.ru/support/tracker/en/api/entities/create-entity) | `entities.create` | query parameters ycli cannot send: `fields` |  |
| [`PATCH /entities/{entity_type}/{entity_ID}`](https://yandex.ru/support/tracker/en/api/entities/update-entity) | `entities.edit` | query parameters ycli cannot send: `expand`, `fields` |  |
| [`POST /entities/{entity_type}/{entity_ID}/attachments/{file_ID}`](https://yandex.ru/support/tracker/en/api/entities/attachments/add-attachment) | `entities.attachments_attach` | query parameters ycli cannot send: `expand`, `fields`, `notify`, `notifyAuthor` |  |
| [`DELETE /entities/{entity_type}/{entity_ID}/checklistItems`](https://yandex.ru/support/tracker/en/api/entities/checklists/delete-checklist) | `entities.checklists_delete` | query parameters ycli cannot send: `expand`, `fields`, `notify`, `notifyAuthor` |  |
| [`PATCH /entities/{entity_type}/{entity_ID}/checklistItems`](https://yandex.ru/support/tracker/en/api/entities/checklists/patch-checklist) | `entities.checklists_edit` | query parameters ycli cannot send: `expand`, `fields`, `notify`, `notifyAuthor` |  |
| [`POST /entities/{entity_type}/{entity_ID}/checklistItems`](https://yandex.ru/support/tracker/en/api/entities/checklists/add-checklist) | `entities.checklists_create` | query parameters ycli cannot send: `expand`, `fields`, `notify`, `notifyAuthor` |  |
| [`DELETE /entities/{entity_type}/{entity_ID}/checklistItems/{checklist_item_ID}`](https://yandex.ru/support/tracker/en/api/entities/checklists/delete-checklist-item) | `entities.checklists_delete_item` | query parameters ycli cannot send: `expand`, `fields`, `notify`, `notifyAuthor` |  |
| [`PATCH /entities/{entity_type}/{entity_ID}/checklistItems/{checklist_item_ID}`](https://yandex.ru/support/tracker/en/api/entities/checklists/patch-checklist-item) | `entities.checklists_edit_item` | query parameters ycli cannot send: `expand`, `fields`, `notify`, `notifyAuthor` |  |
| [`POST /entities/{entity_type}/{entity_ID}/checklistItems/{checklist_item_ID}/_move`](https://yandex.ru/support/tracker/en/api/entities/checklists/move-checklist-item) | `entities.checklists_move` | query parameters ycli cannot send: `expand`, `fields`, `notify`, `notifyAuthor` |  |
| [`POST /entities/{entity_type}/{entity_ID}/comments`](https://yandex.ru/support/tracker/en/api/entities/comments/add-comment) | `entities.comments_create` | query parameters ycli cannot send: `expand`, `isAddToFollowers`, `notify`, `notifyAuthor` |  |
| [`DELETE /entities/{entity_type}/{entity_ID}/comments/{comment_ID}`](https://yandex.ru/support/tracker/en/api/entities/comments/delete-comment) | `entities.comments_delete` | query parameters ycli cannot send: `notify`, `notifyAuthor` |  |
| [`PATCH /entities/{entity_type}/{entity_ID}/comments/{comment_ID}`](https://yandex.ru/support/tracker/en/api/entities/comments/patch-comment) | `entities.comments_edit` | query parameters ycli cannot send: `expand`, `isAddToFollowers`, `notify`, `notifyAuthor` |  |
| [`GET /entities/{entity_type}/{entity_ID}/events/_relative`](https://yandex.ru/support/tracker/en/api/entities/get-events-relative) | `entities.history` | query parameters ycli cannot send: `direction`, `newEventsOnTop`, `selected` |  |
| [`POST /issues`](https://yandex.ru/support/tracker/en/api/issues/create-issue) | `issues.create` | query parameters ycli cannot send: `notify` |  |
| [`POST /issues/_search`](https://yandex.ru/support/tracker/en/api/issues/search-issues) | `issues.search` | query parameters ycli cannot send: `expand`, `perScroll`, `scrollId`, `scrollTTLMillis`, `scrollType` |  |
| [`GET /issues/_suggest`](https://yandex.ru/support/tracker/en/api/issues/get-suggest) | `issues.suggest` | query parameters ycli cannot send: `embed`, `expand`, `fields`, `full`, `queue` |  |
| [`POST /issues/{id_задачи}/_move`](https://yandex.ru/support/tracker/en/api/issues/move-issue) | `issues.move` | query parameters ycli cannot send: `expand`, `initialStatus`, `moveAllFields`, `notify`, `notifyAuthor` |  |
| [`GET /issues/{issue_ID}`](https://yandex.ru/support/tracker/en/api/issues/get-issue) | `issues.get` | query parameters ycli cannot send: `expand`, `fields` |  |
| [`GET /issues/{issue_ID}/changelog`](https://yandex.ru/support/tracker/en/api/issues/get-changelog) | `changelog.list` | query parameters ycli cannot send: `field`, `sort`, `type` |  |
| [`GET /issues/{issue_ID}/comments`](https://yandex.ru/support/tracker/en/api/issues/get-comments) | `comments.list` | query parameters ycli cannot send: `expand` |  |
| [`GET /priorities`](https://yandex.ru/support/tracker/en/api/admin/get-priorities) | `priorities.list` | query parameters ycli cannot send: `localized` |  |
| [`GET /queues`](https://yandex.ru/support/tracker/en/api/queues/get-queues) | `queues.list` | query parameters ycli cannot send: `expand` |  |

</details>

<details>
<summary><b>Wiki: what differs</b></summary>

</details>

<details>
<summary><b>Forms: what differs</b></summary>

**Parameters and fields**

| Operation | ycli | Difference | Why it stays |
|---|---|---|---|
| `POST /surveys` | `surveys.create` | body fields ycli sends that are not published: `is_public`, `is_published`, `language`<br>model fields that are not published: `modified` | the API accepts it and ignores it (checked live on 2026-10-04)<br>the API returns it (checked live on 2026-10-04), the published schema omits it |
| `GET /surveys/{survey_id}` | `surveys.get` | model fields that are not published: `modified` | the API returns it (checked live on 2026-10-04), the published schema omits it |
| `PATCH /surveys/{survey_id}` | `surveys.modify` | body fields ycli sends that are not published: `is_public`, `is_published`, `language`<br>model fields that are not published: `modified` | the API accepts it and ignores it (checked live on 2026-10-04)<br>the API returns it (checked live on 2026-10-04), the published schema omits it |
| `POST /surveys/{survey_id}/hooks/{hook_id}/subscriptions` | `subscriptions.create` | body fields ycli sends that are not published: `id` | one model builds the body and reads the reply, and the reply carries `id` |
| `PATCH /surveys/{survey_id}/hooks/{hook_id}/subscriptions/{subscription_id}` | `subscriptions.modify` | body fields ycli sends that are not published: `id` | one model builds the body and reads the reply, and the reply carries `id` |
| `POST /surveys/{survey_id}/questions` | `questions.create` | body fields ycli sends that are not published: `id` | the API accepts it and ignores it (checked live on 2026-10-04) |
| `DELETE /surveys/{survey_id}/questions/{question_id}` | `questions.delete` | query parameters ycli sends that are not published: `force` | the API accepts it and ignores it (checked live on 2026-10-04) |
| `PATCH /surveys/{survey_id}/questions/{question_id}` | `questions.modify` | body fields ycli sends that are not published: `id` | the API accepts it and ignores it (checked live on 2026-10-04) |

</details>
<!-- COVERAGE:END -->

## Development

```bash
uv sync --all-extras   # the tests use every extra
uv run pytest          # 100% coverage gate; HTTP is stubbed, no live network
```

The layout and the invariants that keep it regular are in [ARCHITECTURE.md](ARCHITECTURE.md); [CONTRIBUTING.md](CONTRIBUTING.md) has the conventions and how to add an endpoint. Contributions are welcome.

## License

[MIT](LICENSE) © 2026 Sava Znatnov
