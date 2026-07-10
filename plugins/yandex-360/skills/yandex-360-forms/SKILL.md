---
name: yandex-360-forms
category: workflow
description: Use when reading or driving Yandex Forms (Yandex 360) — listing forms, inspecting a form's questions/schema, reading or exporting responses, or creating/editing forms and questions and publishing them. Reads go through `ycli forms` CLI / MCP tools or the FormsClient SDK; writes (create form, question CRUD, publish/unpublish, export) go via raw HTTP to api.forms.yandex.net. Use before any form lookup or edit. NOTE the API host differs from Tracker/Wiki (api.forms.yandex.net, not api.tracker.yandex.net) and the org header is X-Org-Id.
---

# Yandex 360 Forms

Drive Yandex Forms via `ycli` (CLI / MCP / SDK) for reads, and raw HTTP for writes.

## When to use

- Listing forms you can access, or inspecting one form's schema (questions, options, conditional logic)
- Reading or exporting form responses (answers)
- Creating a form, doing question CRUD, reordering questions, publishing/unpublishing
- Pre-flight before editing a form in the UI — confirm what's there and what to change

## When NOT to use

- Reading or editing Tracker issues — use `yandex-360-tracker`
- Reading or editing Wiki pages — use `yandex-360-wiki`
- Form appearance / themes, analytics / charts, and integration **hooks** — these are UI-only (see §6); this skill covers programmatic schema/response operations

## Scope: reads vs. writes

You can **read** any form your token can access. You can **write** to any form you have permission on.

- **Reads** — `ycli forms` CLI commands, read-only MCP tools, or the `FormsClient` SDK (§3).
- **Writes** (create form, question CRUD, publish/unpublish, export answers) — **no CLI/MCP/SDK coverage**; use raw HTTP (httpie/curl) against the public API, or edit in the Yandex Forms UI (§5).

If you want to keep your own design notes / specs for forms you maintain, do so however suits your project — this skill does not prescribe a layout.

---

## 1. Auth and hosts

### Authentication

Public API (`api.forms.yandex.net`):

```text
Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN
X-Org-Id: $YANDEX_ID_ORGANIZATION_ID
```

The OAuth token needs `forms:read` / `forms:write` scopes (see the auth section of the live API reference at <https://yandex.ru/dev/forms/>). The same token may work for Tracker/Wiki if those scopes were also granted, but Forms scopes are separate — a Tracker-only token will 401/403 here.

### Hosts

| Host | Use | Auth |
|------|-----|------|
| `api.forms.yandex.net/v1/` | Public API — forms / questions / answers CRUD | OAuth |
| `forms.yandex.ru/cloud/admin/gateway/root/form/*` | UI gateway — hooks, macros, internal config not in the public API | Browser session cookies |
| `forms.yandex.ru/cloud/admin/<form_id>/edit` | UI URL for human editing | Browser session |

The gateway host uses the web UI's session cookies (CSRF + `Cookie`), not OAuth. It is **not headless-friendly** — usable only when a user exports a curl-with-cookies from browser devtools. Avoid it unless there is no alternative.

### Tools

**Reads** are available three ways:

- CLI: `uv run ycli forms <group> <cmd>`
- MCP (read-only): **10** tools named `forms_<resource>_<action>` — the ones you reach for most are `forms_me_get`, `forms_surveys_list`, `forms_surveys_get`, `forms_questions_list`, `forms_answers_list`
- SDK: `from ycli.yandex.forms.client import FormsClient` → `FormsClient(oauth_token=…, organization_id=…).me/.surveys/.questions/.answers`

**Writes** use raw `http` (httpie). Load auth from env first:

```bash
set -a; source .env; set +a

http GET 'https://api.forms.yandex.net/v1/surveys' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID"
```

---

## 2. Reading workflow

**Trigger:** you need context about a form — its schema, options, responses — or to verify a form's live state.

### 2.1. Read endpoints

| Operation | Endpoint | CLI / MCP tool |
|-----------|----------|----------------|
| Auth probe (current user) | — | `uv run ycli forms me get` (MCP `forms_me_get`) |
| List forms | `GET /v1/surveys` | `uv run ycli forms surveys list` (MCP `forms_surveys_list`) |
| Get form settings | `GET /v1/surveys/{id}` | `uv run ycli forms surveys get <form_id>` (MCP `forms_surveys_get`) |
| List questions | `GET /v1/surveys/{id}/questions` | `uv run ycli forms questions list <form_id>` (MCP `forms_questions_list`) |
| Get one question | `GET /v1/surveys/{id}/questions/{q_id}` | `uv run ycli forms questions get <form_id> <q_id>` |
| List answers (responses) | `GET /v1/surveys/{id}/answers` | `uv run ycli forms answers list <form_id>` (MCP `forms_answers_list`) |
| Export answers | `POST /v1/surveys/{id}/answers/_export` | `uv run ycli forms answers export <form_id>` |
| Get operation result (async) | `GET /v1/operations/{op_id}` | `uv run ycli forms operations get <op_id>` (MCP `forms_operations_get`) |

Endpoint paths and payloads are summarised in the bundled `references/forms-api-quick-ref.md`; the full live reference is at <https://yandex.ru/dev/forms/>.

### 2.2. SDK example

```python
from ycli.yandex.forms.client import FormsClient

forms = FormsClient(oauth_token="…", organization_id="…")
forms.me.get()                       # auth probe
forms.surveys.list()                 # list forms
forms.surveys.get("<form_id>")       # form settings
forms.questions.list("<form_id>")    # schema
forms.answers.list("<form_id>")      # responses
```

### 2.3. Common read scenarios

| Scenario | Steps |
|----------|-------|
| «What does form X look like now?» | `uv run ycli forms questions list <form_id>` (live schema) |
| «Show me last 20 responses» | `uv run ycli forms answers list <form_id>` (or raw `GET /v1/surveys/{id}/answers?per_page=20`) |
| «Export all responses to file» | `POST /v1/surveys/{id}/answers/_export` → poll `GET /v1/operations/{op_id}` → download |

---

## 3. Writing workflow

**Trigger:** you create or update a form you have permission on. There is no CLI/MCP/SDK for writes — use raw HTTP, or edit in the UI.

### 3.1. Create a form

```bash
http POST 'https://api.forms.yandex.net/v1/surveys' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" \
  name="My form" language=ru
# Capture form_id from the response.
```

See the create-form endpoint in the live API reference at <https://yandex.ru/dev/forms/>.

### 3.2. Question CRUD

```bash
# Create a question
http POST "https://api.forms.yandex.net/v1/surveys/<form_id>/questions" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" \
  < question-body.json

# Modify
http PUT "https://api.forms.yandex.net/v1/surveys/<form_id>/questions/<q_id>" ...

# Delete
http DELETE "https://api.forms.yandex.net/v1/surveys/<form_id>/questions/<q_id>" ...

# Reorder
http POST "https://api.forms.yandex.net/v1/surveys/<form_id>/questions/<q_id>/_move" \
  position=3 ...
```

Question types — summarised in the bundled `references/forms-api-quick-ref.md`; full per-type docs at <https://yandex.ru/support/forms/>:

- `short-text` / `long-text` / `number` / `integer` / `date` / `email` / `phone` / `link`
- `radiobutton` / `dropdown` / `multiple` / `yes-no` / `rating`
- `file` / `geography` / `tin` (ИНН)
- `people` / `departments` / `teams` (suggest from directory)
- `tracker` / `wiki` (suggest from Tracker / Wiki resources)
- `payment` / `tests` / `series` / `empty`

For datasource-backed dropdowns (e.g. `datasource: tracker_component`, `tracker_user`, `dir_user`, `wiki_table_source`), see the dropdown/tracker question types in `references/forms-api-quick-ref.md` and the live docs at <https://yandex.ru/support/forms/>. These suggests are queue-/space-scoped: ensure the form's `dir_id` / target queue is set before adding such questions.

### 3.3. Publish / unpublish

```bash
http POST "https://api.forms.yandex.net/v1/surveys/<form_id>/_publish" ...
http POST "https://api.forms.yandex.net/v1/surveys/<form_id>/_unpublish" ...
```

See the publish/unpublish endpoints in the live API reference at <https://yandex.ru/dev/forms/>. Unpublished forms reject submit-response calls — check the form settings (`is_published`) before testing submissions.

### 3.4. Conditional logic

Conditional show/hide is configured via the «Условия» feature in the UI, or via the question update endpoint's `conditions` field. See the conditions docs at <https://yandex.ru/support/forms/>.

---

## 4. Integration hooks — UI / gateway only

Integration hooks (create Tracker issue / Wiki page / send email / HTTP webhook on submit) are **not** in the public API. Two options:

1. **UI** (recommended): open the form → «Интеграции» tab → add/edit/delete an action group, configure variables and conditions. For the integration-variable reference see <https://yandex.ru/support/forms/>.
2. **Gateway** (`forms.yandex.ru/cloud/admin/gateway/root/form/getHooks` etc.): internal endpoints used by the web UI, authenticated with browser session cookies + CSRF token. Not headless-friendly; only usable with a curl-with-cookies exported from devtools.

After a hook change, submit a test response and verify the resulting Tracker issue / Wiki page / email has the expected fields.

---

## 5. Guardrails (Yandex Forms quirks)

- **Different host than Tracker/Wiki.** `api.forms.yandex.net` — NOT `api.tracker.yandex.net`. Easy to miss when copy-pasting an auth block from a Tracker request.
- **Header is `X-Org-Id` (lowercase `id`).** Tracker uses `X-Org-ID` (uppercase). httpie/curl pass headers verbatim, so case matters — verify with `--print=H` if a request fails with 422.
- **OAuth scopes are separate.** A 401/403 usually means the token lacks `forms:read` / `forms:write`. May require regenerating the token.
- **Question IDs are server-assigned.** Don't hardcode them before creation; read them back from the create/list response.
- **Hooks are not in the public API.** Do hook changes in the UI (§4).
- **Publish state matters.** Unpublished forms reject submit-response calls; check `is_published`.
- **Datasource questions are scoped.** Tracker/Wiki/directory suggests are queue-/space-scoped — set the form's `dir_id` / target queue first.

---

## 6. References guide

| Resource | When to use |
|----------|-------------|
| `references/forms-api-quick-ref.md` | Bundled cheatsheet — host/auth, endpoint map, question types |
| <https://yandex.ru/dev/forms/> | Developer portal — full public API reference (auth, surveys, questions, answers, operations) |
| <https://yandex.ru/support/forms/> | Product docs — concepts, question types, integrations, publishing, conditions |
