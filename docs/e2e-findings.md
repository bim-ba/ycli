# Live E2E validation — findings & defect log

A record of the first **end-to-end run of `ycli` against a real Yandex 360 organization**
(not the stubbed test suite): every domain exercised through the CLI, the Python SDK, and the
read-only MCP tools, with full create→read→update→delete round-trips and cleanup.

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
| 6 | 🟠 | Forms | `answers.get` (single answer) 404s at every version/path — the endpoint is **not deployed** on `api.forms.yandex.net` | `forms/answers/` | ⚠️ **Needs decision** (see below) |
| 7 | 🟠 | Forms | `answers.export_results` forces `@returns.json()` on a `302`→CSV redirect → `JSONDecodeError`; broke `answers export --wait` | `forms/answers/client.py` | ✅ Fixed — treat followed redirect as terminal |
| 8 | 🟠 | Forms | `answers.list_all` / MCP drain followed a dead `/v3/…` `next_url` (HTML 404) | `forms/answers/client.py` | ✅ Fixed — rebuild the cursor on the working v1 path |
| 9 | 🟡 | Forms | `keysets.modify` (PATCH) requires the full record; help/`exclude_none` implied partial | `forms/keysets/{cli,client,models}.py` | ✅ Fixed — full body required; help corrected |

**8 of 9 fixed** in this branch (strict TDD, red→green confirmed, live-shape-verified, stubbed
tests, 100% coverage held). Bug 6 has no server endpoint to call.

## Needs-decision (not guessed)

- **Bug 6 — `answers.get` single-answer endpoint.** Every candidate path (v1/v2/v3, `{id}` and
  `{answer_key}`, trailing slash, `/answer/`, `?id=`, `?pk=`) returns a **server-level HTML/plain
  404**, never the API's JSON 404 — the route is not deployed. Options: (a) keep the operation and
  document it as a known upstream gap; (b) remove it (changes the ARCH-6 CLI/MCP snapshot and the
  coverage tables). Also: `forms/answers/mcp.py` carries an inaccurate comment claiming a 404
  yields an all-`None` `AnswerDetail` — the real HTML 404 makes `.json()` raise. Left pending this
  decision.
- **Wiki comment threading.** In `GET /pages/{id}/comments` a `parent_id` reply is returned
  **flat as a sibling** (not nested); `thread_id` is `null` on both root and reply; the
  `/comments/{id}/thread` endpoint returns `{"results": []}` for real parent/child pairs. Correct
  thread rendering needs a design choice (client-side grouping by `parent_id`, and/or reconsidering
  what id `comments thread` is called with) — beyond a `models.py` mapping. The content/author
  mapping (Bug 4) is fixed; the tree shape is deferred.
- **Keyset `create` latent gap.** The API also requires `is_enabled` on `keysets.create`, but the
  CLI's `--enabled` is optional there (same class as Bug 9, left out of that fix's scope).

## Doc / skill drift

- The `yandex-360-tracker` skill lists `issues full` / MCP `tracker_issues_full`; neither exists
  (`issues get` is already the full view). Remove from the skill.
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
