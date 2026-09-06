# Yandex Forms API Quick Reference

An original, condensed map of the Forms public API surface used by this skill. For the
full, current reference see the live developer portal at <https://yandex.ru/dev/forms/>
and the product docs at <https://yandex.ru/support/forms/>.

## Host and auth

| | |
|---|---|
| Base | `https://api.forms.yandex.net/v1/` |
| Auth header | `Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN` |
| Org header | `X-Org-Id: $YANDEX_ID_ORGANIZATION_ID` (same canonical header as Tracker/Wiki; case-insensitive) |
| Scopes | `forms:read` / `forms:write` (separate from Tracker/Wiki) |

The base host differs from Tracker/Wiki (`api.tracker.yandex.net`) — a frequent
copy-paste trap. Reads **and writes** are exposed as `ycli forms …` CLI commands,
`forms_*` MCP tools, and `FormsClient` SDK methods; see the skill's Reading/Writing
sections for the mapping. Raw HTTP is needed only for hooks (see below).

## Endpoint map (as wrapped by ycli)

| Resource | Method + path |
|----------|---------------|
| Current user (auth probe) | `GET /users/me` |
| List forms | `GET /surveys` |
| Form settings | `GET /surveys/{id}` |
| Create form | `POST /surveys` |
| Update form settings | `PATCH /surveys/{id}` |
| Delete form | `DELETE /surveys/{id}` |
| Publish / unpublish | `POST /surveys/{id}/publish` · `POST /surveys/{id}/unpublish` |
| List questions (schema) | `GET /surveys/{id}/questions` |
| Get one question | `GET /surveys/{id}/questions/{qid}` |
| Create question | `POST /surveys/{id}/questions` |
| Update question | `PATCH /surveys/{id}/questions/{qid}` |
| Delete question | `DELETE /surveys/{id}/questions/{qid}` |
| Reorder question | `POST /surveys/{id}/questions/{qid}/move` |
| Question show conditions | `GET\|POST\|PATCH /surveys/{id}/questions/{qid}/conditions`, `GET\|PATCH\|DELETE …/conditions/{cid}` |
| Page show conditions | `GET\|POST\|PATCH /surveys/{id}/pages/{page_id}/conditions`, `GET\|PATCH\|DELETE …/conditions/{cid}` |
| Submit-button show conditions | `GET\|POST\|PATCH /surveys/{id}/conditions`, `GET\|PATCH\|DELETE …/conditions/{cid}` |
| Fillable form / submit | `GET\|POST /surveys/{id}/form` |
| Filling suggest | `GET /surveys/{id}/suggest` |
| List answers (responses) | `GET /surveys/{id}/answers` |
| Single answer | `GET /answers?answer_id=…` or `?answer_key=…` (flat route, no survey id) |
| Export answers (async) | `POST /surveys/{id}/answers/export` → `GET …/answers/export-results` |
| Keysets CRUD + download | `GET\|POST /surveys/{id}/keysets`, `GET\|PATCH\|DELETE …/keysets/{kid}`, `GET …/keysets/{kid}/download` |
| Files upload / verify / download / delete | `POST /surveys/{id}/files`, `POST …/files/verify`, `GET\|DELETE /files` |
| Images upload | `POST /surveys/{id}/images` |
| Poll async operation | `GET /operations/{op_id}` |

Question IDs are server-assigned — read them back from the create/list response
rather than hardcoding.

## Question types

| Group | Types |
|-------|-------|
| Text / scalar | `short-text`, `long-text`, `number`, `integer`, `date`, `email`, `phone`, `link` |
| Choice | `radiobutton`, `dropdown`, `multiple`, `yes-no`, `rating` |
| Special input | `file`, `geography`, `tin` (ИНН) |
| Directory suggest | `people`, `departments`, `teams` |
| Resource suggest | `tracker`, `wiki` |
| Other | `payment`, `tests`, `series`, `empty` |

Datasource-backed dropdowns (`datasource: tracker_component`, `tracker_user`,
`dir_user`, `wiki_table_source`, …) are queue-/space-scoped: set the form's `dir_id` /
target queue before adding them, or the suggest returns nothing.

## Documented but not wrapped by ycli

- **Integration hooks** (create Tracker issue / Wiki page / email / webhook on submit)
  — hook groups, subscriptions, conditions, template variables, and notification history
  are documented on `api.forms.yandex.net/v1` but not implemented in ycli (tracked
  coverage gap). Use the UI or raw OAuth HTTP — see the skill's §4.
- **Answer integrations view** — `GET /v1/answers/integrations` (which integrations
  fired for an answer). The single-answer view itself IS wrapped:
  `ycli forms answers get --answer-id …|--answer-key …` (`GET /v1/answers`, flat
  query-param route — the path variants 404).

## Not in the public API

- **Appearance / themes, analytics / charts** — UI only.

See the skill's §4/§5 for the hooks workflow and the durable guardrails
(publish state, scope errors, enum-answer list shape).
