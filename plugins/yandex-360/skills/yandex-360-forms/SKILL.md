---
name: yandex-360-forms
category: workflow
description: Use when reading or driving Yandex Forms through ycli — form schemas, responses, question CRUD, publishing, keysets — via the `ycli forms` CLI, the `forms_*` MCP tools, or the FormsClient SDK.
---

# Yandex 360 Forms

Drive Yandex Forms via `ycli` — reads **and writes** — through the CLI, the `forms_*` MCP tools, or the `FormsClient` SDK. Raw HTTP remains only for integration hooks (§4).

## When to use

- Listing forms you can access, or inspecting one form's schema (questions, options, conditional logic)
- Reading or exporting form responses (answers)
- Creating a form, doing question CRUD, reordering questions, publishing/unpublishing
- Submitting a form programmatically (filling), managing keysets
- Pre-flight before editing a form in the UI — confirm what's there and what to change

## When NOT to use

- Reading or editing Tracker issues — use `yandex-360-tracker`
- Reading or editing Wiki pages — use `yandex-360-wiki`
- Form appearance / themes, analytics / charts — UI-only
- Integration **hooks** are the one write surface ycli does not wrap — see §4 for the raw-HTTP route

## Scope: reads vs. writes

You can **read** any form your token can access. You can **write** to any form you have permission on. Both ship on all three ycli surfaces:

- **CLI** — `uv run ycli forms <group> <cmd>` (full surface, including binary uploads/downloads)
- **MCP** — 28 `forms_*` tools (13 reads + 15 writes). Write tools carry honest annotations (`readOnlyHint=False`, explicit `destructiveHint`); `ycli mcp start --read-only` hides them. Binary payloads (files/images upload, keysets/exports download) are CLI/SDK-only.
- **SDK** — `from ycli.yandex.forms.client import FormsClient` → `FormsClient(oauth_token=…, organization_id=…)`

The one remaining raw-HTTP case: **hooks** (§4).

---

## 1. Auth and hosts

Public API (`api.forms.yandex.net`):

```text
Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN
X-Org-Id: $YANDEX_ID_ORGANIZATION_ID
```

The OAuth token needs `forms:read` / `forms:write` scopes (see the auth section of the live API reference at <https://yandex.ru/dev/forms/>). The same token may work for Tracker/Wiki if those scopes were also granted, but Forms scopes are separate — a Tracker-only token will 401/403 here. The CLI/MCP/SDK set both headers for you from the environment.

**Host trap:** the base host is `api.forms.yandex.net` — NOT `api.tracker.yandex.net`. Only relevant when you drop to raw HTTP (hooks); ycli encodes it.

---

## 2. Reading

| Operation | CLI | MCP tool |
|-----------|-----|----------|
| Auth probe (current user) | `uv run ycli forms me get` | `forms_me_get` |
| List forms | `uv run ycli forms surveys list` | `forms_surveys_list` |
| Get form settings | `uv run ycli forms surveys get <form_id>` | `forms_surveys_get` |
| List questions (schema) | `uv run ycli forms questions list <form_id>` | `forms_questions_list` |
| Get one question | `uv run ycli forms questions get <form_id> <q_id>` | `forms_questions_get` |
| List answers (responses) | `uv run ycli forms answers list <form_id> [--all]` | `forms_answers_list` |
| Fillable form view (option ids!) | `uv run ycli forms filling get <form_id>` | `forms_filling_get` |
| Suggest values for a question | `uv run ycli forms filling suggest <form_id> --question <slug> --text …` | `forms_filling_suggest` |
| Keysets | `uv run ycli forms keysets list\|get …` | `forms_keysets_list` / `forms_keysets_get` |
| Verify uploaded file paths | `uv run ycli forms files verify <form_id> --path …` | `forms_files_verify` |
| Poll async operation | `uv run ycli forms operations get <op_id>` | `forms_operations_get` |

**Single-answer read:** `uv run ycli forms answers get --answer-id <id>` (or `--answer-key <hash>`, which works without form-edit access) — pass exactly one of the two. MCP: `forms_answers_get`. The live route is the flat query-param `GET /v1/answers?answer_id=…`; no survey id needed (the path variants 404).

### SDK example

```python
from ycli.yandex.forms.client import FormsClient

forms = FormsClient(oauth_token="…", organization_id="…")
forms.me.get()                       # auth probe
forms.surveys.list()                 # list forms
forms.surveys.get("<form_id>")       # form settings
forms.questions.list("<form_id>")    # schema
forms.answers.list("<form_id>")      # responses
```

---

## 3. Writing

All writes below are live-verified (2026-07-12) end-to-end via the CLI; each is also an MCP write tool and an SDK method.

### 3.1. Form (survey) lifecycle

```bash
uv run ycli forms surveys create --name "My form"          # → capture the returned id
uv run ycli forms surveys modify <form_id> --name "New name"
uv run ycli forms surveys publish <form_id>                # is_published: true
uv run ycli forms surveys unpublish <form_id>
uv run ycli forms surveys delete <form_id>                 # destructive
```

MCP: `forms_surveys_create` / `forms_surveys_modify` / `forms_surveys_publish` / `forms_surveys_unpublish` / `forms_surveys_delete`.

### 3.2. Question CRUD

```bash
uv run ycli forms questions create <form_id> --type string --label "Your feedback"
uv run ycli forms questions create <form_id> --body-file question.json   # full-body form (enum options, suggest, …)
uv run ycli forms questions modify <form_id> <q_id> --type string --label "Your feedback (edited)"
uv run ycli forms questions move <form_id> <q_id> --page 1 --position 1
uv run ycli forms questions delete <form_id> <q_id>
```

MCP: `forms_questions_create` / `forms_questions_modify` / `forms_questions_move` / `forms_questions_delete`.

### 3.3. Submit a response (filling)

```bash
uv run ycli forms filling get <form_id>                                  # exposes the enum option ids
uv run ycli forms filling submit <form_id> --body-file answer-body.json  # supports a dry-run flag
```

MCP: `forms_filling_submit`. The form must be published (`is_published: true`) or the submit is rejected.

### 3.4. Keysets

```bash
uv run ycli forms keysets create <form_id> --name my-keyset --total 3 --enabled
uv run ycli forms keysets modify <form_id> <keyset_id> --name renamed --total 5 --disabled
uv run ycli forms keysets download <form_id> <keyset_id> --output keys.xlsx   # binary — CLI/SDK only
uv run ycli forms keysets delete <form_id> <keyset_id>
```

MCP: `forms_keysets_create` / `forms_keysets_modify` / `forms_keysets_delete` (download is CLI/SDK-only).

### 3.5. Exports and binary operations

```bash
uv run ycli forms answers export <form_id> --format csv --wait --output export.csv
uv run ycli forms files upload <form_id> report.pdf        # form-filling file upload
uv run ycli forms images upload <form_id> logo.png
uv run ycli forms files download --path <storage_path> --output file.bin
uv run ycli forms files delete --path <storage_path>
```

MCP note: `forms_answers_export` triggers the export and `forms_operations_get` polls it, but the **download** of the produced file — like every raw-bytes operation here (`files upload/download`, `images upload`, `keysets download`) — is CLI/SDK-only; MCP excludes raw binary payloads. `forms_files_delete` (destructive) and `forms_files_verify` are on MCP.

---

## 4. Integration hooks — the one raw-HTTP surface

Hooks (create Tracker issue / Wiki page / send email / HTTP webhook on submit) are **documented in the current public api-ref** on `api.forms.yandex.net/v1` — hook groups (`/v1/surveys/{id}/hooks`), subscriptions (actions), conditions, template variables, notification history — but **ycli does not wrap them yet**. Two options:

1. **UI**: open the form → «Интеграции» tab → add/edit/delete an action group, configure variables and conditions.
2. **Raw HTTP with OAuth** against `api.forms.yandex.net/v1/surveys/{id}/hooks…` per the live reference at <https://yandex.ru/dev/forms/> (endpoints documented; not live-verified by this project — verify responses as you go).

After a hook change, submit a test response and verify the resulting Tracker issue / Wiki page / email has the expected fields.

---

## 5. Guardrails (live-verified quirks, 2026-07-12)

- **Enum answers in `filling submit` must be lists.** `{"answer_choices_<id>": ["<option_id>"]}` — a bare string 400s with `error_code: type`. Option ids come from `filling get`.
- **`questions move` needs `--page` with `--position`.** `--position` alone returns 200 but is a **silent no-op** — order unchanged.
- **`files upload` requires external storage.** Form-filling uploads 400 (`value_error.storage_error`) unless the org has connected its own S3 storage in the Forms UI settings — not API-toggleable.
- **`keysets modify` sends the full record.** The PATCH requires every field, not a partial diff — the CLI enforces this.
- **Publish state matters.** Unpublished forms reject submits; check `is_published` via `surveys get`.
- **Question IDs are server-assigned.** Read them back from the create/list response; never hardcode.
- **Suggest questions:** valid `data_source` names are `city` / `country`; suggest text matching is language-sensitive (Cyrillic input matches Russian city names).
- **OAuth scopes are separate.** A 401/403 usually means the token lacks `forms:read` / `forms:write`.
- **Org header is `X-Org-Id`** — the same canonical header every Yandex 360 service uses; HTTP header names are case-insensitive (RFC 9110), so a 422 is never a casing problem.
- **Datasource questions are scoped.** Tracker/Wiki/directory suggests are queue-/space-scoped — set the form's `dir_id` / target queue first.

---

## 6. References guide

| Resource | When to use |
|----------|-------------|
| `references/forms-api-quick-ref.md` | Bundled cheatsheet — host/auth, endpoint map, question types |
| <https://yandex.ru/dev/forms/> | Developer portal — full public API reference (auth, surveys, questions, answers, hooks, operations) |
| <https://yandex.ru/support/forms/> | Product docs — concepts, question types, integrations, publishing, conditions |
