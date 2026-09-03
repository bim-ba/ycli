<div align="center">

# ycli

**One Yandex 360 toolkit — four ways to use it.**
Drive **Tracker**, **Wiki**, and **Forms** from a CLI, an MCP server, a Python SDK,
or a Claude Code plugin. Built for AI agents first — pleasant for humans too.

[![CI](https://img.shields.io/github/actions/workflow/status/bim-ba/ycli/ci.yml?branch=main&logo=githubactions&logoColor=white&label=ci)](https://github.com/bim-ba/ycli/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?logo=pytest&logoColor=white)](https://github.com/bim-ba/ycli)
[![PyPI](https://img.shields.io/pypi/v/yandex-cli?logo=pypi&logoColor=white&label=pypi)](https://pypi.org/project/yandex-cli/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey?logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/bim-ba/ycli)

<img src="https://raw.githubusercontent.com/bim-ba/ycli/main/docs/assets/demo.gif" alt="ycli in action" width="760">

</div>

- 🧩 **One SDK, four surfaces** — write logic once, use it as a CLI, an MCP server, a Python
  library, or a Claude Code plugin.
- 🤖 **Agent-native** — the MCP server exposes 240 MCP tools (239 domain-scoped read
  **and write** `tracker_*`, `wiki_*`, `forms_*` tools, one per SDK/CLI operation, plus a
  cross-cutting `status` tool) with honest annotations (reads are marked read-only; writes
  declare whether they are destructive/idempotent); `ycli mcp start --read-only` serves a
  reads-only view for cautious deployments.
- 🛡️ **Trustworthy** — typed pydantic models, the real Yandex API quirks handled for you,
  and a test suite kept at **100% coverage**.
- ⚡ **Zero-friction start** — `uv add yandex-cli`, `ycli auth login`, go.

## Install

```bash
uv add yandex-cli            # CLI + Python SDK
uv add 'yandex-cli[mcp]'     # …plus the MCP server (`ycli mcp start`)
```

Run it without installing, or install it as a standalone tool:

```bash
uvx yandex-cli --help                 # one-off, no install
uv tool install yandex-cli            # persistent CLI
uv tool install 'yandex-cli[mcp]'     # …with the MCP server
```

`pip install yandex-cli` works too. The CLI ships as both `yandex-cli` and the short `ycli`.

## Quick start

Pick the surface that fits how you work.

<details open>
<summary><b>CLI</b></summary>

```bash
uv add yandex-cli
ycli --help
ycli tracker issues get TRACKER-1
ycli wiki pages get onboarding
```

**Output formats** — a global `--format` / `-o` picks how results print:

```bash
ycli tracker issues get TRACKER-1            # auto: a pretty table on a TTY…
ycli tracker issues get TRACKER-1 | jq .     # …and raw JSON when piped (agent/script-safe)
ycli -o yaml wiki pages get onboarding       # or: -o json | -o yaml | -o pretty
```
</details>

<details>
<summary><b>MCP server</b> (read/write)</summary>

Run it over stdio (needs the `mcp` extra):

```bash
ycli mcp start               # full read/write tool set (honest annotations)
ycli mcp start --read-only   # reads-only view for cautious deployments
```

List the exposed tool names without running the server:

```bash
ycli mcp methods
```

Point an MCP client at it — no prior install needed via `uvx` (tools are namespaced
`tracker_*`, `wiki_*`, `forms_*`):

```json
{
  "mcpServers": {
    "yandex": {
      "command": "uvx",
      "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"],
      "env": {
        "YANDEX_ID_OAUTH_TOKEN": "...",
        "YANDEX_ID_ORGANIZATION_ID": "..."
      }
    }
  }
}
```
</details>

<details>
<summary><b>Python SDK</b></summary>

```python
from ycli.yandex.tracker.client import TrackerClient

tracker = TrackerClient(oauth_token="…", organization_id="…")
issue = tracker.issues.get("TRACKER-1")
print(issue.summary)
```
</details>

<details>
<summary><b>Claude Code plugin</b></summary>

```
/plugin marketplace add bim-ba/ycli
/plugin install yandex-360@ycli
```

Teaches an agent to drive Yandex 360 through `ycli` — including the real API quirks.
See [`plugins/yandex-360/`](plugins/yandex-360/).
</details>

## Skills (Claude Code plugin)

| Skill | Use for |
|-------|---------|
| `yandex-360` | Entry point — install + auth, pick a surface (CLI/MCP/SDK), route to a domain |
| `yandex-360-tracker` | Issues, epics, comments, transitions, links, worklog, changelog |
| `yandex-360-wiki` | Wiki pages, page tree, comments, attachments, YFM authoring |
| `yandex-360-forms` | Forms, questions/schema, responses, publishing |

The skills encode the read/write commands **and** the gnarly Yandex API quirks
(epic-vs-parent, transition discovery, permanent wiki slugs, `fields=` rules, Forms
host/header traps, answers pagination).

## Configure

`ycli` reads two values from the environment (or a `.env` file — `cp .env.example .env`):

```bash
YANDEX_ID_OAUTH_TOKEN=...        # a Yandex OAuth token with Tracker/Wiki/Forms access
YANDEX_ID_ORGANIZATION_ID=...    # your Yandex 360 organization id
```

ycli sends the org id as `X-Org-Id` for every service (HTTP header names are case-insensitive
per RFC 9110, so one casing serves all).

### Get your credentials

Yandex issues OAuth tokens only through a **registered application**, so it's a one-time
app registration plus one command.

**1. Register an OAuth app** at [oauth.yandex.ru](https://oauth.yandex.ru/client/new) and
grant it the **Tracker**, **Wiki**, and **Forms** permissions (read **and** write — the
CLI and the MCP server both write; the read scopes alone suffice only if you run the MCP
server with `ycli mcp start --read-only`). Put the **ClientID** — and the **Client secret**
if you want the headless flow — in your `.env` (ycli reads it from there):

```bash
YANDEX_OAUTH_CLIENT_ID=...        # from your app
YANDEX_OAUTH_CLIENT_SECRET=...    # optional — enables the headless device flow
```

**2. Log in.** `ycli auth login` gets a token, detects your organization, and writes both
into `.env`:

```bash
ycli auth login
```

- **client id + secret** → the **device flow**: ycli prints a code and a
  `https://ya.ru/device` link; approve there and it captures the token — no redirect, works
  over SSH.
- **only the client id** (or `--implicit`) → the **browser flow**: ycli opens the Yandex
  authorize page; approve, then copy the token it displays and paste it back.

<details>
<summary><b>Prefer to do it by hand?</b></summary>

**Headless (device flow):**

```bash
# 1. start the flow — returns a user_code + verification_url
curl -s -X POST https://oauth.yandex.ru/device/code -d "client_id=$YANDEX_OAUTH_CLIENT_ID"
# 2. open https://ya.ru/device, enter the user_code, approve
# 3. exchange the device_code for the token
curl -s -X POST https://oauth.yandex.ru/token \
  -d grant_type=device_code -d "code=<device_code>" \
  -d "client_id=$YANDEX_OAUTH_CLIENT_ID" -d "client_secret=$YANDEX_OAUTH_CLIENT_SECRET"
```

**Browser (implicit):** open
`https://oauth.yandex.ru/authorize?response_type=token&client_id=<ClientID>` in a logged-in
browser, approve, and copy the token from the page. (Plain `curl` can't — implicit needs an
interactive browser session.)

**Organization id:** [tracker.yandex.ru/admin/orgs](https://tracker.yandex.ru/admin/orgs) →
your organization → copy the identifier.
</details>

<!-- COVERAGE:START (generated by scripts/gen_coverage.py — do not edit by hand) -->
## Coverage

`ycli` wraps **249 operations across 51 resources** of the Tracker, Wiki, and Forms REST API — every one reachable from the **Python SDK** and the **CLI**, plus 240 **MCP** tools (239 domain-scoped + 1 cross-cutting: `status`) for agents.

> **Legend** — operations ship on **SDK + CLI**, and the **MCP** server mirrors them with honest annotations: reads carry `readOnlyHint`, writes carry explicit destructive/idempotent hints, and `ycli mcp start --read-only` serves the reads-only view. In each table **SDK** and **CLI** mean the operation is wrapped on that surface; **MCP** is ✅ when the resource exposes at least one MCP tool. Resource and operation names link to the official **Yandex API reference** (`yandex.ru/support/…/api-ref`). These tables are generated from the code by [`scripts/gen_coverage.py`](scripts/gen_coverage.py) — do not edit by hand.

### Tracker

**32 resources · 153 operations · 151 MCP tools**

#### Issues & work items

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [issues](https://yandex.ru/support/tracker/en/api-ref/issues/get-issue) | [get](https://yandex.ru/support/tracker/en/api-ref/issues/get-issue) · [search](https://yandex.ru/support/tracker/en/api-ref/issues/search-issues) · [count](https://yandex.ru/support/tracker/en/api-ref/issues/count-issues) · [create](https://yandex.ru/support/tracker/en/api-ref/issues/create-issue) · [update](https://yandex.ru/support/tracker/en/api-ref/issues/patch-issue) · [move](https://yandex.ru/support/tracker/en/api-ref/issues/move-issue) · [suggest](https://yandex.ru/support/tracker/en/api-ref/issues/get-suggest) · [scroll_clear](https://yandex.ru/support/tracker/en/api-ref/issues/search-release) | ✅ | ✅ | ✅ |
| [comments](https://yandex.ru/support/tracker/en/api-ref/issues/get-comments) | [list](https://yandex.ru/support/tracker/en/api-ref/issues/get-comments) · [add](https://yandex.ru/support/tracker/en/api-ref/issues/add-comment) · [edit](https://yandex.ru/support/tracker/en/api-ref/issues/edit-comment) · [delete](https://yandex.ru/support/tracker/en/api-ref/issues/delete-comment) · [react](https://yandex.ru/support/tracker/en/api-ref/issues/add-reaction-to-comment) | ✅ | ✅ | ✅ |
| [links](https://yandex.ru/support/tracker/en/api-ref/issues/get-links) | [list](https://yandex.ru/support/tracker/en/api-ref/issues/get-links) · [add](https://yandex.ru/support/tracker/en/api-ref/issues/link-issue) · [delete](https://yandex.ru/support/tracker/en/api-ref/issues/delete-link-issue) | ✅ | ✅ | ✅ |
| [transitions](https://yandex.ru/support/tracker/en/api-ref/issues/get-transitions) | [list](https://yandex.ru/support/tracker/en/api-ref/issues/get-transitions) · [execute](https://yandex.ru/support/tracker/en/api-ref/issues/new-transition) | ✅ | ✅ | ✅ |
| [worklog](https://yandex.ru/support/tracker/en/api-ref/issues/issue-worklog) | [list](https://yandex.ru/support/tracker/en/api-ref/issues/issue-worklog) · [search](https://yandex.ru/support/tracker/en/api-ref/issues/get-worklog) · [global_list](https://yandex.ru/support/tracker/en/api-ref/issues/get-worklog) · [create](https://yandex.ru/support/tracker/en/api-ref/issues/new-worklog) · [edit](https://yandex.ru/support/tracker/en/api-ref/issues/patch-worklog) · [delete](https://yandex.ru/support/tracker/en/api-ref/issues/delete-worklog) | ✅ | ✅ | ✅ |
| [changelog](https://yandex.ru/support/tracker/en/api-ref/issues/get-changelog) | [list](https://yandex.ru/support/tracker/en/api-ref/issues/get-changelog) | ✅ | ✅ | ✅ |
| [checklists](https://yandex.ru/support/tracker/en/api-ref/issues/get-checklist) | [get](https://yandex.ru/support/tracker/en/api-ref/issues/get-checklist) · [create](https://yandex.ru/support/tracker/en/api-ref/issues/add-checklist-item) · [edit](https://yandex.ru/support/tracker/en/api-ref/issues/edit-checklist) · [delete](https://yandex.ru/support/tracker/en/api-ref/issues/delete-checklist-item) · [clear](https://yandex.ru/support/tracker/en/api-ref/issues/delete-checklist) | ✅ | ✅ | ✅ |
| [attachments](https://yandex.ru/support/tracker/en/api-ref/issues/get-attachments-list) | [list](https://yandex.ru/support/tracker/en/api-ref/issues/get-attachments-list) · [download](https://yandex.ru/support/tracker/en/api-ref/issues/get-attachment) · [download_thumbnail](https://yandex.ru/support/tracker/en/api-ref/issues/get-attachment-preview) | ✅ | ✅ | ✅ |
| [remotelinks](https://yandex.ru/support/tracker/en/api-ref/issues/get-external-links) | [list](https://yandex.ru/support/tracker/en/api-ref/issues/get-external-links) · [create](https://yandex.ru/support/tracker/en/api-ref/issues/add-external-link) · [delete](https://yandex.ru/support/tracker/en/api-ref/issues/delete-external-link) | ✅ | ✅ | ✅ |

#### Agile boards

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [boards](https://yandex.ru/support/tracker/en/api-ref/boards/get-boards) | [list](https://yandex.ru/support/tracker/en/api-ref/boards/get-boards) · [get](https://yandex.ru/support/tracker/en/api-ref/boards/get-board) · [create](https://yandex.ru/support/tracker/en/api-ref/boards/post-board) · [edit](https://yandex.ru/support/tracker/en/api-ref/boards/patch-board) · [delete](https://yandex.ru/support/tracker/en/api-ref/boards/delete-board) | ✅ | ✅ | ✅ |
| [sprints](https://yandex.ru/support/tracker/en/api-ref/boards/get-sprints) | [list](https://yandex.ru/support/tracker/en/api-ref/boards/get-sprints) · [get](https://yandex.ru/support/tracker/en/api-ref/boards/get-sprint) · [create](https://yandex.ru/support/tracker/en/api-ref/boards/post-sprint) · [edit](https://yandex.ru/support/tracker/en/api-ref/boards/patch-sprint) · [delete](https://yandex.ru/support/tracker/en/api-ref/boards/delete-sprint) · [start](https://yandex.ru/support/tracker/en/api-ref/boards/start-sprint) · [archive](https://yandex.ru/support/tracker/en/api-ref/boards/archive-sprint) | ✅ | ✅ | ✅ |
| [columns](https://yandex.ru/support/tracker/en/api-ref/boards/get-columns) | [list](https://yandex.ru/support/tracker/en/api-ref/boards/get-columns) · [get](https://yandex.ru/support/tracker/en/api-ref/boards/get-column) · [create](https://yandex.ru/support/tracker/en/api-ref/boards/post-column) · [edit](https://yandex.ru/support/tracker/en/api-ref/boards/patch-column) · [delete](https://yandex.ru/support/tracker/en/api-ref/boards/delete-column) | ✅ | ✅ | ✅ |

#### Dictionaries

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [priorities](https://yandex.ru/support/tracker/en/api-ref/admin/get-priorities) | [list](https://yandex.ru/support/tracker/en/api-ref/admin/get-priorities) · [create](https://yandex.ru/support/tracker/en/api-ref/admin/create-priority) · [edit](https://yandex.ru/support/tracker/en/api-ref/admin/patch-priority) | ✅ | ✅ | ✅ |
| [statuses](https://yandex.ru/support/tracker/en/api-ref/admin/get-statuses) | [list](https://yandex.ru/support/tracker/en/api-ref/admin/get-statuses) · [create](https://yandex.ru/support/tracker/en/api-ref/admin/create-status) · [edit](https://yandex.ru/support/tracker/en/api-ref/admin/patch-status) | ✅ | ✅ | ✅ |
| [resolutions](https://yandex.ru/support/tracker/en/api-ref/admin/get-resolutions) | [list](https://yandex.ru/support/tracker/en/api-ref/admin/get-resolutions) · [create](https://yandex.ru/support/tracker/en/api-ref/admin/create-resolution) · [edit](https://yandex.ru/support/tracker/en/api-ref/admin/patch-resolution) | ✅ | ✅ | ✅ |
| [issuetypes](https://yandex.ru/support/tracker/en/api-ref/admin/get-issue-types) | [list](https://yandex.ru/support/tracker/en/api-ref/admin/get-issue-types) · [create](https://yandex.ru/support/tracker/en/api-ref/admin/create-issue-type) · [edit](https://yandex.ru/support/tracker/en/api-ref/admin/patch-issue-type) | ✅ | ✅ | ✅ |
| linktypes | list | ✅ | ✅ | ✅ |

#### Fields, queues & structure

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [fields](https://yandex.ru/support/tracker/en/api-ref/issues/get-global-fields) | [list](https://yandex.ru/support/tracker/en/api-ref/issues/get-global-fields) · [get](https://yandex.ru/support/tracker/en/api-ref/issues/get-issue-fields) · [create](https://yandex.ru/support/tracker/en/api-ref/issues/create-field) · [edit](https://yandex.ru/support/tracker/en/api-ref/issues/patch-issue-field-name) · [category_create](https://yandex.ru/support/tracker/en/api-ref/issues/create-issue-field-category) · [category_edit](https://yandex.ru/support/tracker/en/api-ref/issues/patch-issue-field-category) | ✅ | ✅ | ✅ |
| [localfields](https://yandex.ru/support/tracker/en/api-ref/queues/get-local-fields) | [list](https://yandex.ru/support/tracker/en/api-ref/queues/get-local-fields) · [get](https://yandex.ru/support/tracker/en/api-ref/queues/get-info-local-field) · [create](https://yandex.ru/support/tracker/en/api-ref/queues/create-local-field) · [edit](https://yandex.ru/support/tracker/en/api-ref/queues/edit-local-field) | ✅ | ✅ | ✅ |
| [components](https://yandex.ru/support/tracker/en/api-ref/queues/get-components) | [list](https://yandex.ru/support/tracker/en/api-ref/queues/get-components) · [create](https://yandex.ru/support/tracker/en/api-ref/queues/post-component) · [edit](https://yandex.ru/support/tracker/en/api-ref/queues/patch-component) | ✅ | ✅ | ✅ |
| [queues](https://yandex.ru/support/tracker/en/api-ref/queues/get-queues) | [list](https://yandex.ru/support/tracker/en/api-ref/queues/get-queues) · [get](https://yandex.ru/support/tracker/en/api-ref/queues/get-queue) · [tags](https://yandex.ru/support/tracker/en/api-ref/queues/get-tags) · [versions](https://yandex.ru/support/tracker/en/api-ref/queues/get-versions) · [fields](https://yandex.ru/support/tracker/en/api-ref/queues/get-fields) · [create](https://yandex.ru/support/tracker/en/api-ref/queues/create-queue) · [delete](https://yandex.ru/support/tracker/en/api-ref/queues/delete-queue) · [restore](https://yandex.ru/support/tracker/en/api-ref/queues/restore-queue) · [set_permissions](https://yandex.ru/support/tracker/en/api-ref/queues/manage-access) · [tag_remove](https://yandex.ru/support/tracker/en/api-ref/queues/delete-tag) · [version_create](https://yandex.ru/support/tracker/en/api-ref/queues/create-version) | ✅ | ✅ | ✅ |

#### Automation & bulk

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [macros](https://yandex.ru/support/tracker/en/api-ref/get-macroses) | [list](https://yandex.ru/support/tracker/en/api-ref/get-macroses) · [get](https://yandex.ru/support/tracker/en/api-ref/get-macros) · [create](https://yandex.ru/support/tracker/en/api-ref/post-macros) · [edit](https://yandex.ru/support/tracker/en/api-ref/patch-macros) · [delete](https://yandex.ru/support/tracker/en/api-ref/delete-macros) | ✅ | ✅ | ✅ |
| [triggers](https://yandex.ru/support/tracker/en/api-ref/queues/get-trigger) | [get](https://yandex.ru/support/tracker/en/api-ref/queues/get-trigger) · [create](https://yandex.ru/support/tracker/en/api-ref/queues/create-trigger) · [edit](https://yandex.ru/support/tracker/en/api-ref/queues/change-trigger) · [webhook_log](https://yandex.ru/support/tracker/en/api-ref/queues/view-trigger-logs) | ✅ | ✅ | ✅ |
| [autoactions](https://yandex.ru/support/tracker/en/api-ref/queues/get-autoaction) | [get](https://yandex.ru/support/tracker/en/api-ref/queues/get-autoaction) · [create](https://yandex.ru/support/tracker/en/api-ref/queues/create-autoaction) · [logs](https://yandex.ru/support/tracker/en/api-ref/queues/view-autoaction-logs) · [log_detail](https://yandex.ru/support/tracker/en/api-ref/queues/view-autoaction-logs) | ✅ | ✅ | ✅ |
| [dashboards](https://yandex.ru/support/tracker/en/api-ref/dashboards/create-dashboard) | [create](https://yandex.ru/support/tracker/en/api-ref/dashboards/create-dashboard) · [add_cycle_time_widget](https://yandex.ru/support/tracker/en/api-ref/dashboards/create-widget) | ✅ | ✅ | ✅ |
| [bulk](https://yandex.ru/support/tracker/en/api-ref/bulkchange/bulk-update-issues) | [update](https://yandex.ru/support/tracker/en/api-ref/bulkchange/bulk-update-issues) · [move](https://yandex.ru/support/tracker/en/api-ref/bulkchange/bulk-move-issues) · [transition](https://yandex.ru/support/tracker/en/api-ref/bulkchange/bulk-transition) · [get](https://yandex.ru/support/tracker/en/api-ref/bulkchange/bulk-move-info) · [issues](https://yandex.ru/support/tracker/en/api-ref/bulkchange/bulk-move-info) | ✅ | ✅ | ✅ |
| [import](https://yandex.ru/support/tracker/en/api-ref/import/import-ticket) | [task](https://yandex.ru/support/tracker/en/api-ref/import/import-ticket) · [comment](https://yandex.ru/support/tracker/en/api-ref/import/import-comments) · [link](https://yandex.ru/support/tracker/en/api-ref/import/import-links) · [worklog](https://yandex.ru/support/tracker/en/api-ref/import/import-worklogs) · [file](https://yandex.ru/support/tracker/en/api-ref/import/import-attachments) | ✅ | ✅ | ✅ |

#### Entities, users & search

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [entities](https://yandex.ru/support/tracker/en/api-ref/entities/about-entities) | [create](https://yandex.ru/support/tracker/en/api-ref/entities/create-entity) · [get](https://yandex.ru/support/tracker/en/api-ref/entities/get-entity) · [edit](https://yandex.ru/support/tracker/en/api-ref/entities/update-entity) · [delete](https://yandex.ru/support/tracker/en/api-ref/entities/delete-entity) · [search](https://yandex.ru/support/tracker/en/api-ref/entities/search-entities) · [history](https://yandex.ru/support/tracker/en/api-ref/entities/get-events-relative) · [permissions](https://yandex.ru/support/tracker/en/api-ref/entities/get-access) · [set_permissions](https://yandex.ru/support/tracker/en/api-ref/entities/patch-access) · [bulk_update](https://yandex.ru/support/tracker/en/api-ref/entities/bulkchange-entities) · [bulk_status](https://yandex.ru/support/tracker/en/api-ref/entities/bulkchange-entities) · [create_report](https://yandex.ru/support/tracker/en/api-ref/entities/about-entities) · [comments_list](https://yandex.ru/support/tracker/en/api-ref/entities/comments/get-all-comments) · [comments_relative](https://yandex.ru/support/tracker/en/api-ref/entities/comments/get-all-comments) · [comments_get](https://yandex.ru/support/tracker/en/api-ref/entities/comments/get-comment) · [comments_create](https://yandex.ru/support/tracker/en/api-ref/entities/comments/add-comment) · [comments_edit](https://yandex.ru/support/tracker/en/api-ref/entities/comments/patch-comment) · [comments_delete](https://yandex.ru/support/tracker/en/api-ref/entities/comments/delete-comment) · [checklists_create](https://yandex.ru/support/tracker/en/api-ref/entities/checklists/add-checklist) · [checklists_edit](https://yandex.ru/support/tracker/en/api-ref/entities/checklists/patch-checklist) · [checklists_edit_item](https://yandex.ru/support/tracker/en/api-ref/entities/checklists/patch-checklist-item) · [checklists_delete](https://yandex.ru/support/tracker/en/api-ref/entities/checklists/delete-checklist) · [checklists_delete_item](https://yandex.ru/support/tracker/en/api-ref/entities/checklists/delete-checklist-item) · [checklists_move](https://yandex.ru/support/tracker/en/api-ref/entities/checklists/move-checklist-item) · [links_list](https://yandex.ru/support/tracker/en/api-ref/entities/links/get-links) · [links_create](https://yandex.ru/support/tracker/en/api-ref/entities/links/add-links) · [links_delete](https://yandex.ru/support/tracker/en/api-ref/entities/links/delete-link) · [attachments_list](https://yandex.ru/support/tracker/en/api-ref/entities/attachments/get-all-attachments) · [attachments_get](https://yandex.ru/support/tracker/en/api-ref/entities/attachments/get-attachment) · [attachment_download](https://yandex.ru/support/tracker/en/api-ref/entities/about-entities) · [attachments_attach](https://yandex.ru/support/tracker/en/api-ref/entities/attachments/add-attachment) · [attachments_delete](https://yandex.ru/support/tracker/en/api-ref/entities/attachments/delete-attachment) | ✅ | ✅ | ✅ |
| [users](https://yandex.ru/support/tracker/en/api-ref/users/get-users) | [get](https://yandex.ru/support/tracker/en/api-ref/users/get-user) · [list](https://yandex.ru/support/tracker/en/api-ref/users/get-users) | ✅ | ✅ | ✅ |
| [applications](https://yandex.ru/support/tracker/en/api-ref/issues/get-applications) | [list](https://yandex.ru/support/tracker/en/api-ref/issues/get-applications) | ✅ | ✅ | ✅ |
| [filters](https://yandex.ru/support/tracker/en/api-ref/filters/get-filter) | [get](https://yandex.ru/support/tracker/en/api-ref/filters/get-filter) · [create](https://yandex.ru/support/tracker/en/api-ref/filters/create-filter) · [edit](https://yandex.ru/support/tracker/en/api-ref/filters/update-filter) | ✅ | ✅ | ✅ |
| [me](https://yandex.ru/support/tracker/en/api-ref/users/get-user-info) | [get](https://yandex.ru/support/tracker/en/api-ref/users/get-user-info) | ✅ | ✅ | ✅ |

### Wiki

**9 resources · 43 operations · 42 MCP tools**

#### Pages

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [pages](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) | [get_by_id](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details_by_id) · [get](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) · [descendants](https://yandex.ru/support/wiki/en/api-ref/pages/pages__descendants_by_slug) · [descendants_by_id](https://yandex.ru/support/wiki/en/api-ref/pages/pages__descendants_by_id) · [grids](https://yandex.ru/support/wiki/en/api-ref/pages/pages__page_grids) · [create](https://yandex.ru/support/wiki/en/api-ref/pages/pages__create_page) · [update](https://yandex.ru/support/wiki/en/api-ref/pages/pages__update_page_details) · [delete](https://yandex.ru/support/wiki/en/api-ref/pages/pages__delete_page) · [append_content](https://yandex.ru/support/wiki/en/api-ref/pages/pages__append_content) · [clone](https://yandex.ru/support/wiki/en/api-ref/pages/pages__clone_page) | ✅ | ✅ | ✅ |
| [resources](https://yandex.ru/support/wiki/en/api-ref/pagesresources/pagesresources__resources) | [list](https://yandex.ru/support/wiki/en/api-ref/pagesresources/pagesresources__resources) | ✅ | ✅ | ✅ |
| [recovery](https://yandex.ru/support/wiki/en/api-ref/recovery_tokens/recovery_tokens__recover_page_by_token) | [restore](https://yandex.ru/support/wiki/en/api-ref/recovery_tokens/recovery_tokens__recover_page_by_token) | ✅ | ✅ | ✅ |

#### Collaboration

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [comments](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__comments) | [list](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__comments) · [thread](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__thread_comments) · [create](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__create_comment) · [delete](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__delete_comment) | ✅ | ✅ | ✅ |
| [attachments](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) | [list](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) · [download](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__download_by_file_id) · [download_by_url](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__download_by_filename_slug_pair) · [delete](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__delete_attach) · [attach](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attach_file) · [upload](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) | ✅ | ✅ | ✅ |

#### Grids (dynamic tables)

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [grids](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) | [get](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) · [create](https://yandex.ru/support/wiki/en/api-ref/grids/grids__create_grid) · [update](https://yandex.ru/support/wiki/en/api-ref/grids/grids__update_grid) · [delete](https://yandex.ru/support/wiki/en/api-ref/grids/grids__delete_grid) · [add_rows](https://yandex.ru/support/wiki/en/api-ref/grids/grids__add_rows) · [remove_rows](https://yandex.ru/support/wiki/en/api-ref/grids/grids__remove_rows) · [move_rows](https://yandex.ru/support/wiki/en/api-ref/grids/grids__move_rows) · [add_columns](https://yandex.ru/support/wiki/en/api-ref/grids/grids__add_columns) · [remove_columns](https://yandex.ru/support/wiki/en/api-ref/grids/grids__remove_columns) · [move_columns](https://yandex.ru/support/wiki/en/api-ref/grids/grids__move_columns) · [update_cells](https://yandex.ru/support/wiki/en/api-ref/grids/grids__update_cells) · [clone](https://yandex.ru/support/wiki/en/api-ref/grids/grids__clone_grid) | ✅ | ✅ | ✅ |

#### Async & uploads

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [operations](https://yandex.ru/support/wiki/en/api-ref/operations/operations__get_clone_operation_status) | [clone_get](https://yandex.ru/support/wiki/en/api-ref/operations/operations__get_clone_operation_status) · [gridclone_get](https://yandex.ru/support/wiki/en/api-ref/operations/operations__get_clone_inline_grid_operation_status) | ✅ | ✅ | ✅ |
| [uploadsessions](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__create_upload_session) | [create](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__create_upload_session) · [get](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__get_upload_session) · [upload_part](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__upload_part) · [finish](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__complete_multipart_upload) · [abort](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__abort_multipart_upload) · [abort_all](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__abort_all) | ✅ | ✅ | ✅ |

#### Identity

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [me](https://yandex.ru/support/wiki/en/api-ref/users/users__me) | [get](https://yandex.ru/support/wiki/en/api-ref/users/users__me) | ✅ | ✅ | ✅ |

### Forms

**10 resources · 53 operations · 46 MCP tools**

#### Surveys & questions

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [surveys](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_surveys_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_surveys_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_survey_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_create_survey_public_view) · [modify](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_delete_survey_public_view) · [publish](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_publish_survey_public_view) · [unpublish](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_unpublish_survey_public_view) | ✅ | ✅ | ✅ |
| [questions](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_get_questions_public_view) | [get](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_get_question_public_view) · [list](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_get_questions_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_create_question_public_view) · [modify](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_modify_question_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_delete_question_public_view) · [move](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_move_question_public_view) | ✅ | ✅ | ✅ |
| [conditions](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_question_conditions_public_view) | [question_list](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_question_conditions_public_view) · [question_get](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_question_condition_public_view) · [question_create](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_create_question_condition_public_view) · [question_modify](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_modify_question_condition_public_view) · [question_delete](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_delete_question_condition_public_view) · [question_set_operator](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_patch_question_conditions_operator_public_view) · [page_list](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_page_conditions_public_view) · [page_get](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_page_condition_public_view) · [page_create](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_create_page_condition_public_view) · [page_modify](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_modify_page_condition_public_view) · [page_delete](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_delete_page_condition_public_view) · [page_set_operator](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_patch_page_conditions_operator_public_view) · [submit_list](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_submit_conditions_public_view) · [submit_get](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_submit_condition_public_view) · [submit_create](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_create_submit_condition_public_view) · [submit_modify](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_modify_submit_condition_public_view) · [submit_delete](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_delete_submit_condition_public_view) · [submit_set_operator](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_patch_submit_conditions_operator_public_view) | ✅ | ✅ | ✅ |

#### Responses & export

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [answers](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) | [get](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answer_public_view) · [list](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) · [list_all](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) · [export](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_export_answers_public_view) · [export_results](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_export_answers_results_public_view) · [download_export](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_export_answers_results_public_view) | ✅ | ✅ | ✅ |
| [operations](https://yandex.ru/support/forms/en/api-ref/operations/events_v1_views_operations_get_operation_view) | [get](https://yandex.ru/support/forms/en/api-ref/operations/events_v1_views_operations_get_operation_view) | ✅ | ✅ | ✅ |

#### Distribution

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [keysets](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_get_keysets_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_get_keysets_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_get_keyset_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_create_keyset_public_view) · [modify](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_modify_keyset_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_delete_keyset_public_view) · [download](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_download_keyset_public_view) | ✅ | ✅ | ✅ |
| [filling](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view) | [get](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view) · [submit](https://yandex.ru/support/forms/en/api-ref/filling/events_b2b_v1_views_surveys_submit_form_public_view) · [suggest](https://yandex.ru/support/forms/en/api-ref/filling/events_b2b_v1_views_surveys_get_suggest_public_view) | ✅ | ✅ | ✅ |

#### Media

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [files](https://yandex.ru/support/forms/en/api-ref/files/events_b2b_v1_views_files_get_file_public_view) | [upload](https://yandex.ru/support/forms/en/api-ref/files/events_b2b_v1_views_surveys_save_survey_file_public_view) · [verify](https://yandex.ru/support/forms/en/api-ref/files/events_b2b_v1_views_surveys_verify_file_public_view) · [download](https://yandex.ru/support/forms/en/api-ref/files/events_b2b_v1_views_files_get_file_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/files/events_b2b_v1_views_files_delete_file_public_view) | ✅ | ✅ | ✅ |
| [images](https://yandex.ru/support/forms/en/api-ref/images/events_b2b_v1_views_surveys_create_image_public_view) | [upload](https://yandex.ru/support/forms/en/api-ref/images/events_b2b_v1_views_surveys_create_image_public_view) | ✅ | ✅ | — |

#### Identity

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [me](https://yandex.ru/support/forms/en/api-ref/users/events_v1_views_users_get_user_view) | [get](https://yandex.ru/support/forms/en/api-ref/users/events_v1_views_users_get_user_view) | ✅ | ✅ | ✅ |

Every resource and operation above deep-links to the Yandex API reference: 245 of 249 operations resolve to their own endpoint page and 3 to their resource's page. No public API reference exists yet for `tracker.linktypes`, `tracker.linktypes.list`, shown as plain text. See `CONTRIBUTING.md` for the intentional exclusions (UI-only endpoints with no public REST API) and per-method notes.
<!-- COVERAGE:END -->

## Layout

```text
src/ycli/
├── cli/                # root Typer CLI  → `ycli` / `yandex-cli` (app · context · output)
├── mcp/                # root FastMCP server → `ycli mcp start` (read/write, `[mcp]` extra)
├── settings.py         # AppConfig + Credentials (pydantic-settings)
├── log.py              # central loguru config
└── yandex/
    ├── tracker/        # per-domain SDK …
    ├── wiki/           #   each resource group has:
    └── forms/          #   client.py · cli.py · mcp.py · models.py
plugins/yandex-360/     # distributable Claude Code plugin (skills + instructions)
references/             # vendored Yandex API reference docs (local-only; see references/README.md)
```

## Development

```bash
uv sync --all-extras   # --all-extras pulls in the `mcp` extra the tests exercise
uv run pytest          # 100% coverage gate; HTTP stubbed with `responses` (no live network)
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for conventions and how to add an endpoint.
Contributions welcome.

## License

[MIT](LICENSE) © 2026 Sava Znatnov
