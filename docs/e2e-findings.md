# Live E2E validation — findings & defect log

A record of the **end-to-end runs of `ycli` against a real Yandex 360 organization**
(not the stubbed test suite): every domain exercised through the CLI, the Python SDK, and the
MCP tools, with full create→read→update→delete round-trips and cleanup. Two runs so far: the
first full pass (2026-07-10, below) and the full-surface re-test after the MCP server went
**read/write** (2026-07-12, [last section](#2026-07-12--full-surface-live-test-all-230-sdk-methods)).

> **Provenance.** Run **2026-07-10** on branch `feat/full-api-coverage` against a freshly
> created test org. Fixtures were created, exercised, and deleted; a handful of Tracker
> dictionary items have no DELETE endpoint and were left (see *Leftovers*). Credential values
> were never printed or committed.

## Coverage summary

| Domain | Resources | PASS | FAIL | SKIP | Real code defects |
|--------|:---------:|:----:|:----:|:----:|:-----------------:|
| Tracker | 32 | 105 (+1 partial) | 10 | 19 | 2 |
| Wiki | 9 | 44 | 0 | 0 | 3 |
| Forms | 9 | 28 | 4 | 2 | 4 |

Most FAIL/SKIP rows are **correct API behavior** (business-rule 422s, admin-gated features not
enabled on a fresh org, binary-storage preconditions) — not `ycli` bugs. The genuine code
defects are tracked below. Both Forms **inferred** signatures (`surveys.create` `POST /surveys`,
`surveys.modify` `PATCH /surveys/{id}`) were **confirmed correct** against the live API.

## Defect log

Severity: 🔴 crash · 🟠 wrong data / broken flow · 🟡 minor. Status as of this branch.

| # | Sev | Domain | Defect | File | Status |
|---|:---:|--------|--------|------|--------|
| 1 | 🔴 | Tracker | `Queue.id` typed `str`; live top-level `/queues/` returns an `int` → `queues create/get/list/restore` crash on parse | `tracker/queues/models.py` | ✅ Fixed — `str \| int \| None` |
| 2 | 🔴 | Tracker | `FieldProvider.values` typed `list[str]`; field `possibleSpam` returns `[0,1]` → `fields list` crashes | `tracker/fields/models.py` | ✅ Fixed — `list[str \| int]` |
| 3 | 🟠 | Wiki | grids `add_columns`: `required=None` dropped by `exclude_none` → API 400 on every column | `wiki/grids/models.py` | ✅ Fixed — default `required=False` |
| 4 | 🟠 | Wiki | comments list/thread render `content:null`/`author:null` (model read `content`/`display`, API sends `body`/`author.display_name`) | `wiki/comments/models.py`, `yandex/models.py` | ✅ Fixed — alias `body`→content, flatten `author.display_name` |
| 5 | 🟡 | Wiki | attachments list `size:0`/`mime_type:null` (API sends size as a string like `"0.00"`; key is `mimetype`) | `wiki/attachments/models.py` | ✅ Fixed — `size: str`, `mimetype` |
| 6 | 🟠 | Forms | `answers.get` (single answer) 404s at every version/path — the endpoint is **not deployed** on `api.forms.yandex.net` | `forms/answers/` | ✅ **Removed** (dead op, all surfaces) |
| 7 | 🟠 | Forms | `answers.export_results` forces `@returns.json()` on a `302`→CSV redirect → `JSONDecodeError`; broke `answers export --wait` | `forms/answers/client.py` | ✅ Fixed — treat followed redirect as terminal |
| 8 | 🟠 | Forms | `answers.list_all` / MCP drain followed a dead `/v3/…` `next_url` (HTML 404) | `forms/answers/client.py` | ✅ Fixed — rebuild the cursor on the working v1 path |
| 9 | 🟡 | Forms | `keysets.modify` (PATCH) requires the full record; help/`exclude_none` implied partial | `forms/keysets/{cli,client,models}.py` | ✅ Fixed — full body required; help corrected |

**All 9 resolved** in this branch (strict TDD, red→green confirmed, live-shape-verified, stubbed
tests, 100% coverage held): **8 fixed**, and **Bug 6 removed entirely** — no server endpoint
exists to call.

## Resolved follow-ups

- **Bug 6 — `answers.get`.** Removed the operation from SDK / CLI / MCP (every candidate path —
  v1/v2/v3, `{id}` and `{answer_key}`, trailing slash, `/answer/`, `?id=`, `?pk=` — returns a
  server-level HTML/plain 404, so the route simply is not deployed). Its unused model chain
  (`AnswerDetail` & friends) and the inaccurate `mcp.py` comment went with it; snapshots +
  coverage tables regenerated (Forms now **34 ops · 10 MCP tools**).
- **Wiki comment threading.** `comments thread` now reconstructs the thread **client-side** from
  the flat comment list — grouping by `parent_id` from the target to any depth (DFS, cycle-guarded)
  — instead of the dead `/thread` endpoint; `id` and `parent_id` were added to the comment model.
- **Keyset `create`.** Now requires and always sends `is_enabled` (mirrors the Bug 9 `modify` fix).

## Doc / skill drift

- Minor CLI-contract gaps where the API requires a flag the CLI marks optional: Tracker
  `worklog add --start`, `priorities create --order`, and `edit` ops needing `--version`
  (components/triggers). Low priority.

## Cross-cutting: MCP vs `.env` can point at different orgs

During this run the in-session MCP server authenticated to a **different** org than the CLI/SDK
`.env` (the MCP process kept an earlier session's token). All three E2E agents observed this
independently: CLI/SDK created fixtures in the `.env` org, so the MCP tools correctly 404'd on
them. The MCP *tools themselves* returned valid typed data against their own org. **Restart the
MCP server after changing `.env`** so both surfaces share one tenant.

## Leftovers (fresh test org)

Deleted everything create-able. Four Tracker dictionary items have **no DELETE endpoint** and
remain: a resolution, a status, a priority, and a global field (all `e2e*`-prefixed). The
`YCLITEST` queue was soft-deleted (async purge). These can only be removed via the Tracker admin
UI, if at all.

---

## 2026-07-12 — full-surface live test (all 230 SDK methods)

Run on branch `feat/mcp-read-write` (the branch that made the MCP server read/write, 222 tools)
against the same test org: **every one of the 230 SDK operations** exercised end-to-end via the
CLI, in five parallel sweeps (Forms; Wiki; Tracker core issue flow; Tracker admin; Tracker
entities/bulk/import/dashboards), each write verified by reading back the changed state, with
full sandbox cleanup.

**Verdicts: 237 OK rows · 7 `ycli` bugs · 1 upstream API bug** (the remaining rows were
expected failures from environment preconditions, e.g. Forms file uploads requiring external
S3 storage). Both previously "inferred" Forms signatures were re-confirmed against the live API.

### ycli bugs found (fixes landing on this same branch)

| # | Domain | Bug | Live symptom |
|---|--------|-----|--------------|
| 1 | Tracker | `sprints edit / start / archive` send no optimistic-locking version | HTTP 428 — the API requires `?version=` or `If-Match`; the CLI/SDK expose no `--version` for sprints (unlike triggers/components/statuses) |
| 2 | Tracker | `entities comments edit` PATCHes the comments *collection* route | HTTP 405 — the live API wants per-comment `PATCH …/comments/{comment_id}` (raw probe 200); the vendored doc page is stale |
| 3 | Tracker | `entities attachments delete` crashes on the empty response body | Server delete succeeds, then the CLI raises `JSONDecodeError` (`uplink.returns.json()` on a bodyless DELETE) |
| 4 | Tracker | `import worklog` parses the array response as a single `Worklog` | Server write succeeds, then pydantic validation error (`input_type=list`) |
| 5 | Wiki | `pages append` without `--location` sends no placement selector | HTTP 400 `VALIDATION_ERROR` («body/section/anchor mutually exclusive») — fix: default to bottom |
| 6 | Wiki | `grids columns add` claims per-column `slug` is server-generated | HTTP 400 `value_error.missing` unless every column carries an explicit `"slug"` |
| 7 | Wiki | `grids update --default-sort` dumps the *read* shape | The API writes a mapping list `[{"<column_slug>": "asc"}]`; the model emits `[{"slug","title","direction"}]` → 400 (and the correct shape gets stripped by pydantic) |

### Upstream (Yandex) API bug

- **Tracker entities checklist whole-replace** — `PATCH /v3/entities/{type}/{id}/checklistItems`
  returns **500 «Внутренняя ошибка»** even for a doc-conformant raw request; the per-item
  `edit-item` route works. Server-side, not a ycli defect.

Beyond the defects, the run recorded a set of durable API quirks (queue keys reject digits;
`queues create` de-facto requires an `--issue-type-config` with a real `*PresetWorkflow` id;
deleted queues 403-but-stay-listed; Forms enum answers must be lists; `questions move` without
`--page` is a silent no-op; …) — these now live in the plugin skills
(`plugins/yandex-360/skills/*/SKILL.md`) as agent-facing guardrails.
