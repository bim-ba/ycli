---
name: forms-api-docs-index
description: Navigation guide to Yandex Forms documentation — 9 sections, 110 files, endpoints and concepts mapped by purpose
type: index
---

# Yandex Forms — Documentation Index

Full docs: `docs/40-references/yandex/forms/` (the section directories beside this index) (9 top-level sections, 110 markdown files).

**Public API base:** `https://api.forms.yandex.net/v1/`
**Auth:** `Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN` + `X-Org-Id: $YANDEX_ID_ORGANIZATION_ID`
**OAuth scopes:** `forms:read` (read-only) / `forms:write` (create + modify + delete)

> Note: different from Tracker — `api.forms.yandex.net` (not `api.tracker.yandex.net`), and header is `X-Org-Id` (lowercase `id`) per official docs.

---

## Quick reference — API endpoints by resource

| Resource | Key endpoints |
|----------|---------------|
| **Forms (surveys)** | `POST /v1/surveys` · `GET /v1/surveys` · `GET /v1/surveys/{id}` · `PATCH /v1/surveys/{id}` · `DELETE /v1/surveys/{id}` · `POST /v1/surveys/{id}/_publish` · `POST /v1/surveys/{id}/_unpublish` |
| **Questions** | `POST /v1/surveys/{id}/questions` · `GET /v1/surveys/{id}/questions` · `GET /v1/surveys/{id}/questions/{q_id}` · `PUT /v1/surveys/{id}/questions/{q_id}` · `DELETE /v1/surveys/{id}/questions/{q_id}` · `POST /v1/surveys/{id}/questions/{q_id}/_move` |
| **Answers (responses)** | `GET /v1/surveys/{id}/answers` · `GET /v1/surveys/{id}/answers/{a_id}` · `POST /v1/surveys/{id}/answers/_export` · `GET /v1/surveys/{id}/answers/_export/{op_id}` |
| **Form filling** | `GET /v1/surveys/{id}/_filling/settings` · `GET /v1/surveys/{id}/_filling/suggestions` · `POST /v1/surveys/{id}/_filling/submit` |
| **Form-filling keys** (one-time tokens for embeds) | `POST /v1/surveys/{id}/filling-keys` · `GET /v1/surveys/{id}/filling-keys` · `GET /v1/surveys/{id}/filling-keys/{k_id}` · `PUT /v1/surveys/{id}/filling-keys/{k_id}` · `DELETE /v1/surveys/{id}/filling-keys/{k_id}` · `GET /v1/surveys/{id}/filling-keys/_download` |
| **Files** (uploaded attachments) | `POST /v1/files/_upload` · `GET /v1/files/{f_id}/_download` · `GET /v1/files/{f_id}/_get-upload` · `DELETE /v1/files/{f_id}` |
| **Images** | `POST /v1/images/_upload` |
| **Operations** (async tasks like export) | `GET /v1/operations/{op_id}` |
| **Users** | `GET /v1/users/me` · `GET /v1/users/{u_id}` |

> The Public API does NOT cover **integration hooks** (Tracker / Wiki / Email / HTTP webhook). Hooks are configured in the Yandex Forms UI and accessible only via the gateway endpoint with session cookies. See SKILL.md §4.3.

---

## Directory map

| Dir | Resource | Key features | When to read |
|-----|----------|--------------|--------------|
| `01-overview/` | Concepts, terminology | What Forms is, business vs personal modes, how it integrates with 360 | When unfamiliar with Forms — single intro file |
| `02-go-to-forms/` | Login, activation, onboarding | How to enter Forms, how to activate it for an org | When setting up Forms for the first time for an org user |
| `03-quickstart/` | First-time walkthrough | 5-min «create a form» guide | If user has never made a form |
| `04-new/` | Creating new forms | Appearance / questions / success page / tests / validation | When starting a new form from scratch |
| `05-integration/` | Hook integrations | Tracker / Wiki / Email / HTTP request / Cloud Functions / Variables / Yandex Metrica | **MOST relevant** for connecting forms to downstream systems. **Variables** doc (`variables.md`) is key for hook body templates |
| `06-publish/` | Publishing & access | Publish + conditions + pre-fill via query / hidden fields / question-id / refilling / restrictions | When making a form public + when implementing conditional question logic |
| `07-editing/` | Editing forms | Access (who can edit), settings, personal settings | When managing form ownership and editor permissions |
| `08-questions/` | All 26 question types | One file per type — short-text, long-text, number, integer, date, email, phone, link, radiobutton, dropdown, multiple, yes-no, rating, file, geography, tin, people, departments, teams, tracker, wiki, payment, tests, series, empty | **Read individual file before adding a question of that type** to understand options and datasources |
| `09-api/` | Public API reference | Auth + examples + per-resource endpoint reference | **Read first** for any programmatic operation |

---

## Per-section deep-dives

### `05-integration/` — integration hooks

| File | What it covers |
|------|----------------|
| `index.md` | Section overview |
| `create-issue-yandex-tracker.md` | **Tracker integration** — how to map form fields to Tracker issue fields. Critical: typed dropdown fields like `type` / `priority` do NOT accept variable substitution — use conditional action groups |
| `respone-to-wiki.md` | **Wiki integration** — create Wiki page from form response |
| `send-email.md` | Email action |
| `send-request.md` | Generic HTTP webhook — sends JSON body to URL |
| `external-storage.md` | External database storage |
| `cloud-functions/` | Yandex Cloud Functions integration (3 files: index, quickstart, datalens, send-to-database) |
| `yandex-metrica.md` | Yandex Metrica tracking |
| `history.md` | Integration execution history (UI feature) |
| `variables.md` | **Variables reference** — `form.question_answer`, `form.question_answer_choice_slug`, user info, browser info, request info. Critical for body templates |

### `06-publish/` — publishing and conditions

| File | What it covers |
|------|----------------|
| `index.md` | Section overview |
| `answers.md` | Setting up where responses go |
| `conditions.md` | **Conditional logic** — show / hide questions based on previous answers. Used heavily for «show this Q only if previous Q = X» |
| `quickstart.md` | Quick publish workflow |
| `restrictions.md` | Access restrictions, anonymous responses, etc. |
| `pre-fill/index.md` | How to pre-fill form fields |
| `pre-fill/hidden-query.md` | Pre-fill via URL query params (hidden fields) |
| `pre-fill/question-id.md` | Pre-fill via question ID query params |
| `pre-fill/request-parameters.md` | Detailed query param syntax |
| `pre-fill/refilling.md` | Refilling forms (e.g., for editing prior responses) |

### `08-questions/` — question type catalog (26 types)

Common types:

- **Text:** `short-text.md`, `long-text.md`, `email.md`, `phone.md`, `link.md`
- **Numeric:** `number.md`, `integer.md`
- **Date / time:** `date.md`
- **Choice:** `radiobutton.md`, `dropdown.md`, `multiple.md` (checkboxes), `yes-no.md`, `rating.md`
- **File:** `file.md` (with `maxSize` / `maxCount` limits)
- **Geography:** `geography.md`, `tin.md` (ИНН) — Russia-specific
- **Directory-backed:** `people.md`, `departments.md`, `teams.md` (suggest from org directory)
- **Tracker / Wiki:** `tracker.md`, `wiki.md` (suggest from Tracker components / users / Wiki spaces)
- **Special:** `payment.md`, `tests.md`, `series.md`, `empty.md` (section divider)

Each file documents the question's data structure, options, validation rules, and UI behaviour.

### `09-api/` — public API reference

Top-level files:

- `index.md` — section overview
- `access.md` — **Authentication** (OAuth 2.0 + IAM token + headers)
- `examples.md` — example requests

Under `reference/`:

| Sub-dir | Endpoints |
|---------|-----------|
| `01-answers/` | get, get-many, export, get-export-result, index |
| `02-files/` | upload, download, delete, get-upload, index |
| `03-forms/` | list, create, modify, get-settings, publish, unpublish, delete, index |
| `04-form-filling/` | get-settings, get-suggestions, submit-response, index |
| `05-images/` | upload, index |
| `06-questions/` | list, get, create, modify, delete, move, index |
| `07-form-filling-keys/` | list, get, create, modify, delete, download, index |
| `08-operations/` | get-result, index |
| `09-users/` | get, index |

---

## Common workflows

### Read a form's current schema

```bash
set -a; source .env; set +a

http GET "https://api.forms.yandex.net/v1/surveys/$FORM_ID" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID"

http GET "https://api.forms.yandex.net/v1/surveys/$FORM_ID/questions" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID"
```

### List forms in the organization

```bash
http GET 'https://api.forms.yandex.net/v1/surveys?page=1&per_page=100' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID"
```

### Export all answers to a file (async)

```bash
# 1. Start export
http POST "https://api.forms.yandex.net/v1/surveys/$FORM_ID/answers/_export" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" \
  format=csv
# Returns operation_id

# 2. Poll operation status
http GET "https://api.forms.yandex.net/v1/operations/$OP_ID" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID"

# 3. Download when ready (status=done)
http GET "https://api.forms.yandex.net/v1/surveys/$FORM_ID/answers/_export/$OP_ID" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" \
  > answers.csv
```

### Create a new question on a form

See `09-api/reference/06-questions/create.md` for full JSON body schema by question type.

```bash
http POST "https://api.forms.yandex.net/v1/surveys/$FORM_ID/questions" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" \
  < /tmp/question-body.json
```

---

## Known limitations

- **No hook CRUD via public API.** Integration hooks (Tracker / Wiki / Email / HTTP) must be configured through the UI. Programmatic access only via gateway with session cookies.
- **No appearance / theme API.** Form appearance (colors, fonts, logos) is UI-only.
- **No analytics API.** Yandex Metrica integration is UI-only.
- **Variable substitution for typed dropdown fields.** In Tracker integration hooks, `type` and `priority` are typed dropdowns that don't accept variable substitution from form answers. Use conditional action groups OR default-value-and-manual-triage.
- **OAuth scope limitations.** `forms:read` does NOT include reading hook configs (those are UI-only anyway). `forms:write` covers form CRUD but NOT hook management.
- **Rate limits not documented.** Use bulk-friendly endpoints (`_export` instead of per-answer GET) for large operations.
