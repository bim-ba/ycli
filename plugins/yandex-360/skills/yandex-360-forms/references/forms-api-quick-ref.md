# Yandex Forms API Quick Reference

An original, condensed map of the Forms public API surface used by this skill. For the
full, current reference see the live developer portal at <https://yandex.ru/dev/forms/>
and the product docs at <https://yandex.ru/support/forms/>.

## Host and auth

| | |
|---|---|
| Base | `https://api.forms.yandex.net/v1/` |
| Auth header | `Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN` |
| Org header | `X-Org-Id: $YANDEX_ID_ORGANIZATION_ID` (lowercase `id` — unlike Tracker) |
| Scopes | `forms:read` / `forms:write` (separate from Tracker/Wiki) |

The base host differs from Tracker/Wiki (`api.tracker.yandex.net`) — a frequent
copy-paste trap. Reads are also exposed as `ycli forms …` CLI commands and read-only
`forms_*` MCP tools; see the skill's Reading section for the CLI/MCP mapping.

## Endpoint map

| Resource | Method + path |
|----------|---------------|
| Current user (auth probe) | `GET /me` |
| List forms | `GET /surveys` |
| Form settings | `GET /surveys/{id}` |
| Create form | `POST /surveys` |
| Update form settings | `PUT /surveys/{id}` |
| Publish / unpublish | `POST /surveys/{id}/_publish` · `POST /surveys/{id}/_unpublish` |
| List questions (schema) | `GET /surveys/{id}/questions` |
| Get one question | `GET /surveys/{id}/questions/{qid}` |
| Create question | `POST /surveys/{id}/questions` |
| Update question | `PUT /surveys/{id}/questions/{qid}` |
| Delete question | `DELETE /surveys/{id}/questions/{qid}` |
| Reorder question | `POST /surveys/{id}/questions/{qid}/_move` |
| List answers (responses) | `GET /surveys/{id}/answers` |
| Export answers (async) | `POST /surveys/{id}/answers/_export` |
| Poll async operation | `GET /operations/{op_id}` |

Paths are grouped by resource; `_`-prefixed segments (`_publish`, `_move`, `_export`)
are action endpoints. Question IDs are server-assigned — read them back from the
create/list response rather than hardcoding.

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

## Not in the public API

- **Integration hooks** (create Tracker issue / Wiki page / email / webhook on submit)
  — UI or the session-cookie gateway only.
- **Appearance / themes, analytics / charts** — UI only.

See the skill's §4/§5 for the UI-and-gateway workflow and the durable guardrails
(publish state, header casing, scope errors).
