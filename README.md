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

- **A command line that scripts well.** JSON when piped, ready for `jq`, `--dry-run` for every write, an exit code for each kind of failure.
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

It adds the MCP server and five skills (`yandex-360`, `yandex-360-tracker`, `yandex-360-wiki`, `yandex-360-forms`, `yandex-360-datalens`) that teach an agent the commands and the API's quirks. Source: [`plugins/yandex-360/`](plugins/yandex-360/).

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

<img src="https://raw.githubusercontent.com/bim-ba/ycli/main/docs/assets/coverage.svg" alt="406 operations across 74 resources: Tracker 190, Wiki 58, Forms 85, DataLens 73" width="760">

`ycli` wraps **406 operations across 74 resources** of the Tracker, Wiki, Forms, and DataLens API. Every one is reachable from the **Python SDK** and the **CLI**, and 396 **MCP** tools serve them to agents (394 per service plus `schema_get`, `status_get`).

> **Legend.** ✅ in **CLI** or **MCP** means the resource is reachable on that surface; MCP tools carry honest hints (reads are `readOnlyHint`, writes say whether they are destructive or idempotent), and `ycli mcp start --read-only` serves only the reads. Resource and operation names link to the official **Yandex API reference**. An operation has one of three states against what Yandex publishes. **Covered** (no mark): ycli sends every published parameter and reads every published field. **Partial** (◐): ycli wraps it and differs somewhere; the mark links to the row that says where and why. **Not covered** (○): Yandex publishes it and ycli does not wrap it; these are listed under each service. Wiki, Forms and DataLens are measured against their OpenAPI documents; Tracker publishes none, so its state is measured against the reference pages (operations, and query parameters where a page lists them). DataLens is in progress, wrapped section by section: the operations of a section ycli has not begun are pending, not missing. Generated from the code by [`scripts/gen_coverage.py`](scripts/gen_coverage.py); do not edit by hand.

### Tracker

<details>
<summary><b>34 resources · 190 operations · 187 MCP tools</b></summary>

**Issues & work items**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [issues](https://yandex.ru/support/tracker/en/api/issues/get-issue) | [get](https://yandex.ru/support/tracker/en/api/issues/get-issue) · [search](https://yandex.ru/support/tracker/en/api/issues/search-issues) · [count](https://yandex.ru/support/tracker/en/api/issues/count-issues) · [create](https://yandex.ru/support/tracker/en/api/issues/create-issue) · [update](https://yandex.ru/support/tracker/en/api/issues/patch-issue) · [move](https://yandex.ru/support/tracker/en/api/issues/move-issue) · [suggest](https://yandex.ru/support/tracker/en/api/issues/get-suggest) · [scroll_clear](https://yandex.ru/support/tracker/en/api/issues/search-release) · [update_bulk](https://yandex.ru/support/tracker/en/api/bulkchange/bulk-update-issues) · [move_bulk](https://yandex.ru/support/tracker/en/api/bulkchange/bulk-move-issues) · [transition_bulk](https://yandex.ru/support/tracker/en/api/bulkchange/bulk-transition) · [import_](https://yandex.ru/support/tracker/en/api/import/import-ticket) | ✅ | ✅ |
| [comments](https://yandex.ru/support/tracker/en/api/issues/get-comments) | [list](https://yandex.ru/support/tracker/en/api/issues/get-comments) · [get](https://yandex.ru/support/tracker/en/api/issues/get-comment) · [create](https://yandex.ru/support/tracker/en/api/issues/add-comment) · [update](https://yandex.ru/support/tracker/en/api/issues/edit-comment) · [delete](https://yandex.ru/support/tracker/en/api/issues/delete-comment) · [reactions_create](https://yandex.ru/support/tracker/en/api/issues/add-reaction-to-comment) · [import_](https://yandex.ru/support/tracker/en/api/import/import-comments) | ✅ | ✅ |
| [links](https://yandex.ru/support/tracker/en/api/issues/get-links) | [list](https://yandex.ru/support/tracker/en/api/issues/get-links) · [list_filtered](https://yandex.ru/support/tracker/en/api/issues/get-links-paginate) · [create](https://yandex.ru/support/tracker/en/api/issues/link-issue) · [delete](https://yandex.ru/support/tracker/en/api/issues/delete-link-issue) · [import_](https://yandex.ru/support/tracker/en/api/import/import-links) | ✅ | ✅ |
| [transitions](https://yandex.ru/support/tracker/en/api/issues/get-transitions) | [list](https://yandex.ru/support/tracker/en/api/issues/get-transitions) · [execute](https://yandex.ru/support/tracker/en/api/issues/new-transition) | ✅ | ✅ |
| [worklog](https://yandex.ru/support/tracker/en/api/issues/issue-worklog) | [list](https://yandex.ru/support/tracker/en/api/issues/issue-worklog) · [search](https://yandex.ru/support/tracker/en/api/issues/get-worklog) · [list_global](https://yandex.ru/support/tracker/en/api/issues/get-worklog) · [create](https://yandex.ru/support/tracker/en/api/issues/new-worklog) · [update](https://yandex.ru/support/tracker/en/api/issues/patch-worklog) · [delete](https://yandex.ru/support/tracker/en/api/issues/delete-worklog) · [import_](https://yandex.ru/support/tracker/en/api/import/import-worklogs) | ✅ | ✅ |
| [changelog](https://yandex.ru/support/tracker/en/api/issues/get-changelog) | [list](https://yandex.ru/support/tracker/en/api/issues/get-changelog) | ✅ | ✅ |
| [checklists](https://yandex.ru/support/tracker/en/api/issues/get-checklist) | [list](https://yandex.ru/support/tracker/en/api/issues/get-checklist) · [create](https://yandex.ru/support/tracker/en/api/issues/add-checklist-item) · [update](https://yandex.ru/support/tracker/en/api/issues/edit-checklist) · [delete](https://yandex.ru/support/tracker/en/api/issues/delete-checklist-item) · [clear](https://yandex.ru/support/tracker/en/api/issues/delete-checklist) | ✅ | ✅ |
| [attachments](https://yandex.ru/support/tracker/en/api/issues/get-attachments-list) | [list](https://yandex.ru/support/tracker/en/api/issues/get-attachments-list) · [download](https://yandex.ru/support/tracker/en/api/issues/get-attachment) · [thumbnails_download](https://yandex.ru/support/tracker/en/api/issues/get-attachment-preview) · [get](https://yandex.ru/support/tracker/en/api/issues/get-attachment-info) · [delete](https://yandex.ru/support/tracker/en/api/issues/delete-attachment) · [upload](https://yandex.ru/support/tracker/en/api/issues/post-attachment) · [upload_temp](https://yandex.ru/support/tracker/en/api/issues/temp-attachment) · [import_](https://yandex.ru/support/tracker/en/api/import/import-attachments) · [import_for_comment](https://yandex.ru/support/tracker/en/api/import/import-attachments) | ✅ | ✅ |
| [remotelinks](https://yandex.ru/support/tracker/en/api/issues/get-external-links) | [list](https://yandex.ru/support/tracker/en/api/issues/get-external-links) · [create](https://yandex.ru/support/tracker/en/api/issues/add-external-link) · [delete](https://yandex.ru/support/tracker/en/api/issues/delete-external-link) | ✅ | ✅ |

**Agile boards**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [boards](https://yandex.ru/support/tracker/en/api/boards/get-boards) | [list](https://yandex.ru/support/tracker/en/api/boards/get-boards) · [get](https://yandex.ru/support/tracker/en/api/boards/get-board) · [create](https://yandex.ru/support/tracker/en/api/boards/post-board) · [update](https://yandex.ru/support/tracker/en/api/boards/patch-board) · [delete](https://yandex.ru/support/tracker/en/api/boards/delete-board) | ✅ | ✅ |
| [sprints](https://yandex.ru/support/tracker/en/api/boards/get-sprints) | [list](https://yandex.ru/support/tracker/en/api/boards/get-sprints) · [get](https://yandex.ru/support/tracker/en/api/boards/get-sprint) · [create](https://yandex.ru/support/tracker/en/api/boards/post-sprint) · [update](https://yandex.ru/support/tracker/en/api/boards/patch-sprint) · [delete](https://yandex.ru/support/tracker/en/api/boards/delete-sprint) · [start](https://yandex.ru/support/tracker/en/api/boards/start-sprint) · [archive](https://yandex.ru/support/tracker/en/api/boards/archive-sprint) | ✅ | ✅ |
| [columns](https://yandex.ru/support/tracker/en/api/boards/get-columns) | [list](https://yandex.ru/support/tracker/en/api/boards/get-columns) · [get](https://yandex.ru/support/tracker/en/api/boards/get-column) · [create](https://yandex.ru/support/tracker/en/api/boards/post-column) · [update](https://yandex.ru/support/tracker/en/api/boards/patch-column) · [delete](https://yandex.ru/support/tracker/en/api/boards/delete-column) | ✅ | ✅ |

**Dictionaries**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [priorities](https://yandex.ru/support/tracker/en/api/admin/get-priorities) | [list](https://yandex.ru/support/tracker/en/api/admin/get-priorities) · [create](https://yandex.ru/support/tracker/en/api/admin/create-priority) · [update](https://yandex.ru/support/tracker/en/api/admin/patch-priority) | ✅ | ✅ |
| [statuses](https://yandex.ru/support/tracker/en/api/admin/get-statuses) | [list](https://yandex.ru/support/tracker/en/api/admin/get-statuses) · [create](https://yandex.ru/support/tracker/en/api/admin/create-status) · [update](https://yandex.ru/support/tracker/en/api/admin/patch-status) | ✅ | ✅ |
| [resolutions](https://yandex.ru/support/tracker/en/api/admin/get-resolutions) | [list](https://yandex.ru/support/tracker/en/api/admin/get-resolutions) · [create](https://yandex.ru/support/tracker/en/api/admin/create-resolution) · [update](https://yandex.ru/support/tracker/en/api/admin/patch-resolution) | ✅ | ✅ |
| [issuetypes](https://yandex.ru/support/tracker/en/api/admin/get-issue-types) | [list](https://yandex.ru/support/tracker/en/api/admin/get-issue-types) · [create](https://yandex.ru/support/tracker/en/api/admin/create-issue-type) · [update](https://yandex.ru/support/tracker/en/api/admin/patch-issue-type) | ✅ | ✅ |
| linktypes | list | ✅ | ✅ |

**Fields, queues & structure**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [fields](https://yandex.ru/support/tracker/en/api/issues/get-global-fields) | [list](https://yandex.ru/support/tracker/en/api/issues/get-global-fields) · [get](https://yandex.ru/support/tracker/en/api/issues/get-issue-fields) · [create](https://yandex.ru/support/tracker/en/api/issues/create-field) · [update](https://yandex.ru/support/tracker/en/api/issues/patch-issue-field-name) · [categories_create](https://yandex.ru/support/tracker/en/api/issues/create-issue-field-category) · [categories_update](https://yandex.ru/support/tracker/en/api/issues/patch-issue-field-category) | ✅ | ✅ |
| [localfields](https://yandex.ru/support/tracker/en/api/queues/get-local-fields) | [list](https://yandex.ru/support/tracker/en/api/queues/get-local-fields) · [get](https://yandex.ru/support/tracker/en/api/queues/get-info-local-field) · [create](https://yandex.ru/support/tracker/en/api/queues/create-local-field) · [update](https://yandex.ru/support/tracker/en/api/queues/edit-local-field) | ✅ | ✅ |
| [components](https://yandex.ru/support/tracker/en/api/queues/get-components) | [list](https://yandex.ru/support/tracker/en/api/queues/get-components) · [create](https://yandex.ru/support/tracker/en/api/queues/post-component) · [update](https://yandex.ru/support/tracker/en/api/queues/patch-component) · [list_for_queue](https://yandex.ru/support/tracker/en/api/queues/get-queue-components) · [get](https://yandex.ru/support/tracker/en/api/queues/get-component) · [delete](https://yandex.ru/support/tracker/en/api/queues/delete-component) · [user_permissions_get](https://yandex.ru/support/tracker/en/api/queues/get-component-user-access) · [group_permissions_get](https://yandex.ru/support/tracker/en/api/queues/get-component-group-access) | ✅ | ✅ |
| [queues](https://yandex.ru/support/tracker/en/api/queues/get-queues) | [list](https://yandex.ru/support/tracker/en/api/queues/get-queues) · [get](https://yandex.ru/support/tracker/en/api/queues/get-queue) · [tags_list](https://yandex.ru/support/tracker/en/api/queues/get-tags) · [versions_list](https://yandex.ru/support/tracker/en/api/queues/get-versions) · [fields_list](https://yandex.ru/support/tracker/en/api/queues/get-fields) · [create](https://yandex.ru/support/tracker/en/api/queues/create-queue) · [delete](https://yandex.ru/support/tracker/en/api/queues/delete-queue) · [restore](https://yandex.ru/support/tracker/en/api/queues/restore-queue) · [permissions_update](https://yandex.ru/support/tracker/en/api/queues/manage-access) · [tags_delete](https://yandex.ru/support/tracker/en/api/queues/delete-tag) · [versions_create](https://yandex.ru/support/tracker/en/api/queues/create-version) · [versions_get](https://yandex.ru/support/tracker/en/api/queues/get-version) · [versions_update](https://yandex.ru/support/tracker/en/api/queues/update-version) · [versions_delete](https://yandex.ru/support/tracker/en/api/queues/delete-version) · [user_permissions_get](https://yandex.ru/support/tracker/en/api/queues/get-user-access) · [group_permissions_get](https://yandex.ru/support/tracker/en/api/queues/get-group-access) | ✅ | ✅ |
| [workflows](https://yandex.ru/support/tracker/en/api/queues/workflows/get-workflows) | [list](https://yandex.ru/support/tracker/en/api/queues/workflows/get-workflows) · [get](https://yandex.ru/support/tracker/en/api/queues/workflows/get-workflow) · [list_for_queue](https://yandex.ru/support/tracker/en/api/queues/workflows/get-queue-workflows) · [create](https://yandex.ru/support/tracker/en/api/queues/workflows/post-workflow) · [update](https://yandex.ru/support/tracker/en/api/queues/workflows/patch-workflow) · [actions_update](https://yandex.ru/support/tracker/en/api/queues/workflows/patch-workflow-action) · [delete](https://yandex.ru/support/tracker/en/api/queues/workflows/delete-workflow) | ✅ | ✅ |
| [projects](https://yandex.ru/support/tracker/en/api/projects/get-projects) | [list](https://yandex.ru/support/tracker/en/api/projects/get-projects) · [get](https://yandex.ru/support/tracker/en/api/projects/get-project) · [queues_list](https://yandex.ru/support/tracker/en/api/projects/get-project-queues) · [create](https://yandex.ru/support/tracker/en/api/projects/create-project) · [update](https://yandex.ru/support/tracker/en/api/projects/update-project) · [delete](https://yandex.ru/support/tracker/en/api/projects/delete-project) | ✅ | ✅ |

**Automation & bulk**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [macros](https://yandex.ru/support/tracker/en/api/get-macroses) | [list](https://yandex.ru/support/tracker/en/api/get-macroses) · [get](https://yandex.ru/support/tracker/en/api/get-macros) · [create](https://yandex.ru/support/tracker/en/api/post-macros) · [update](https://yandex.ru/support/tracker/en/api/patch-macros) · [delete](https://yandex.ru/support/tracker/en/api/delete-macros) | ✅ | ✅ |
| [triggers](https://yandex.ru/support/tracker/en/api/queues/get-trigger) | [list](https://yandex.ru/support/tracker/en/api/queues/get-triggers) · [get](https://yandex.ru/support/tracker/en/api/queues/get-trigger) · [create](https://yandex.ru/support/tracker/en/api/queues/create-trigger) · [update](https://yandex.ru/support/tracker/en/api/queues/change-trigger) · [webhook_log_list](https://yandex.ru/support/tracker/en/api/queues/view-trigger-logs) | ✅ | ✅ |
| [autoactions](https://yandex.ru/support/tracker/en/api/queues/get-autoaction) | [get](https://yandex.ru/support/tracker/en/api/queues/get-autoaction) · [create](https://yandex.ru/support/tracker/en/api/queues/create-autoaction) · [logs_list](https://yandex.ru/support/tracker/en/api/queues/view-autoaction-logs) · [logs_get](https://yandex.ru/support/tracker/en/api/queues/view-autoaction-logs) | ✅ | ✅ |
| [dashboards](https://yandex.ru/support/tracker/en/api/dashboards/create-dashboard) | [create](https://yandex.ru/support/tracker/en/api/dashboards/create-dashboard) · [widgets_create_cycle_time](https://yandex.ru/support/tracker/en/api/dashboards/create-widget) | ✅ | ✅ |
| [bulk](https://yandex.ru/support/tracker/en/api/bulkchange/bulk-move-info) | [get](https://yandex.ru/support/tracker/en/api/bulkchange/bulk-move-info) · [issues_list](https://yandex.ru/support/tracker/en/api/bulkchange/bulk-move-info) | ✅ | ✅ |

**Entities, users & search**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [entities](https://yandex.ru/support/tracker/en/api/entities/about-entities) | [create](https://yandex.ru/support/tracker/en/api/entities/create-entity) · [get](https://yandex.ru/support/tracker/en/api/entities/get-entity) · [update](https://yandex.ru/support/tracker/en/api/entities/update-entity) · [delete](https://yandex.ru/support/tracker/en/api/entities/delete-entity) · [search](https://yandex.ru/support/tracker/en/api/entities/search-entities) · [events_list](https://yandex.ru/support/tracker/en/api/entities/get-events-relative) · [permissions_get](https://yandex.ru/support/tracker/en/api/entities/get-access) · [permissions_update](https://yandex.ru/support/tracker/en/api/entities/patch-access) · [permissions_get_direct](https://yandex.ru/support/tracker/en/api/entities/get-permissions) · [permissions_update_direct](https://yandex.ru/support/tracker/en/api/entities/patch-permissions) · [update_bulk](https://yandex.ru/support/tracker/en/api/entities/bulkchange-entities) · [bulk_get](https://yandex.ru/support/tracker/en/api/entities/bulkchange-entities) · [reports_create](https://yandex.ru/support/tracker/en/api/entities/about-entities) · [comments_list](https://yandex.ru/support/tracker/en/api/entities/comments/get-all-comments) · [comments_list_relative](https://yandex.ru/support/tracker/en/api/entities/comments/get-all-comments) · [comments_get](https://yandex.ru/support/tracker/en/api/entities/comments/get-comment) · [comments_create](https://yandex.ru/support/tracker/en/api/entities/comments/add-comment) · [comments_update](https://yandex.ru/support/tracker/en/api/entities/comments/patch-comment) · [comments_delete](https://yandex.ru/support/tracker/en/api/entities/comments/delete-comment) · [checklists_create](https://yandex.ru/support/tracker/en/api/entities/checklists/add-checklist) · [checklists_update](https://yandex.ru/support/tracker/en/api/entities/checklists/patch-checklist) · [checklists_items_update](https://yandex.ru/support/tracker/en/api/entities/checklists/patch-checklist-item) · [checklists_delete](https://yandex.ru/support/tracker/en/api/entities/checklists/delete-checklist) · [checklists_items_delete](https://yandex.ru/support/tracker/en/api/entities/checklists/delete-checklist-item) · [checklists_move](https://yandex.ru/support/tracker/en/api/entities/checklists/move-checklist-item) · [links_list](https://yandex.ru/support/tracker/en/api/entities/links/get-links) · [links_create](https://yandex.ru/support/tracker/en/api/entities/links/add-links) · [links_delete](https://yandex.ru/support/tracker/en/api/entities/links/delete-link) · [attachments_list](https://yandex.ru/support/tracker/en/api/entities/attachments/get-all-attachments) · [attachments_get](https://yandex.ru/support/tracker/en/api/entities/attachments/get-attachment) · [attachments_download](https://yandex.ru/support/tracker/en/api/entities/about-entities) · [attachments_attach](https://yandex.ru/support/tracker/en/api/entities/attachments/add-attachment) · [attachments_delete](https://yandex.ru/support/tracker/en/api/entities/attachments/delete-attachment) | ✅ | ✅ |
| [users](https://yandex.ru/support/tracker/en/api/users/get-users) | [get](https://yandex.ru/support/tracker/en/api/users/get-user) · [list](https://yandex.ru/support/tracker/en/api/users/get-users) | ✅ | ✅ |
| [applications](https://yandex.ru/support/tracker/en/api/issues/get-applications) | [list](https://yandex.ru/support/tracker/en/api/issues/get-applications) | ✅ | ✅ |
| [filters](https://yandex.ru/support/tracker/en/api/filters/get-filter) | [get](https://yandex.ru/support/tracker/en/api/filters/get-filter) · [create](https://yandex.ru/support/tracker/en/api/filters/create-filter) · [update](https://yandex.ru/support/tracker/en/api/filters/update-filter) · [delete](https://yandex.ru/support/tracker/en/api/filters/delete-filter) | ✅ | ✅ |
| [gaps](https://yandex.ru/support/tracker/en/api/gaps/post-gaps) | [create](https://yandex.ru/support/tracker/en/api/gaps/post-gaps) · [search](https://yandex.ru/support/tracker/en/api/gaps/search-gaps) · [delete](https://yandex.ru/support/tracker/en/api/gaps/delete-gaps) | ✅ | ✅ |
| [me](https://yandex.ru/support/tracker/en/api/users/get-user-info) | [get](https://yandex.ru/support/tracker/en/api/users/get-user-info) | ✅ | ✅ |

**Not covered** (2)

- ○ [`GET /boards`](https://yandex.ru/support/tracker/en/api/boards/get-boards): `boards list` reads the paginated `GET /boards/_paginate`
- ○ [`GET /users`](https://yandex.ru/support/tracker/en/api/users/get-users): `users list` reads the paginated `GET /users/_relative`

</details>

### Wiki

<details>
<summary><b>10 resources · 58 operations · 56 MCP tools</b></summary>

**Pages**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [pages](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) | [get_by_id](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details_by_id) · [get](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) · [descendants_list](https://yandex.ru/support/wiki/en/api-ref/pages/pages__descendants_by_slug) · [descendants_list_by_id](https://yandex.ru/support/wiki/en/api-ref/pages/pages__descendants_by_id) · [grids_list](https://yandex.ru/support/wiki/en/api-ref/pages/pages__page_grids) · [create](https://yandex.ru/support/wiki/en/api-ref/pages/pages__create_page) · [update](https://yandex.ru/support/wiki/en/api-ref/pages/pages__update_page_details) · [delete](https://yandex.ru/support/wiki/en/api-ref/pages/pages__delete_page) · [append](https://yandex.ru/support/wiki/en/api-ref/pages/pages__append_content) · [clone](https://yandex.ru/support/wiki/en/api-ref/pages/pages__clone_page) · [move](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) · [revisions_list](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) · [backlinks_list](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) · [search](https://yandex.ru/support/wiki/en/api-ref/search/search__search) | ✅ | ✅ |
| [resources](https://yandex.ru/support/wiki/en/api-ref/pagesresources/pagesresources__resources) | [list](https://yandex.ru/support/wiki/en/api-ref/pagesresources/pagesresources__resources) | ✅ | ✅ |
| [recovery](https://yandex.ru/support/wiki/en/api-ref/recovery_tokens/recovery_tokens__recover_page_by_token) | [recover](https://yandex.ru/support/wiki/en/api-ref/recovery_tokens/recovery_tokens__recover_page_by_token) | ✅ | ✅ |

**Collaboration**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [comments](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__comments) | [list](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__comments) · [thread_list](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__thread_comments) · [thread_get](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__thread_comments) · [create](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__create_comment) · [delete](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__delete_comment) | ✅ | ✅ |
| [attachments](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) | [list](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) · [get](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) · [previews_download](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) · [download](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__download_by_file_id) · [download_by_url](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__download_by_filename_slug_pair) · [delete](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__delete_attach) · [attach](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attach_file) · [upload](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) | ✅ | ✅ |
| [access](https://yandex.ru/support/wiki/en/api-ref/pages_access/pagesaccess__create_page_access) | [create](https://yandex.ru/support/wiki/en/api-ref/pages_access/pagesaccess__create_page_access) · [update](https://yandex.ru/support/wiki/en/api-ref/pages_access/pagesaccess__update_page_access) · [delete](https://yandex.ru/support/wiki/en/api-ref/pages_access/pagesaccess__delete_page_access) · [clear](https://yandex.ru/support/wiki/en/api-ref/pages_access/pagesaccess__delete_page_accesses) | ✅ | ✅ |

**Grids (dynamic tables)**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [grids](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) | [get](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) · [create](https://yandex.ru/support/wiki/en/api-ref/grids/grids__create_grid) · [update](https://yandex.ru/support/wiki/en/api-ref/grids/grids__update_grid) · [delete](https://yandex.ru/support/wiki/en/api-ref/grids/grids__delete_grid) · [rows_create](https://yandex.ru/support/wiki/en/api-ref/grids/grids__add_rows) · [rows_delete](https://yandex.ru/support/wiki/en/api-ref/grids/grids__remove_rows) · [rows_move](https://yandex.ru/support/wiki/en/api-ref/grids/grids__move_rows) · [columns_create](https://yandex.ru/support/wiki/en/api-ref/grids/grids__add_columns) · [columns_delete](https://yandex.ru/support/wiki/en/api-ref/grids/grids__remove_columns) · [columns_move](https://yandex.ru/support/wiki/en/api-ref/grids/grids__move_columns) · [cells_update](https://yandex.ru/support/wiki/en/api-ref/grids/grids__update_cells) · [clone](https://yandex.ru/support/wiki/en/api-ref/grids/grids__clone_grid) · [columns_suggest](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) · [columns_update](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) · [rows_update](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) | ✅ | ✅ |

**Async & uploads**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [operations](https://yandex.ru/support/wiki/en/api-ref/operations/operations__get_clone_operation_status) | [clone_get](https://yandex.ru/support/wiki/en/api-ref/operations/operations__get_clone_operation_status) · [clone_inline_grid_get](https://yandex.ru/support/wiki/en/api-ref/operations/operations__get_clone_inline_grid_operation_status) · [move_get](https://yandex.ru/support/wiki/en/api-ref/operations/operations__get_clone_operation_status) | ✅ | ✅ |
| [uploadsessions](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__create_upload_session) | [create](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__create_upload_session) · [get](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__get_upload_session) · [parts_upload](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__upload_part) · [finish](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__complete_multipart_upload) · [abort](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__abort_multipart_upload) · [abort_all](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__abort_all) | ✅ | ✅ |

**Identity**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [me](https://yandex.ru/support/wiki/en/api-ref/users/users__me) | [get](https://yandex.ru/support/wiki/en/api-ref/users/users__me) | ✅ | ✅ |

</details>

### Forms

<details>
<summary><b>16 resources · 85 operations · 78 MCP tools</b></summary>

**Surveys & questions**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [surveys](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_surveys_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_surveys_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_survey_public_view) [◐](#differs-forms-get-surveys-survey-id) · [create](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_create_survey_public_view) [◐](#differs-forms-post-surveys) · [update](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view) [◐](#differs-forms-patch-surveys-survey-id) · [delete](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_delete_survey_public_view) · [publish](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_publish_survey_public_view) · [unpublish](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_unpublish_survey_public_view) | ✅ | ✅ |
| [questions](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_get_questions_public_view) | [get](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_get_question_public_view) · [list](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_get_questions_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_create_question_public_view) [◐](#differs-forms-post-surveys-survey-id-questions) · [update](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_modify_question_public_view) [◐](#differs-forms-patch-surveys-survey-id-questions-question-id) · [delete](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_delete_question_public_view) [◐](#differs-forms-delete-surveys-survey-id-questions-question-id) · [move](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_move_question_public_view) | ✅ | ✅ |
| [conditions](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_question_conditions_public_view) | [question_list](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_question_conditions_public_view) · [question_get](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_question_condition_public_view) · [question_create](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_create_question_condition_public_view) · [question_update](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_modify_question_condition_public_view) · [question_delete](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_delete_question_condition_public_view) · [question_update_operator](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_patch_question_conditions_operator_public_view) · [page_list](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_page_conditions_public_view) · [page_get](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_page_condition_public_view) · [page_create](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_create_page_condition_public_view) · [page_update](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_modify_page_condition_public_view) · [page_delete](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_delete_page_condition_public_view) · [page_update_operator](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_patch_page_conditions_operator_public_view) · [submit_list](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_submit_conditions_public_view) · [submit_get](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_submit_condition_public_view) · [submit_create](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_create_submit_condition_public_view) · [submit_update](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_modify_submit_condition_public_view) · [submit_delete](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_delete_submit_condition_public_view) · [submit_update_operator](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_patch_submit_conditions_operator_public_view) · [hook_list](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_get_hook_conditions_public_view) · [hook_get](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_get_hook_condition_public_view) · [hook_create](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_create_hook_condition_public_view) · [hook_update](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_modify_hook_condition_public_view) · [hook_delete](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_delete_hook_condition_public_view) · [hook_update_operator](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_patch_hook_conditions_operator_public_view) | ✅ | ✅ |
| [access](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_permissions_get_access_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_permissions_get_access_public_view) · [update](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_permissions_update_access_public_view) · [grant](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_permissions_grant_access_public_view) · [revoke](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_permissions_revoke_access_public_view) | ✅ | ✅ |
| [history](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_survey_history_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_survey_history_public_view) | ✅ | ✅ |

**Responses & export**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [answers](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) | [get](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answer_public_view) · [list](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) · [export](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_export_answers_public_view) · [export_results_get](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_export_answers_results_public_view) · [export_download](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_export_answers_results_public_view) · [integrations_list](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_answers_get_integrations_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) · [restore](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) | ✅ | ✅ |
| [operations](https://yandex.ru/support/forms/en/api-ref/operations/events_v1_views_operations_get_operation_view) | [get](https://yandex.ru/support/forms/en/api-ref/operations/events_v1_views_operations_get_operation_view) | ✅ | ✅ |

**Integrations**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [hooks](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_get_hooks_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_get_hooks_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_get_hook_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_create_hook_public_view) · [update](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_modify_hook_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_delete_hook_public_view) | ✅ | ✅ |
| [subscriptions](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_get_subscriptions_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_get_subscriptions_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_get_subscription_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_create_subscription_public_view) [◐](#differs-forms-post-surveys-survey-id-hooks-hook-id-subscriptions) · [update](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_modify_subscription_public_view) [◐](#differs-forms-patch-surveys-survey-id-hooks-hook-id-subscriptions-subscription-id) · [delete](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_delete_subscription_public_view) · [attach](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_save_subscription_attachment_public_view) | ✅ | ✅ |
| [variables](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_get_variables_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_get_variables_public_view) | ✅ | ✅ |
| [notifications](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_get_notifications_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_get_notifications_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_get_notification_public_view) · [status_get](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_get_notification_status_public_view) · [restart](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_restart_notification_public_view) · [cancel](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_cancel_notification_public_view) · [errors_list](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_surveys_get_visible_errors_public_view) | ✅ | ✅ |

**Distribution**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [keysets](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_get_keysets_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_get_keysets_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_get_keyset_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_create_keyset_public_view) · [update](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_modify_keyset_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_delete_keyset_public_view) · [download](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_download_keyset_public_view) | ✅ | ✅ |
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

### DataLens

<details>
<summary><b>14 resources · 73 operations · 73 MCP tools</b></summary>

**Organization**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| tenant | details_get | ✅ | ✅ |
| [members](https://yandex.cloud/en/docs/datalens/api-ref/Access/) | [list](https://yandex.cloud/en/docs/datalens/api-ref/Access/rpcbatchListMembers-post) | ✅ | ✅ |

**Collections & workbooks**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [collections](https://yandex.cloud/en/docs/datalens/api-ref/Collection/) | [get](https://yandex.cloud/en/docs/datalens/api-ref/Collection/rpcgetCollection-post) · [list_by_ids](https://yandex.cloud/en/docs/datalens/api-ref/Collection/rpcgetCollectionsByIds-post) · [content_list](https://yandex.cloud/en/docs/datalens/api-ref/Collection/rpcgetCollectionContent-post) · [breadcrumbs_list](https://yandex.cloud/en/docs/datalens/api-ref/Collection/rpcgetCollectionBreadcrumbs-post) · [permissions_get_root](https://yandex.cloud/en/docs/datalens/api-ref/Collection/rpcgetRootCollectionPermissions-post) · [access_bindings_list](https://yandex.cloud/en/docs/datalens/api-ref/Collection/rpclistCollectionAccessBindings-post) · [create](https://yandex.cloud/en/docs/datalens/api-ref/Collection/rpccreateCollection-post) · [update](https://yandex.cloud/en/docs/datalens/api-ref/Collection/rpcupdateCollection-post) · [move](https://yandex.cloud/en/docs/datalens/api-ref/Collection/rpcmoveCollection-post) · [move_bulk](https://yandex.cloud/en/docs/datalens/api-ref/Collection/rpcmoveCollections-post) · [delete](https://yandex.cloud/en/docs/datalens/api-ref/Collection/rpcdeleteCollection-post) · [delete_bulk](https://yandex.cloud/en/docs/datalens/api-ref/Collection/rpcdeleteCollections-post) · [access_bindings_update](https://yandex.cloud/en/docs/datalens/api-ref/Collection/rpcupdateCollectionAccessBindings-post) | ✅ | ✅ |
| [workbooks](https://yandex.cloud/en/docs/datalens/api-ref/Workbook/) | [get](https://yandex.cloud/en/docs/datalens/api-ref/Workbook/rpcgetWorkbook-post) · [list](https://yandex.cloud/en/docs/datalens/api-ref/Workbook/rpcgetWorkbooksList-post) · [list_by_ids](https://yandex.cloud/en/docs/datalens/api-ref/Workbook/rpcgetWorkbooksByIds-post) · [access_bindings_list](https://yandex.cloud/en/docs/datalens/api-ref/Workbook/rpclistWorkbookAccessBindings-post) · [entries_list](https://yandex.cloud/en/docs/datalens/api-ref/Workbook/rpcgetWorkbookEntries-post) · [create](https://yandex.cloud/en/docs/datalens/api-ref/Workbook/rpccreateWorkbook-post) · [update](https://yandex.cloud/en/docs/datalens/api-ref/Workbook/rpcupdateWorkbook-post) · [move](https://yandex.cloud/en/docs/datalens/api-ref/Workbook/rpcmoveWorkbook-post) · [move_bulk](https://yandex.cloud/en/docs/datalens/api-ref/Workbook/rpcmoveWorkbooks-post) · [delete](https://yandex.cloud/en/docs/datalens/api-ref/Workbook/rpcdeleteWorkbook-post) · [delete_bulk](https://yandex.cloud/en/docs/datalens/api-ref/Workbook/rpcdeleteWorkbooks-post) · [access_bindings_update](https://yandex.cloud/en/docs/datalens/api-ref/Workbook/rpcupdateWorkbookAccessBindings-post) | ✅ | ✅ |
| [workbookexports](https://yandex.cloud/en/docs/datalens/api-ref/WorkbookExport/) | [start](https://yandex.cloud/en/docs/datalens/api-ref/WorkbookExport/rpcstartWorkbookExport-post) · [status_get](https://yandex.cloud/en/docs/datalens/api-ref/WorkbookExport/rpcgetWorkbookExportStatus-post) · [result_get](https://yandex.cloud/en/docs/datalens/api-ref/WorkbookExport/rpcgetWorkbookExportResult-post) · [cancel](https://yandex.cloud/en/docs/datalens/api-ref/WorkbookExport/rpccancelWorkbookExport-post) | ✅ | ✅ |
| [workbookimports](https://yandex.cloud/en/docs/datalens/api-ref/WorkbookImport/) | [start](https://yandex.cloud/en/docs/datalens/api-ref/WorkbookImport/rpcstartWorkbookImport-post) · [status_get](https://yandex.cloud/en/docs/datalens/api-ref/WorkbookImport/rpcgetWorkbookImportStatus-post) | ✅ | ✅ |

**Entries**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [entries](https://yandex.cloud/en/docs/datalens/api-ref/Entries/) | [list](https://yandex.cloud/en/docs/datalens/api-ref/Navigation/rpcgetEntries-post) · [relations_list](https://yandex.cloud/en/docs/datalens/api-ref/Entries/rpcgetEntriesRelations-post) · [permissions_get](https://yandex.cloud/en/docs/datalens/api-ref/Entries/rpcgetEntriesPermissions-post) · [revisions_list](https://yandex.cloud/en/docs/datalens/api-ref/Entries/) · [rename](https://yandex.cloud/en/docs/datalens/api-ref/Entries/rpcrenameEntry-post) | ✅ | ✅ |
| [entrylocks](https://yandex.cloud/en/docs/datalens/api-ref/EntryLock/) | [create](https://yandex.cloud/en/docs/datalens/api-ref/EntryLock/rpccreateEntryLock-post) · [extend](https://yandex.cloud/en/docs/datalens/api-ref/EntryLock/rpcextendEntryLock-post) · [delete](https://yandex.cloud/en/docs/datalens/api-ref/EntryLock/rpcdeleteEntryLock-post) | ✅ | ✅ |
| [permissions](https://yandex.cloud/en/docs/datalens/api-ref/Permissions/) | [get_bulk](https://yandex.cloud/en/docs/datalens/api-ref/Permissions/rpcgetPermissionsBulk-post) | ✅ | ✅ |

**Data**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [connections](https://yandex.cloud/en/docs/datalens/api-ref/Connection/) | [get](https://yandex.cloud/en/docs/datalens/api-ref/Connection/rpcgetConnection-post) · [create](https://yandex.cloud/en/docs/datalens/api-ref/Connection/rpccreateConnection-post) · [update](https://yandex.cloud/en/docs/datalens/api-ref/Connection/rpcupdateConnection-post) · [delete](https://yandex.cloud/en/docs/datalens/api-ref/Connection/rpcdeleteConnection-post) | ✅ | ✅ |
| [datasets](https://yandex.cloud/en/docs/datalens/api-ref/Data/) | [get](https://yandex.cloud/en/docs/datalens/api-ref/Dataset/rpcgetDataset-post) · [create](https://yandex.cloud/en/docs/datalens/api-ref/Dataset/rpccreateDataset-post) · [update](https://yandex.cloud/en/docs/datalens/api-ref/Dataset/rpcupdateDataset-post) · [delete](https://yandex.cloud/en/docs/datalens/api-ref/Dataset/rpcdeleteDataset-post) · [validate](https://yandex.cloud/en/docs/datalens/api-ref/Dataset/rpcvalidateDataset-post) · [data_get](https://yandex.cloud/en/docs/datalens/api-ref/Data/rpcgetDatasetData-post) | ✅ | ✅ |

**Charts**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [charts](https://yandex.cloud/en/docs/datalens/api-ref/Editor/) | [data_get](https://yandex.cloud/en/docs/datalens/api-ref/Editor/) · [wizard_get](https://yandex.cloud/en/docs/datalens/api-ref/Wizard/rpcgetWizardChart-post) · [wizard_create](https://yandex.cloud/en/docs/datalens/api-ref/Wizard/rpccreateWizardChart-post) · [wizard_update](https://yandex.cloud/en/docs/datalens/api-ref/Wizard/rpcupdateWizardChart-post) · [wizard_delete](https://yandex.cloud/en/docs/datalens/api-ref/Wizard/rpcdeleteWizardChart-post) · [ql_get](https://yandex.cloud/en/docs/datalens/api-ref/QL/rpcgetQLChart-post) · [ql_create](https://yandex.cloud/en/docs/datalens/api-ref/QL/rpccreateQLChart-post) · [ql_update](https://yandex.cloud/en/docs/datalens/api-ref/QL/rpcupdateQLChart-post) · [ql_delete](https://yandex.cloud/en/docs/datalens/api-ref/QL/rpcdeleteQLChart-post) · [editor_get](https://yandex.cloud/en/docs/datalens/api-ref/Editor/rpcgetEditorChart-post) · [editor_create](https://yandex.cloud/en/docs/datalens/api-ref/Editor/rpccreateEditorChart-post) · [editor_update](https://yandex.cloud/en/docs/datalens/api-ref/Editor/rpcupdateEditorChart-post) · [editor_delete](https://yandex.cloud/en/docs/datalens/api-ref/Editor/rpcdeleteEditorChart-post) | ✅ | ✅ |

**Embedding**

| Resource | Operations | CLI | MCP |
|----------|------------|:---:|:---:|
| [embeds](https://yandex.cloud/en/docs/datalens/api-ref/Embeds/) | [list](https://yandex.cloud/en/docs/datalens/api-ref/Embeds/rpclistEmbeds-post) · [create](https://yandex.cloud/en/docs/datalens/api-ref/Embeds/rpccreateEmbed-post) · [update](https://yandex.cloud/en/docs/datalens/api-ref/Embeds/rpcupdateEmbed-post) · [delete](https://yandex.cloud/en/docs/datalens/api-ref/Embeds/rpcdeleteEmbed-post) | ✅ | ✅ |
| [embeddingsecrets](https://yandex.cloud/en/docs/datalens/api-ref/EmbeddingSecrets/) | [get](https://yandex.cloud/en/docs/datalens/api-ref/EmbeddingSecrets/rpcgetEmbeddingSecret-post) · [list](https://yandex.cloud/en/docs/datalens/api-ref/EmbeddingSecrets/rpclistEmbeddingSecrets-post) · [create](https://yandex.cloud/en/docs/datalens/api-ref/EmbeddingSecrets/rpccreateEmbeddingSecret-post) · [delete](https://yandex.cloud/en/docs/datalens/api-ref/EmbeddingSecrets/rpcdeleteEmbeddingSecret-post) | ✅ | ✅ |

**Not covered** (7)

- ○ [`POST /rpc/createFolder`](https://yandex.cloud/en/docs/datalens/api-ref/Folder/rpccreateFolder-post): the old placement model (folders); the organization has none to check it on (#394)
- ○ [`POST /rpc/deleteFolder`](https://yandex.cloud/en/docs/datalens/api-ref/Folder/rpcdeleteFolder-post): the old placement model (folders); the organization has none to check it on (#394)
- ○ [`POST /rpc/dlsSuggest`](https://yandex.cloud/en/docs/datalens/api-ref/Folder/rpcdlsSuggest-post): the old placement model (folders); the organization has none to check it on (#394)
- ○ [`POST /rpc/getPermissions`](https://yandex.cloud/en/docs/datalens/api-ref/Folder/rpcgetPermissions-post): the old placement model (folders); the organization has none to check it on (#394)
- ○ [`POST /rpc/listDirectory`](https://yandex.cloud/en/docs/datalens/api-ref/Navigation/rpclistDirectory-post): the old placement model (folders); the organization has none to check it on (#394)
- ○ [`POST /rpc/modifyPermissions`](https://yandex.cloud/en/docs/datalens/api-ref/Folder/rpcmodifyPermissions-post): the old placement model (folders); the organization has none to check it on (#394)
- ○ [`POST /rpc/moveFolderEntry`](https://yandex.cloud/en/docs/datalens/api-ref/Folder/rpcmoveFolderEntry-post): the old placement model (folders); the organization has none to check it on (#394)

</details>

Every resource and operation above deep-links to the Yandex API reference: 387 of 406 operations resolve to their own endpoint page and 17 to their resource's page. No public API reference exists yet for `datalens.tenant`, `datalens.tenant.details_get`, `tracker.linktypes`, `tracker.linktypes.list`, shown as plain text. See `CONTRIBUTING.md` for the intentional exclusions (UI-only endpoints with no public REST API) and per-method notes.

### Against the published API

What ycli sends, replayed from its contract tests, compared with what Yandex publishes: the Wiki, Forms and DataLens OpenAPI documents and Tracker's API reference (prose, so only operations and the query parameters a page lists are compared). A request body is compared only where ycli has a typed model for it and the model is closed; the **Bodies compared** column says how many that is, so an empty list is not read as a match. The published side is the snapshot in [`scripts/api_snapshot/`](scripts/api_snapshot); a [weekly job](.github/workflows/api-drift.yml) fetches it again and opens an issue when Yandex has changed it.

| Service | Published | Wrapped | Not wrapped | Operations that differ | Bodies compared | Source |
|---------|:---------:|:-------:|:-----------:|:----------------------:|:---------------:|--------|
| Tracker | 190 | 188 | 0 (+2 on purpose) | 0 | — | [API reference](https://yandex.ru/support/tracker/en/api/about-api) |
| Wiki | 56 | 56 | 0 | 0 | 24 of 24 | [OpenAPI](https://api.wiki.yandex.net/v1/openapi.json) |
| Forms | 84 | 84 | 0 | 8 | 26 of 30 | [OpenAPI](https://api.forms.yandex.net/v1/openapi.json) |
| DataLens | 141 | 73 | 0 (+7 on purpose) (+61 pending) | 0 | 71 of 71 | [OpenAPI](https://api.datalens.tech/json/) |

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
| `entities.attachments_download` | `GET /attachments/{file_id}/{filename}` |
| `linktypes.list` | `GET /linktypes` |

</details>

<details>
<summary><b>Wiki: what differs</b></summary>

</details>

<details>
<summary><b>Forms: what differs</b></summary>

**Parameters and fields**

| Operation | ycli | Difference | Why it stays |
|---|---|---|---|
| <a id="differs-forms-post-surveys"></a>`POST /surveys` | `surveys.create` | body fields ycli sends that are not published: `is_public`, `is_published`, `language`<br>model fields that are not published: `modified` | the API accepts it and ignores it (checked live on 2026-10-04)<br>the API returns it (checked live on 2026-10-04), the published schema omits it |
| <a id="differs-forms-get-surveys-survey-id"></a>`GET /surveys/{survey_id}` | `surveys.get` | model fields that are not published: `modified` | the API returns it (checked live on 2026-10-04), the published schema omits it |
| <a id="differs-forms-patch-surveys-survey-id"></a>`PATCH /surveys/{survey_id}` | `surveys.update` | body fields ycli sends that are not published: `is_public`, `is_published`, `language`<br>model fields that are not published: `modified` | the API accepts it and ignores it (checked live on 2026-10-04)<br>the API returns it (checked live on 2026-10-04), the published schema omits it |
| <a id="differs-forms-post-surveys-survey-id-hooks-hook-id-subscriptions"></a>`POST /surveys/{survey_id}/hooks/{hook_id}/subscriptions` | `subscriptions.create` | body fields ycli sends that are not published: `id` | one model builds the body and reads the reply, which carries `id` |
| <a id="differs-forms-patch-surveys-survey-id-hooks-hook-id-subscriptions-subscription-id"></a>`PATCH /surveys/{survey_id}/hooks/{hook_id}/subscriptions/{subscription_id}` | `subscriptions.update` | body fields ycli sends that are not published: `id` | one model builds the body and reads the reply, which carries `id` |
| <a id="differs-forms-post-surveys-survey-id-questions"></a>`POST /surveys/{survey_id}/questions` | `questions.create` | body fields ycli sends that are not published: `id` | the API accepts it and ignores it (checked live on 2026-10-04) |
| <a id="differs-forms-delete-surveys-survey-id-questions-question-id"></a>`DELETE /surveys/{survey_id}/questions/{question_id}` | `questions.delete` | query parameters ycli sends that are not published: `force` | the API accepts it and ignores it (checked live on 2026-10-04) |
| <a id="differs-forms-patch-surveys-survey-id-questions-question-id"></a>`PATCH /surveys/{survey_id}/questions/{question_id}` | `questions.update` | body fields ycli sends that are not published: `id` | the API accepts it and ignores it (checked live on 2026-10-04) |

</details>

<details>
<summary><b>DataLens: what differs</b></summary>

**Not wrapped on purpose**

| Operation | Why |
|---|---|
| [`POST /rpc/createFolder`](https://yandex.cloud/en/docs/datalens/api-ref/Folder/rpccreateFolder-post) | the old placement model (folders); the organization has none to check it on (#394) |
| [`POST /rpc/deleteFolder`](https://yandex.cloud/en/docs/datalens/api-ref/Folder/rpcdeleteFolder-post) | the old placement model (folders); the organization has none to check it on (#394) |
| [`POST /rpc/dlsSuggest`](https://yandex.cloud/en/docs/datalens/api-ref/Folder/rpcdlsSuggest-post) | the old placement model (folders); the organization has none to check it on (#394) |
| [`POST /rpc/getPermissions`](https://yandex.cloud/en/docs/datalens/api-ref/Folder/rpcgetPermissions-post) | the old placement model (folders); the organization has none to check it on (#394) |
| [`POST /rpc/listDirectory`](https://yandex.cloud/en/docs/datalens/api-ref/Navigation/rpclistDirectory-post) | the old placement model (folders); the organization has none to check it on (#394) |
| [`POST /rpc/modifyPermissions`](https://yandex.cloud/en/docs/datalens/api-ref/Folder/rpcmodifyPermissions-post) | the old placement model (folders); the organization has none to check it on (#394) |
| [`POST /rpc/moveFolderEntry`](https://yandex.cloud/en/docs/datalens/api-ref/Folder/rpcmoveFolderEntry-post) | the old placement model (folders); the organization has none to check it on (#394) |

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
