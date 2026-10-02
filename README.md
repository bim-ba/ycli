<!-- mcp-name: io.github.bim-ba/ycli -->
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
- 🤖 **Agent-native** — the MCP server exposes read **and write** `tracker_*`, `wiki_*`,
  `forms_*` tools, one per SDK/CLI operation, plus a cross-cutting `status` tool (counts in
  [Coverage](#coverage)), with honest annotations (reads are marked read-only; writes
  declare whether they are destructive/idempotent); `ycli mcp start --read-only` serves a
  reads-only view for cautious deployments, and `--toolsets core` serves a curated everyday
  profile when a host limits how many tools it accepts.
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

Using an AI harness (Claude Code, Claude Desktop, Cursor, VS Code, Codex, Gemini CLI, opencode,
Docker)? See [Install in your harness](docs/install.md).

The SDK's `ServiceAccountAuth` (IAM tokens minted from a Yandex Cloud service-account key) needs
the `service-account` extra: `uv add 'yandex-cli[service-account]'`.

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

**Output formats** — a global `--format` / `-o` picks how results print (the global options work before or after the subcommand: `ycli -o json tracker issues get K` = `ycli tracker issues get K -o json`; a command that declares an option of its own, like `forms answers export --format`, keeps it):

```bash
ycli tracker issues get TRACKER-1            # auto: a pretty table on a TTY…
ycli tracker issues get TRACKER-1 | jq .     # …and raw JSON when piped (agent/script-safe)
ycli -o yaml wiki pages get onboarding       # or: -o json | -o yaml | -o pretty
ycli --jq .summary tracker issues get TRACKER-1   # filter the JSON with jq; a string prints bare
```

`--jq EXPR` runs a [jq](https://jqlang.org) program over the command's JSON result and prints
like `jq -r`: a string comes out raw, anything else as one compact JSON value per line. It
cannot be combined with `-o yaml` / `-o pretty`, and it needs the `jq` Python package (a
dependency; it has no build for Windows on ARM).

**Deleting asks first.** A command that destroys data (every `delete`, `clear`, `abort`…) asks
`DELETE <url> — this deletes data. Continue?` on stderr when you are at a terminal, and exits 1
if you decline. In a script, a pipe or CI there is no one to ask, so it fails with exit 2 until
you pass `--yes` / `-y`: `ycli tracker boards delete 7 --yes`. Reads and ordinary writes never ask.

**Preview a write.** `--dry-run` sends nothing for any write: it prints the request instead
(method, URL, body; never your token), through the same `-o` / `--jq` output, and exits 0.
Reads still run, so a command that reads and then writes shows its first write only:
`ycli tracker boards delete 7 --dry-run`. (The two commands that ask the API itself to validate
a request, `forms filling submit` and `wiki pages move`, call that `--validate-only`.)

**An endpoint ycli has not wrapped.** `ycli api PATH --service tracker|wiki|forms` calls it like
[`gh api`](https://cli.github.com/manual/gh_api) would, with the same auth, retries, output and exit codes:

```bash
ycli api issues/TRACKER-1 --service tracker --jq .summary           # GET (the default method)
ycli api issues/TRACKER-1/comments --service tracker -F text=@note.md   # POST: a field turns it into one
ycli api pages/descendants --service wiki -f slug=docs --paginate   # every page, as one JSON array
```

`PATH` is relative to the service's base URL; a full URL of a service needs no `--service`, and
any other host is refused (your token never goes elsewhere). `-f key=value` is a string, `-F` is
typed (`true`, `null`, numbers, JSON, `@file` for a file's text, `key[sub]=v` to nest, `key[]=v`
for an array); fields of a GET or DELETE go to the query string, otherwise to a JSON body (`--input
FILE` sends a raw body instead). `-H 'Name: value'` adds a header, `-X` sets the method, and
`--dry-run`, `--yes` and `--jq` behave as everywhere. `--paginate` works for Wiki only: Tracker and
Forms page their listings in more than one way, so pass `-f page=2` and the like yourself.
</details>

<details>
<summary><b>MCP server</b> (read/write)</summary>

Run it over stdio (needs the `mcp` extra):

```bash
ycli mcp start               # full read/write tool set (honest annotations)
ycli mcp start --read-only   # reads-only view for cautious deployments
```

Serving all 322 tools costs a large `tools/list` and some hosts cap a request (VS Code allows
128 tools), so pick what the session needs:

| Flag | Serves |
|---|---|
| `--toolsets tracker,wiki` | only those services (`tracker`, `wiki`, `forms`); default `all` |
| `--toolsets core` | a curated everyday profile of about 40 tools (issues, comments, transitions, worklog, wiki pages and search, form reads) |
| `--tools a,b` / `--exclude-tools a,b` | add or hide single tools by name (unknown names fail at start) |
| `--read-only` | no write tools; always wins over the flags above |
| `--tool-search` | lists a search tool and a call proxy instead of the tools; use it with a large set |

`status_get` is always served. The listing omits output schemas and doctest examples (results
still carry `structuredContent`), which cuts `tools/list` from about 1.9 MB to about 0.5 MB for
the full set.

List the tool names a given set of flags exposes without running the server:

```bash
ycli mcp methods --toolsets core --read-only
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

Optional settings follow the `YCLI__<GROUP>__<SETTING>` pattern; ycli rejects an invalid value
at startup and names the variable:

| Variable | Default | Meaning |
|---|---|---|
| `YCLI__HTTP__TIMEOUT_SECONDS` | `30` | Per-request timeout, seconds (> 0) |
| `YCLI__HTTP__RETRIES` | `3` | Retries for idempotent requests on 429/5xx (≥ 0) |
| `YCLI__HTTP__MAX_ITEMS` | `500` | Item cap for listings without `--limit`/`--all` (> 0) |
| `YCLI__LOGGING__LEVEL` | `WARNING` | `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`; `-v` means `INFO` (every HTTP request), `-vv` means `DEBUG` |
| `YCLI__LOGGING__FORMAT` | `text` | `text` or `json` (one object per line); logs always go to stderr |

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

Check it any time with `ycli auth status`: it shows whose token it is (from Yandex ID), your
organization (its name needs the optional `directory:read_organization` scope; without it you
get the id and a note) and whether each service accepts the token. `ycli tracker auth status`
(or `wiki`, `forms`) probes just that one service. Both exit non-zero when a service rejects
the token.

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

## Exit codes

A failed `ycli` command exits with a code that says what kind of failure it was, so a script can branch without parsing the message.

| Code | Meaning | When |
|---|---|---|
| 0 | ok | the command succeeded |
| 1 | failure | any other failure: a 4xx the API rejected, an unmapped error, a declined confirmation |
| 2 | usage | a bad command line or an invalid `YCLI__…` setting |
| 3 | not found | the API answered 404 (or the token cannot see the object) |
| 4 | auth | 401 / 403, or no credentials set |
| 5 | rate limited | the API answered 429 and the retries ran out (the hint shows `Retry-After`) |
| 6 | transient | a 5xx, a timeout or a lost connection: worth retrying later |

<!-- COVERAGE:START (generated by scripts/gen_coverage.py — do not edit by hand) -->
## Coverage

`ycli` wraps **334 operations across 62 resources** of the Tracker, Wiki, and Forms REST API — every one reachable from the **Python SDK** and the **CLI**, plus 322 **MCP** tools (321 domain-scoped + 1 cross-cutting: `status`) for agents.

> **Legend** — operations ship on **SDK + CLI**, and the **MCP** server mirrors them with honest annotations: reads carry `readOnlyHint`, writes carry explicit destructive/idempotent hints, and `ycli mcp start --read-only` serves the reads-only view. In each table **SDK** and **CLI** mean the operation is wrapped on that surface; **MCP** is ✅ when the resource exposes at least one MCP tool. Resource and operation names link to the official **Yandex API reference** (`yandex.ru/support/…/api-ref`). These tables are generated from the code by [`scripts/gen_coverage.py`](scripts/gen_coverage.py) — do not edit by hand.

### Tracker

**35 resources · 190 operations · 187 MCP tools**

#### Issues & work items

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [issues](https://yandex.ru/support/tracker/en/api-ref/issues/get-issue) | [get](https://yandex.ru/support/tracker/en/api-ref/issues/get-issue) · [search](https://yandex.ru/support/tracker/en/api-ref/issues/search-issues) · [count](https://yandex.ru/support/tracker/en/api-ref/issues/count-issues) · [create](https://yandex.ru/support/tracker/en/api-ref/issues/create-issue) · [update](https://yandex.ru/support/tracker/en/api-ref/issues/patch-issue) · [move](https://yandex.ru/support/tracker/en/api-ref/issues/move-issue) · [suggest](https://yandex.ru/support/tracker/en/api-ref/issues/get-suggest) · [scroll_clear](https://yandex.ru/support/tracker/en/api-ref/issues/search-release) | ✅ | ✅ | ✅ |
| [comments](https://yandex.ru/support/tracker/en/api-ref/issues/get-comments) | [list](https://yandex.ru/support/tracker/en/api-ref/issues/get-comments) · [get](https://yandex.ru/support/tracker/en/api-ref/issues/get-comment) · [add](https://yandex.ru/support/tracker/en/api-ref/issues/add-comment) · [edit](https://yandex.ru/support/tracker/en/api-ref/issues/edit-comment) · [delete](https://yandex.ru/support/tracker/en/api-ref/issues/delete-comment) · [react](https://yandex.ru/support/tracker/en/api-ref/issues/add-reaction-to-comment) | ✅ | ✅ | ✅ |
| [links](https://yandex.ru/support/tracker/en/api-ref/issues/get-links) | [list](https://yandex.ru/support/tracker/en/api-ref/issues/get-links) · [search](https://yandex.ru/support/tracker/en/api-ref/issues/get-links-paginate) · [add](https://yandex.ru/support/tracker/en/api-ref/issues/link-issue) · [delete](https://yandex.ru/support/tracker/en/api-ref/issues/delete-link-issue) | ✅ | ✅ | ✅ |
| [transitions](https://yandex.ru/support/tracker/en/api-ref/issues/get-transitions) | [list](https://yandex.ru/support/tracker/en/api-ref/issues/get-transitions) · [execute](https://yandex.ru/support/tracker/en/api-ref/issues/new-transition) | ✅ | ✅ | ✅ |
| [worklog](https://yandex.ru/support/tracker/en/api-ref/issues/issue-worklog) | [list](https://yandex.ru/support/tracker/en/api-ref/issues/issue-worklog) · [search](https://yandex.ru/support/tracker/en/api-ref/issues/get-worklog) · [global_list](https://yandex.ru/support/tracker/en/api-ref/issues/get-worklog) · [create](https://yandex.ru/support/tracker/en/api-ref/issues/new-worklog) · [edit](https://yandex.ru/support/tracker/en/api-ref/issues/patch-worklog) · [delete](https://yandex.ru/support/tracker/en/api-ref/issues/delete-worklog) | ✅ | ✅ | ✅ |
| [changelog](https://yandex.ru/support/tracker/en/api-ref/issues/get-changelog) | [list](https://yandex.ru/support/tracker/en/api-ref/issues/get-changelog) | ✅ | ✅ | ✅ |
| [checklists](https://yandex.ru/support/tracker/en/api-ref/issues/get-checklist) | [get](https://yandex.ru/support/tracker/en/api-ref/issues/get-checklist) · [create](https://yandex.ru/support/tracker/en/api-ref/issues/add-checklist-item) · [edit](https://yandex.ru/support/tracker/en/api-ref/issues/edit-checklist) · [delete](https://yandex.ru/support/tracker/en/api-ref/issues/delete-checklist-item) · [clear](https://yandex.ru/support/tracker/en/api-ref/issues/delete-checklist) | ✅ | ✅ | ✅ |
| [attachments](https://yandex.ru/support/tracker/en/api-ref/issues/get-attachments-list) | [list](https://yandex.ru/support/tracker/en/api-ref/issues/get-attachments-list) · [download](https://yandex.ru/support/tracker/en/api-ref/issues/get-attachment) · [download_thumbnail](https://yandex.ru/support/tracker/en/api-ref/issues/get-attachment-preview) · [get](https://yandex.ru/support/tracker/en/api-ref/issues/get-attachment-info) · [delete](https://yandex.ru/support/tracker/en/api-ref/issues/delete-attachment) · [upload](https://yandex.ru/support/tracker/en/api-ref/issues/post-attachment) · [upload_temp](https://yandex.ru/support/tracker/en/api-ref/issues/temp-attachment) | ✅ | ✅ | ✅ |
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
| [components](https://yandex.ru/support/tracker/en/api-ref/queues/get-components) | [list](https://yandex.ru/support/tracker/en/api-ref/queues/get-components) · [create](https://yandex.ru/support/tracker/en/api-ref/queues/post-component) · [edit](https://yandex.ru/support/tracker/en/api-ref/queues/patch-component) · [list_for_queue](https://yandex.ru/support/tracker/en/api-ref/queues/get-queue-components) · [get](https://yandex.ru/support/tracker/en/api-ref/queues/get-component) · [delete](https://yandex.ru/support/tracker/en/api-ref/queues/delete-component) · [user_permissions](https://yandex.ru/support/tracker/en/api-ref/queues/get-component-user-access) · [group_permissions](https://yandex.ru/support/tracker/en/api-ref/queues/get-component-group-access) | ✅ | ✅ | ✅ |
| [queues](https://yandex.ru/support/tracker/en/api-ref/queues/get-queues) | [list](https://yandex.ru/support/tracker/en/api-ref/queues/get-queues) · [get](https://yandex.ru/support/tracker/en/api-ref/queues/get-queue) · [tags](https://yandex.ru/support/tracker/en/api-ref/queues/get-tags) · [versions](https://yandex.ru/support/tracker/en/api-ref/queues/get-versions) · [fields](https://yandex.ru/support/tracker/en/api-ref/queues/get-fields) · [create](https://yandex.ru/support/tracker/en/api-ref/queues/create-queue) · [delete](https://yandex.ru/support/tracker/en/api-ref/queues/delete-queue) · [restore](https://yandex.ru/support/tracker/en/api-ref/queues/restore-queue) · [set_permissions](https://yandex.ru/support/tracker/en/api-ref/queues/manage-access) · [tag_remove](https://yandex.ru/support/tracker/en/api-ref/queues/delete-tag) · [version_create](https://yandex.ru/support/tracker/en/api-ref/queues/create-version) · [version_get](https://yandex.ru/support/tracker/en/api-ref/queues/get-version) · [version_edit](https://yandex.ru/support/tracker/en/api-ref/queues/update-version) · [version_delete](https://yandex.ru/support/tracker/en/api-ref/queues/delete-version) · [user_permissions](https://yandex.ru/support/tracker/en/api-ref/queues/get-user-access) · [group_permissions](https://yandex.ru/support/tracker/en/api-ref/queues/get-group-access) | ✅ | ✅ | ✅ |
| [workflows](https://yandex.ru/support/tracker/en/api-ref/queues/workflows/get-workflows) | [list](https://yandex.ru/support/tracker/en/api-ref/queues/workflows/get-workflows) · [get](https://yandex.ru/support/tracker/en/api-ref/queues/workflows/get-workflow) · [for_queue](https://yandex.ru/support/tracker/en/api-ref/queues/workflows/get-queue-workflows) · [create](https://yandex.ru/support/tracker/en/api-ref/queues/workflows/post-workflow) · [edit](https://yandex.ru/support/tracker/en/api-ref/queues/workflows/patch-workflow) · [edit_action](https://yandex.ru/support/tracker/en/api-ref/queues/workflows/patch-workflow-action) · [delete](https://yandex.ru/support/tracker/en/api-ref/queues/workflows/delete-workflow) | ✅ | ✅ | ✅ |
| [projects](https://yandex.ru/support/tracker/en/api-ref/projects/get-projects) | [list](https://yandex.ru/support/tracker/en/api-ref/projects/get-projects) · [get](https://yandex.ru/support/tracker/en/api-ref/projects/get-project) · [queues](https://yandex.ru/support/tracker/en/api-ref/projects/get-project-queues) · [create](https://yandex.ru/support/tracker/en/api-ref/projects/create-project) · [edit](https://yandex.ru/support/tracker/en/api-ref/projects/update-project) · [delete](https://yandex.ru/support/tracker/en/api-ref/projects/delete-project) | ✅ | ✅ | ✅ |

#### Automation & bulk

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [macros](https://yandex.ru/support/tracker/en/api-ref/get-macroses) | [list](https://yandex.ru/support/tracker/en/api-ref/get-macroses) · [get](https://yandex.ru/support/tracker/en/api-ref/get-macros) · [create](https://yandex.ru/support/tracker/en/api-ref/post-macros) · [edit](https://yandex.ru/support/tracker/en/api-ref/patch-macros) · [delete](https://yandex.ru/support/tracker/en/api-ref/delete-macros) | ✅ | ✅ | ✅ |
| [triggers](https://yandex.ru/support/tracker/en/api-ref/queues/get-trigger) | [list](https://yandex.ru/support/tracker/en/api-ref/queues/get-triggers) · [get](https://yandex.ru/support/tracker/en/api-ref/queues/get-trigger) · [create](https://yandex.ru/support/tracker/en/api-ref/queues/create-trigger) · [edit](https://yandex.ru/support/tracker/en/api-ref/queues/change-trigger) · [webhook_log](https://yandex.ru/support/tracker/en/api-ref/queues/view-trigger-logs) | ✅ | ✅ | ✅ |
| [autoactions](https://yandex.ru/support/tracker/en/api-ref/queues/get-autoaction) | [get](https://yandex.ru/support/tracker/en/api-ref/queues/get-autoaction) · [create](https://yandex.ru/support/tracker/en/api-ref/queues/create-autoaction) · [logs](https://yandex.ru/support/tracker/en/api-ref/queues/view-autoaction-logs) · [log_detail](https://yandex.ru/support/tracker/en/api-ref/queues/view-autoaction-logs) | ✅ | ✅ | ✅ |
| [dashboards](https://yandex.ru/support/tracker/en/api-ref/dashboards/create-dashboard) | [create](https://yandex.ru/support/tracker/en/api-ref/dashboards/create-dashboard) · [add_cycle_time_widget](https://yandex.ru/support/tracker/en/api-ref/dashboards/create-widget) | ✅ | ✅ | ✅ |
| [bulk](https://yandex.ru/support/tracker/en/api-ref/bulkchange/bulk-update-issues) | [update](https://yandex.ru/support/tracker/en/api-ref/bulkchange/bulk-update-issues) · [move](https://yandex.ru/support/tracker/en/api-ref/bulkchange/bulk-move-issues) · [transition](https://yandex.ru/support/tracker/en/api-ref/bulkchange/bulk-transition) · [get](https://yandex.ru/support/tracker/en/api-ref/bulkchange/bulk-move-info) · [issues](https://yandex.ru/support/tracker/en/api-ref/bulkchange/bulk-move-info) | ✅ | ✅ | ✅ |
| [import](https://yandex.ru/support/tracker/en/api-ref/import/import-ticket) | [task](https://yandex.ru/support/tracker/en/api-ref/import/import-ticket) · [comment](https://yandex.ru/support/tracker/en/api-ref/import/import-comments) · [link](https://yandex.ru/support/tracker/en/api-ref/import/import-links) · [worklog](https://yandex.ru/support/tracker/en/api-ref/import/import-worklogs) · [file](https://yandex.ru/support/tracker/en/api-ref/import/import-attachments) · [comment_file](https://yandex.ru/support/tracker/en/api-ref/import/import-attachments) | ✅ | ✅ | ✅ |

#### Entities, users & search

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [entities](https://yandex.ru/support/tracker/en/api-ref/entities/about-entities) | [create](https://yandex.ru/support/tracker/en/api-ref/entities/create-entity) · [get](https://yandex.ru/support/tracker/en/api-ref/entities/get-entity) · [edit](https://yandex.ru/support/tracker/en/api-ref/entities/update-entity) · [delete](https://yandex.ru/support/tracker/en/api-ref/entities/delete-entity) · [search](https://yandex.ru/support/tracker/en/api-ref/entities/search-entities) · [history](https://yandex.ru/support/tracker/en/api-ref/entities/get-events-relative) · [permissions](https://yandex.ru/support/tracker/en/api-ref/entities/get-access) · [set_permissions](https://yandex.ru/support/tracker/en/api-ref/entities/patch-access) · [direct_permissions](https://yandex.ru/support/tracker/en/api-ref/entities/get-permissions) · [set_direct_permissions](https://yandex.ru/support/tracker/en/api-ref/entities/patch-permissions) · [bulk_update](https://yandex.ru/support/tracker/en/api-ref/entities/bulkchange-entities) · [bulk_status](https://yandex.ru/support/tracker/en/api-ref/entities/bulkchange-entities) · [create_report](https://yandex.ru/support/tracker/en/api-ref/entities/about-entities) · [comments_list](https://yandex.ru/support/tracker/en/api-ref/entities/comments/get-all-comments) · [comments_relative](https://yandex.ru/support/tracker/en/api-ref/entities/comments/get-all-comments) · [comments_get](https://yandex.ru/support/tracker/en/api-ref/entities/comments/get-comment) · [comments_create](https://yandex.ru/support/tracker/en/api-ref/entities/comments/add-comment) · [comments_edit](https://yandex.ru/support/tracker/en/api-ref/entities/comments/patch-comment) · [comments_delete](https://yandex.ru/support/tracker/en/api-ref/entities/comments/delete-comment) · [checklists_create](https://yandex.ru/support/tracker/en/api-ref/entities/checklists/add-checklist) · [checklists_edit](https://yandex.ru/support/tracker/en/api-ref/entities/checklists/patch-checklist) · [checklists_edit_item](https://yandex.ru/support/tracker/en/api-ref/entities/checklists/patch-checklist-item) · [checklists_delete](https://yandex.ru/support/tracker/en/api-ref/entities/checklists/delete-checklist) · [checklists_delete_item](https://yandex.ru/support/tracker/en/api-ref/entities/checklists/delete-checklist-item) · [checklists_move](https://yandex.ru/support/tracker/en/api-ref/entities/checklists/move-checklist-item) · [links_list](https://yandex.ru/support/tracker/en/api-ref/entities/links/get-links) · [links_create](https://yandex.ru/support/tracker/en/api-ref/entities/links/add-links) · [links_delete](https://yandex.ru/support/tracker/en/api-ref/entities/links/delete-link) · [attachments_list](https://yandex.ru/support/tracker/en/api-ref/entities/attachments/get-all-attachments) · [attachments_get](https://yandex.ru/support/tracker/en/api-ref/entities/attachments/get-attachment) · [attachment_download](https://yandex.ru/support/tracker/en/api-ref/entities/about-entities) · [attachments_attach](https://yandex.ru/support/tracker/en/api-ref/entities/attachments/add-attachment) · [attachments_delete](https://yandex.ru/support/tracker/en/api-ref/entities/attachments/delete-attachment) | ✅ | ✅ | ✅ |
| [users](https://yandex.ru/support/tracker/en/api-ref/users/get-users) | [get](https://yandex.ru/support/tracker/en/api-ref/users/get-user) · [list](https://yandex.ru/support/tracker/en/api-ref/users/get-users) | ✅ | ✅ | ✅ |
| [applications](https://yandex.ru/support/tracker/en/api-ref/issues/get-applications) | [list](https://yandex.ru/support/tracker/en/api-ref/issues/get-applications) | ✅ | ✅ | ✅ |
| [filters](https://yandex.ru/support/tracker/en/api-ref/filters/get-filter) | [get](https://yandex.ru/support/tracker/en/api-ref/filters/get-filter) · [create](https://yandex.ru/support/tracker/en/api-ref/filters/create-filter) · [edit](https://yandex.ru/support/tracker/en/api-ref/filters/update-filter) · [delete](https://yandex.ru/support/tracker/en/api-ref/filters/delete-filter) | ✅ | ✅ | ✅ |
| [gaps](https://yandex.ru/support/tracker/en/api-ref/gaps/post-gaps) | [create](https://yandex.ru/support/tracker/en/api-ref/gaps/post-gaps) · [search](https://yandex.ru/support/tracker/en/api-ref/gaps/search-gaps) · [delete](https://yandex.ru/support/tracker/en/api-ref/gaps/delete-gaps) | ✅ | ✅ | ✅ |
| [me](https://yandex.ru/support/tracker/en/api-ref/users/get-user-info) | [get](https://yandex.ru/support/tracker/en/api-ref/users/get-user-info) | ✅ | ✅ | ✅ |

### Wiki

**11 resources · 58 operations · 56 MCP tools**

#### Pages

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [pages](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) | [get_by_id](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details_by_id) · [get](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) · [descendants](https://yandex.ru/support/wiki/en/api-ref/pages/pages__descendants_by_slug) · [descendants_by_id](https://yandex.ru/support/wiki/en/api-ref/pages/pages__descendants_by_id) · [grids](https://yandex.ru/support/wiki/en/api-ref/pages/pages__page_grids) · [create](https://yandex.ru/support/wiki/en/api-ref/pages/pages__create_page) · [update](https://yandex.ru/support/wiki/en/api-ref/pages/pages__update_page_details) · [delete](https://yandex.ru/support/wiki/en/api-ref/pages/pages__delete_page) · [append_content](https://yandex.ru/support/wiki/en/api-ref/pages/pages__append_content) · [clone](https://yandex.ru/support/wiki/en/api-ref/pages/pages__clone_page) · [move](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) · [revisions](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) · [backlinks](https://yandex.ru/support/wiki/en/api-ref/pages/pages__get_page_details) | ✅ | ✅ | ✅ |
| [resources](https://yandex.ru/support/wiki/en/api-ref/pagesresources/pagesresources__resources) | [list](https://yandex.ru/support/wiki/en/api-ref/pagesresources/pagesresources__resources) | ✅ | ✅ | ✅ |
| [recovery](https://yandex.ru/support/wiki/en/api-ref/recovery_tokens/recovery_tokens__recover_page_by_token) | [restore](https://yandex.ru/support/wiki/en/api-ref/recovery_tokens/recovery_tokens__recover_page_by_token) | ✅ | ✅ | ✅ |
| [search](https://yandex.ru/support/wiki/en/api-ref/search/search__search) | [query](https://yandex.ru/support/wiki/en/api-ref/search/search__search) | ✅ | ✅ | ✅ |

#### Collaboration

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [comments](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__comments) | [list](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__comments) · [thread](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__thread_comments) · [thread_get](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__thread_comments) · [create](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__create_comment) · [delete](https://yandex.ru/support/wiki/en/api-ref/comments/pagescomments__delete_comment) | ✅ | ✅ | ✅ |
| [attachments](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) | [list](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) · [get](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) · [preview](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) · [download](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__download_by_file_id) · [download_by_url](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__download_by_filename_slug_pair) · [delete](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__delete_attach) · [attach](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attach_file) · [upload](https://yandex.ru/support/wiki/en/api-ref/attachments/pagesattachments__attachments) | ✅ | ✅ | ✅ |
| [access](https://yandex.ru/support/wiki/en/api-ref/pages_access/pagesaccess__create_page_access) | [create](https://yandex.ru/support/wiki/en/api-ref/pages_access/pagesaccess__create_page_access) · [update](https://yandex.ru/support/wiki/en/api-ref/pages_access/pagesaccess__update_page_access) · [delete](https://yandex.ru/support/wiki/en/api-ref/pages_access/pagesaccess__delete_page_access) · [clear](https://yandex.ru/support/wiki/en/api-ref/pages_access/pagesaccess__delete_page_accesses) | ✅ | ✅ | ✅ |

#### Grids (dynamic tables)

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [grids](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) | [get](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) · [create](https://yandex.ru/support/wiki/en/api-ref/grids/grids__create_grid) · [update](https://yandex.ru/support/wiki/en/api-ref/grids/grids__update_grid) · [delete](https://yandex.ru/support/wiki/en/api-ref/grids/grids__delete_grid) · [add_rows](https://yandex.ru/support/wiki/en/api-ref/grids/grids__add_rows) · [remove_rows](https://yandex.ru/support/wiki/en/api-ref/grids/grids__remove_rows) · [move_rows](https://yandex.ru/support/wiki/en/api-ref/grids/grids__move_rows) · [add_columns](https://yandex.ru/support/wiki/en/api-ref/grids/grids__add_columns) · [remove_columns](https://yandex.ru/support/wiki/en/api-ref/grids/grids__remove_columns) · [move_columns](https://yandex.ru/support/wiki/en/api-ref/grids/grids__move_columns) · [update_cells](https://yandex.ru/support/wiki/en/api-ref/grids/grids__update_cells) · [clone](https://yandex.ru/support/wiki/en/api-ref/grids/grids__clone_grid) · [suggest_column](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) · [update_column](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) · [update_row](https://yandex.ru/support/wiki/en/api-ref/grids/grids__get_grid) | ✅ | ✅ | ✅ |

#### Async & uploads

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [operations](https://yandex.ru/support/wiki/en/api-ref/operations/operations__get_clone_operation_status) | [clone_get](https://yandex.ru/support/wiki/en/api-ref/operations/operations__get_clone_operation_status) · [gridclone_get](https://yandex.ru/support/wiki/en/api-ref/operations/operations__get_clone_inline_grid_operation_status) · [move_get](https://yandex.ru/support/wiki/en/api-ref/operations/operations__get_clone_operation_status) | ✅ | ✅ | ✅ |
| [uploadsessions](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__create_upload_session) | [create](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__create_upload_session) · [get](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__get_upload_session) · [upload_part](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__upload_part) · [finish](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__complete_multipart_upload) · [abort](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__abort_multipart_upload) · [abort_all](https://yandex.ru/support/wiki/en/api-ref/upload_sessions/upload_sessions__abort_all) | ✅ | ✅ | ✅ |

#### Identity

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [me](https://yandex.ru/support/wiki/en/api-ref/users/users__me) | [get](https://yandex.ru/support/wiki/en/api-ref/users/users__me) | ✅ | ✅ | ✅ |

### Forms

**16 resources · 86 operations · 78 MCP tools**

#### Surveys & questions

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [surveys](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_surveys_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_surveys_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_survey_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_create_survey_public_view) · [modify](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_delete_survey_public_view) · [publish](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_publish_survey_public_view) · [unpublish](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_unpublish_survey_public_view) | ✅ | ✅ | ✅ |
| [questions](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_get_questions_public_view) | [get](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_get_question_public_view) · [list](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_get_questions_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_create_question_public_view) · [modify](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_modify_question_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_delete_question_public_view) · [move](https://yandex.ru/support/forms/en/api-ref/questions/events_b2b_v1_views_questions_move_question_public_view) | ✅ | ✅ | ✅ |
| [conditions](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_question_conditions_public_view) | [question_list](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_question_conditions_public_view) · [question_get](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_question_condition_public_view) · [question_create](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_create_question_condition_public_view) · [question_modify](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_modify_question_condition_public_view) · [question_delete](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_delete_question_condition_public_view) · [question_set_operator](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_patch_question_conditions_operator_public_view) · [page_list](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_page_conditions_public_view) · [page_get](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_page_condition_public_view) · [page_create](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_create_page_condition_public_view) · [page_modify](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_modify_page_condition_public_view) · [page_delete](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_delete_page_condition_public_view) · [page_set_operator](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_patch_page_conditions_operator_public_view) · [submit_list](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_submit_conditions_public_view) · [submit_get](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_get_submit_condition_public_view) · [submit_create](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_create_submit_condition_public_view) · [submit_modify](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_modify_submit_condition_public_view) · [submit_delete](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_delete_submit_condition_public_view) · [submit_set_operator](https://yandex.ru/support/forms/en/api-ref/display-conditions/events_b2b_v1_views_conditions_patch_submit_conditions_operator_public_view) · [hook_list](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_get_hook_conditions_public_view) · [hook_get](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_get_hook_condition_public_view) · [hook_create](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_create_hook_condition_public_view) · [hook_modify](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_modify_hook_condition_public_view) · [hook_delete](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_delete_hook_condition_public_view) · [hook_set_operator](https://yandex.ru/support/forms/en/api-ref/conditions/events_b2b_v1_views_conditions_patch_hook_conditions_operator_public_view) | ✅ | ✅ | ✅ |
| [access](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_permissions_get_access_public_view) | [get](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_permissions_get_access_public_view) · [set](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_permissions_update_access_public_view) · [grant](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_permissions_grant_access_public_view) · [revoke](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_permissions_revoke_access_public_view) | ✅ | ✅ | ✅ |
| [history](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_survey_history_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_survey_history_public_view) | ✅ | ✅ | ✅ |

#### Responses & export

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [answers](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) | [get](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answer_public_view) · [list](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) · [list_all](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) · [export](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_export_answers_public_view) · [export_results](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_export_answers_results_public_view) · [download_export](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_export_answers_results_public_view) · [integrations_list](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_answers_get_integrations_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) · [restore](https://yandex.ru/support/forms/en/api-ref/answers/events_b2b_v1_views_answers_get_answers_public_view) | ✅ | ✅ | ✅ |
| [operations](https://yandex.ru/support/forms/en/api-ref/operations/events_v1_views_operations_get_operation_view) | [get](https://yandex.ru/support/forms/en/api-ref/operations/events_v1_views_operations_get_operation_view) | ✅ | ✅ | ✅ |

#### Integrations

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [hooks](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_get_hooks_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_get_hooks_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_get_hook_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_create_hook_public_view) · [modify](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_modify_hook_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/groups/events_b2b_v1_views_hooks_delete_hook_public_view) | ✅ | ✅ | ✅ |
| [subscriptions](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_get_subscriptions_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_get_subscriptions_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_get_subscription_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_create_subscription_public_view) · [modify](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_modify_subscription_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_delete_subscription_public_view) · [attach](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_save_subscription_attachment_public_view) | ✅ | ✅ | ✅ |
| [variables](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_get_variables_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/hooks/events_b2b_v1_views_hooks_get_variables_public_view) | ✅ | ✅ | ✅ |
| [notifications](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_get_notifications_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_get_notifications_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_get_notification_public_view) · [status_get](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_get_notification_status_public_view) · [restart](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_restart_notification_public_view) · [cancel](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_notifications_cancel_notification_public_view) · [errors_list](https://yandex.ru/support/forms/en/api-ref/events/events_b2b_v1_views_surveys_get_visible_errors_public_view) | ✅ | ✅ | ✅ |

#### Distribution

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [keysets](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_get_keysets_public_view) | [list](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_get_keysets_public_view) · [get](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_get_keyset_public_view) · [create](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_create_keyset_public_view) · [modify](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_modify_keyset_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_delete_keyset_public_view) · [download](https://yandex.ru/support/forms/en/api-ref/keysets/events_b2b_v1_views_keysets_download_keyset_public_view) | ✅ | ✅ | ✅ |
| [filling](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view) | [get](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view) · [submit](https://yandex.ru/support/forms/en/api-ref/filling/events_b2b_v1_views_surveys_submit_form_public_view) · [suggest](https://yandex.ru/support/forms/en/api-ref/filling/events_b2b_v1_views_surveys_get_suggest_public_view) | ✅ | ✅ | ✅ |

#### Media

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [files](https://yandex.ru/support/forms/en/api-ref/files/events_b2b_v1_views_files_get_file_public_view) | [upload](https://yandex.ru/support/forms/en/api-ref/files/events_b2b_v1_views_surveys_save_survey_file_public_view) · [verify](https://yandex.ru/support/forms/en/api-ref/files/events_b2b_v1_views_surveys_verify_file_public_view) · [download](https://yandex.ru/support/forms/en/api-ref/files/events_b2b_v1_views_files_get_file_public_view) · [delete](https://yandex.ru/support/forms/en/api-ref/files/events_b2b_v1_views_files_delete_file_public_view) | ✅ | ✅ | ✅ |
| [images](https://yandex.ru/support/forms/en/api-ref/images/events_b2b_v1_views_surveys_create_image_public_view) | [upload](https://yandex.ru/support/forms/en/api-ref/images/events_b2b_v1_views_surveys_create_image_public_view) · [clone](https://yandex.ru/support/forms/en/api-ref/images/events_b2b_v1_views_surveys_create_image_public_view) | ✅ | ✅ | ✅ |

#### Identity

| Resource | Operations | SDK | CLI | MCP |
|----------|------------|:---:|:---:|:---:|
| [me](https://yandex.ru/support/forms/en/api-ref/users/events_v1_views_users_get_user_view) | [get](https://yandex.ru/support/forms/en/api-ref/users/events_v1_views_users_get_user_view) | ✅ | ✅ | ✅ |

Every resource and operation above deep-links to the Yandex API reference: 318 of 334 operations resolve to their own endpoint page and 15 to their resource's page. No public API reference exists yet for `tracker.linktypes`, `tracker.linktypes.list`, shown as plain text. See `CONTRIBUTING.md` for the intentional exclusions (UI-only endpoints with no public REST API) and per-method notes.
<!-- COVERAGE:END -->

## Layout

```text
src/ycli/
├── cli/                # root Typer CLI  → `ycli` / `yandex-cli` (app · context · output)
├── mcp/                # root FastMCP server → `ycli mcp start` (read/write, `[mcp]` extra)
├── settings.py         # AppConfig + Credentials (pydantic-settings)
├── log.py              # stderr logging setup (stdlib)
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
uv run pytest          # 100% coverage gate; HTTP stubbed with `MockAPI` (no live network)
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for conventions and how to add an endpoint.
Contributions welcome.

## License

[MIT](LICENSE) © 2026 Sava Znatnov
