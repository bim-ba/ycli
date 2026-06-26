---
name: yandex-360-tracker
description: Use when reading from or writing to Yandex Tracker via the ycli tool — look up an issue/epic/comment/changelog/worklog, search issues with Tracker Query Language, count matches, or create/update/transition/link/comment on issues. Covers the CLI (`uv run ycli tracker …`), the read-only `tracker_*` MCP tools, and the Python SDK. Reach for it whenever a task mentions a Tracker issue key (e.g. MYQUEUE-123), an epic, a queue, or driving Yandex Tracker programmatically. Not for Yandex Wiki (use yandex-360-wiki) or Yandex Forms (use yandex-360-forms).
category: workflow
---

# Yandex Tracker (via ycli)

Drive Yandex Tracker through the `ycli` tool: read issues, comments, links,
changelog, worklog and transitions; search with Tracker Query Language; and create,
update, transition, link and comment on issues.

Three interfaces, same underlying API:

- **CLI** — `uv run ycli tracker <group> <cmd>`. Full read **and** write surface.
- **MCP tools** — 13 read-only tools named `tracker_<resource>_<action>`. No write tools.
- **Python SDK** — `from ycli.yandex.tracker.client import TrackerClient`.

**Prefer the CLI or the `tracker_*` MCP tools over raw `http` calls.** They handle
auth and output formatting consistently and surface the `epic` field that raw HTTP
users routinely miss. Raw `http` is only for endpoints the CLI does not cover.

## When to use

- Read context about existing work: "what is MYQUEUE-123 about", "what's open under
  epic EPIC-1", "what changed last week on MYQUEUE-42", "who is assigned across the
  queue", history of a transition, current assignees.
- Write: create a new issue, update fields, transition status, add a comment, link
  two issues.

You can read from any queue you have access to, and write to any queue where you have
permission.

## When NOT to use

- Reading or editing Yandex Wiki pages → use the `yandex-360-wiki` skill.
- Yandex Forms → use the `yandex-360-forms` skill.
- Changing Tracker workflow structure (statuses, transitions, required fields) — this
  is done in the Tracker admin UI only; the API cannot modify workflow structure.

## Authentication

The CLI, MCP tools, and SDK all read credentials from the environment:

| Env var | Purpose |
|---------|---------|
| `YANDEX_ID_OAUTH_TOKEN` | OAuth token → sent as `Authorization: OAuth …` |
| `YANDEX_ID_ORGANIZATION_ID` | Organization ID → sent as the `X-Org-ID` header |

Full API reference is vendored at `../../../docs/references/yandex/tracker/`. Start
from `../../../docs/references/yandex/tracker/index/docs.md` to find the right doc.

---

## Reading

All read commands accept any issue key or queue you can access. Each is also a
read-only MCP tool.

| CLI command | MCP tool | Purpose |
|-------------|----------|---------|
| `uv run ycli tracker issues get KEY` | `tracker_issues_get` | Compact view: key, summary, type, status, priority, **epic**, parent, assignee |
| `uv run ycli tracker issues full KEY` | `tracker_issues_full` | Full JSON — every field |
| `uv run ycli tracker issues list [--queue ...] [--status ...] [--assignee ...] [--epic ...] [--type ...]` | `tracker_issues_list` | Filtered list — all filters optional; pass none for everything you can read, any subset to narrow |
| `uv run ycli tracker issues search '...'` | `tracker_issues_search` | Full-text search via Tracker Query Language |
| `uv run ycli tracker issues count [--query '...'] [--queue X] [--status Y]` | `tracker_issues_count` | Count without listing — sanity-check a filter first. `--query` is mutually exclusive with `--queue`/`--status` |
| `uv run ycli tracker comments list KEY` | `tracker_comments_list` | List comments |
| `uv run ycli tracker links list KEY` | `tracker_links_list` | List links between issues |
| `uv run ycli tracker changelog list KEY` | `tracker_changelog_list` | Changelog: who changed what, when |
| `uv run ycli tracker worklog list KEY` | `tracker_worklog_list` | Time-tracking entries |
| `uv run ycli tracker transitions list KEY` | `tracker_transitions_list` | Available transitions (a read — used before a write) |

The 13 read-only MCP tools are: `tracker_issues_get`, `tracker_issues_full`,
`tracker_issues_list`, `tracker_issues_search`, `tracker_issues_count`,
`tracker_comments_list`, `tracker_links_list`, `tracker_changelog_list`,
`tracker_worklog_list`, `tracker_transitions_list`, `tracker_priorities_list`,
`tracker_linktypes_list`, `tracker_issuetypes_list`. Write operations are CLI-only.

### Search — Tracker Query Language

`issues search` takes a TQL string. Examples:

```bash
uv run ycli tracker issues search '"parcels"'                          # full-text, all queues
uv run ycli tracker issues search 'Queue: MYQUEUE AND "parcels"'       # scoped to a queue
uv run ycli tracker issues search 'Assignee: <your-login> AND Updated: today()'
uv run ycli tracker issues search 'Tags: "data-product"'
```

### Discovery helpers — run BEFORE building a write payload

These return the valid enum values for your installation — call them instead of
guessing:

| Command | MCP tool | Returns |
|---------|----------|---------|
| `uv run ycli tracker priorities list` | `tracker_priorities_list` | Valid priority keys (commonly `trivial` / `minor` / `normal` / `critical` / `blocker`). **`high` is not a key.** |
| `uv run ycli tracker issuetypes list` | `tracker_issuetypes_list` | Valid type keys for the queue. For the Primary workflow: `epic` / `story` / `improvement` / `refactoring` / `newFeature` / `bug` / `incident` (`task` is a Quick Start type — see `rules/01-workflow.md`) |
| `uv run ycli tracker linktypes list` | `tracker_linktypes_list` | Valid link relationship IDs — note `"epic"` is listed but is NOT creatable via the links API (see Quirks) |

### Caveats — reads that look like more than they are

- **`transitions list KEY`** returns only the transitions available from the issue's
  **current** status — a slice of the workflow, not the whole workflow.
- **`--status` is LITERAL.** `--status open` matches only the status key `open` (Quick
  Start workflow) — it is NOT a synonym for "all active". In the Primary workflow the
  active statuses are `backlog` / `inProgress` / `inReview` / `blockedGoal` / `onHold`,
  none of which match `--status open`. For "all active", drop the `--status` filter and
  post-filter with `jq`, e.g.
  `jq '.[] | select(.status.key != "closed" and .status.key != "cancelled")'`. If a
  query you expect to return many returns 1, suspect filter semantics.
- **`linktypes list`** shows every link type Tracker recognises for reading — not
  whether each is creatable via `POST /links`.

When you are uncertain about the full workflow structure, say so — do not infer it
from `transitions list` output and present the inference as fact. See
`rules/01-workflow.md` for the Primary-workflow reference.

---

## Writing

Writes are CLI-only. Target any queue where you have permission.

### Create an issue

1. **Pick the issue type** — see `rules/01-workflow.md`. For Primary-workflow queues
   use `epic` / `story` / `improvement` / `refactoring` / `newFeature` / `bug` /
   `incident`; avoid `task` (Quick Start).
2. **Discover valid field values** with the discovery helpers above — don't guess.
3. **Create**, supplying summary and description explicitly:

   ```bash
   uv run ycli tracker issues create \
     --queue MYQUEUE \
     --type improvement \
     --priority normal \
     --parent EPIC-1 \
     --summary "Short title" \
     --description "$(cat /tmp/desc.md)"
   ```

   `--priority` defaults to `normal`; `--parent` is optional (omit for top-level
   issues). Use `-F key=value` (repeatable) for any field without a named flag.

4. **If creating under an Epic, set the `epic` field immediately** (see Quirks):

   ```bash
   uv run ycli tracker issues update <created-key> -F 'epic={"key":"EPIC-1"}'
   ```

5. **Verify** with `uv run ycli tracker issues get KEY` — confirm type, priority,
   queue, `parent`, and `epic`.

### Update fields

```bash
uv run ycli tracker issues update MYQUEUE-123 \
  --priority critical \
  -F storyPoints=5 \
  -F assignee=<your-login>
```

Only `--summary` / `--type` / `--priority` / `--parent` / `--description` / `--tag`
have named flags. Every other field (`assignee`, `end_date`, `storyPoints`, `epic`, …)
goes through the repeatable `-F key=value` JSON-coerce hatch: bare integers stay
integers, quoted strings stay strings, `{...}` / `[...]` are parsed as JSON.

### Transition status

```bash
uv run ycli tracker transitions list MYQUEUE-123                  # discover IDs FIRST
uv run ycli tracker transitions execute MYQUEUE-123 <id> [-F key=value …]
```

Never guess transition IDs and never execute a transition not in the available list
(returns 400). Required fields per transition (e.g. `resolution` on close) are in
`rules/01-workflow.md`. Set `assignee` (and a due/end date) at or before moving to
In Progress:

```bash
uv run ycli tracker issues update MYQUEUE-123 -F assignee=<your-login> -F end_date='YYYY-MM-DD'
```

Closing to `closed` (Done) requires a `resolution`:

```bash
uv run ycli tracker transitions execute MYQUEUE-123 closed -F 'resolution={"key":"fixed"}'
```

### Add a comment

```bash
uv run ycli tracker comments add MYQUEUE-123 --text "$(cat comment.md)"
```

### Link issues

```bash
uv run ycli tracker linktypes list                               # discover valid phrases first
uv run ycli tracker links add MYQUEUE-130 'depends on' MYQUEUE-129
```

---

## Yandex Tracker quirks (the durable gotchas)

- **`epic` vs `parent` are different mechanisms.** When you create an issue with
  `--parent EPIC_KEY`, the result has `parent: EPIC_KEY` but `epic: null` — it will
  NOT appear in Epic board views or match `issues list --epic EPIC_KEY`. You must set
  the `epic` field explicitly:
  `uv run ycli tracker issues update KEY -F 'epic={"key":"EPIC-1"}'`. This is a
  mandatory second step for any Story/issue created under an Epic.
- **The "epic" link type is NOT creatable via `POST /links`.** `linktypes list` shows
  `"epic"`, but creating a link with `relationship: "epic"` returns 400. The only
  working method to associate an issue with an Epic is the `-F 'epic={"key":...}'`
  update above.
- **When `parent` and `epic` point to the same key, Tracker auto-clears `parent`**
  (the epic field takes precedence). For an issue under a Story, `parent` (→ Story) and
  `epic` (→ Epic) coexist correctly.
- **Always discover transition IDs** with `transitions list KEY` before
  `transitions execute` — IDs are suffixed per source status (`cancelled`,
  `cancelled1`, …) and depend on the current status.
- **`--status` is a literal key filter, not "all active"** (see Reading caveats).
- **`-F key=value` is the JSON-coerce escape hatch** for any field without a named flag
  — custom fields, story points, arbitrary metadata.
- **Discover enums before guessing** — `priorities list`, `issuetypes list`,
  `linktypes list`.
- **Primary vs Quick Start workflow:** type `task` belongs to Quick Start (initial
  status `open`). The Primary workflow uses `epic` / `story` / `improvement` /
  `refactoring` / `newFeature` / `bug` / `incident`, starts in `backlog`, and requires
  a `resolution` on close. See `rules/01-workflow.md`.
- **User objects in issue responses have no `login` field** — only `id` (numeric),
  `display`, and `cloudUid`. To get a login, call `GET /v3/users/{numericId}`
  separately. Never use `cloudUid` or `display` as a substitute for login.

---

## Python SDK

```python
from ycli.yandex.tracker.client import TrackerClient

client = TrackerClient.from_env()        # reads YANDEX_ID_* from the environment
issue = client.issues.get("MYQUEUE-123")
```

`TrackerClient` exposes one sub-client per resource, all sharing a session:
`issues`, `comments`, `links`, `transitions`, `worklog`, `changelog`, `priorities`,
`issuetypes`, `linktypes`. Search, count, full-fetch, create and update are methods on
`client.issues` (`issues.search`, `issues.count`, `issues.get_raw`, `issues.create`,
`issues.update`). Verify resource/method names against
`src/ycli/yandex/tracker/client.py` if in doubt.

---

## References

| Resource | When to use |
|----------|-------------|
| `rules/01-workflow.md` | Primary vs Quick Start workflow: types, statuses, lifecycle, transitions, resolution values |
| `references/taskfile-quick-ref.md` | Cheatsheet of all `uv run ycli tracker …` operations |
| `../../../docs/references/yandex/tracker/index/docs.md` | Navigation guide to the Yandex Tracker API docs |
| `../../../docs/references/yandex/tracker/{N}-{topic}/` | Full Yandex Tracker API docs by topic area |
