---
name: tracker-api-docs-index
description: Comprehensive navigation guide to Yandex Tracker API docs — endpoints, features, and when to read each directory
type: index
---

# Yandex Tracker API — Documentation Index

Full docs: `docs/40-references/yandex/tracker/` (the section directories beside this index) (18 directories, 397 files, ~500 API endpoints)

Base URL: `https://api.tracker.yandex.net/v3`
Auth: `Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN` + `X-Org-ID: $YANDEX_ID_ORGANIZATION_ID`

---

## Quick Reference: Endpoints by Resource

| Resource | Key Endpoints |
|----------|--------------|
| **Issues/Tasks** | `POST /v3/issues/` · `GET /v3/issues/{key}` · `PATCH /v3/issues/{key}` · `DELETE /v3/issues/{key}` · `POST /v3/issues/_search` · `POST /v3/issues/{key}/move` |
| **Transitions** | `GET /v3/issues/{key}/transitions` · `POST /v3/issues/{key}/transitions/{id}/_execute` |
| **Comments** | `POST /v3/issues/{key}/comments/` · `GET /v3/issues/{key}/comments/` · `PATCH /v3/issues/{key}/comments/{id}` · `DELETE /v3/issues/{key}/comments/{id}` |
| **Reactions** | `POST /v3/issues/{key}/comments/{id}/reactions` |
| **Attachments** | `POST /v3/issues/{key}/attachments/` · `GET /v3/issues/{key}/attachments/` · `DELETE /v3/issues/{key}/attachments/{id}` · `POST /v3/issues/{key}/attachments/upload` (temp) |
| **Links** | `POST /v3/issues/{key}/links` · `GET /v3/issues/{key}/links` · `DELETE /v3/issues/{key}/links/{id}` |
| **External Links** | `POST /v3/issues/{id}/externalLinks` · `GET /v3/issues/{id}/externalLinks` · `DELETE /v3/issues/{id}/externalLinks/{id}` |
| **Checklists** | `POST /v3/issues/{key}/checklistItems` · `GET /v3/issues/{key}/checklistItems` · `PATCH /v3/issues/{key}/checklistItems/{id}` · `DELETE /v3/issues/{key}/checklistItems/{id}` |
| **Worklog** | `POST /v3/issues/{key}/worklog` · `GET /v3/issues/{key}/worklog` · `PATCH /v3/issues/{key}/worklog/{id}` · `DELETE /v3/issues/{key}/worklog/{id}` · `POST /v3/worklog/_search` |
| **History** | `GET /v3/issues/{key}/history` |
| **Bulk Operations** | `POST /v3/bulkchange/_update` · `POST /v3/bulkchange/_move` · `GET /v3/bulkchange/_status/{id}` |
| **Boards** | `POST /v3/boards/` · `GET /v3/boards/` · `PATCH /v3/boards/{id}` · `DELETE /v3/boards/{id}` |
| **Sprints** | `POST /v3/boards/{id}/sprints` · `GET /v3/boards/{id}/sprints` · `POST /v3/boards/{id}/sprints/{id}/start` · `POST /v3/boards/{id}/sprints/{id}/archive` |
| **Board Columns** | `GET /v3/boards/{id}/columns` · `PATCH /v3/boards/{id}/columns/{id}` |
| **Queues** | `POST /v3/queues/` · `GET /v3/queues/` · `GET /v3/queues/{id}` · `PATCH /v3/queues/{id}` · `DELETE /v3/queues/{id}` |
| **Queue Sub-resources** | `/v3/queues/{id}/components/` · `/v3/queues/{id}/versions` · `/v3/queues/{id}/tags` · `/v3/queues/{id}/requiredFields` |
| **Triggers** | `POST /v3/queues/{id}/triggers/` · `GET /v3/queues/{id}/triggers/` · `PATCH /v3/queues/{id}/triggers/{id}` · `GET /v3/queues/{id}/triggers/{id}/logs` |
| **Macros** | `POST /v3/queues/{id}/macros/` · `GET /v3/queues/{id}/macros/` · `PATCH /v3/queues/{id}/macros/{id}` · `DELETE /v3/queues/{id}/macros/{id}` |
| **Autoactions** | `POST /v3/queues/{id}/autoactions/` · `GET /v3/queues/{id}/autoactions/` · `PATCH /v3/queues/{id}/autoactions/{id}` · `GET /v3/queues/{id}/autoactions/{id}/logs` |
| **Entities** | `POST /v3/entities/{type}/` · `GET /v3/entities/{type}/` · `PATCH /v3/entities/{id}` · `DELETE /v3/entities/{id}` · `POST /v3/entities/_bulk_edit` |
| **Entity Sub-resources** | `/v3/entities/{id}/comments` · `/v3/entities/{id}/files` · `/v3/entities/{id}/links` · `/v3/entities/{id}/checklists` |
| **Fields** | `GET /v3/fields/` · `GET /v3/fields/{id}/values` · `GET /v3/queues/{id}/localFields/` |
| **Users** | `GET /v3/users/` · `GET /v3/myself` |
| **Search / Filters** | `POST /v3/filters/` · `GET /v3/filters/` · `PATCH /v3/filters/{id}` |
| **Import** | `POST /v3/issues/_import` · `POST /v3/issues/{id}/comments/_import` · `POST /v3/issues/{id}/attachments/_import` · `POST /v3/issues/{id}/worklog/_import` · `POST /v3/issues/{id}/links/_import` |

---

## Directory Map

| Dir | Resource | Key features | When to read |
|-----|----------|-------------|--------------|
| `01-overview/` | Tracker concepts, terminology, entities | Data model: issues, queues, boards, sprints, projects; entity hierarchy; field types | When unfamiliar with Tracker data model or need conceptual grounding |
| `02-configuration/` | Queue setup, workflow configuration | Status and transition configuration; required fields per transition; workflow templates | When troubleshooting status/transition issues or setting up a new queue |
| `03-how-to-use/` | General usage patterns | End-to-end usage walkthroughs | Rarely needed — most patterns are in SKILL.md |
| `04-guides/` | Step-by-step guides | Complex multi-step operations (import, automation setup, board configuration) | When doing a complex operation for the first time |
| `05-queue/` | Queue CRUD and metadata | Components, versions, tags, access rules, required fields per transition | When reading or modifying queue metadata |
| `06-tasks/` | Issue CRUD, search, transitions, comments, links | Full issue lifecycle; search query syntax; transition execution; comment and link management | **Most common — read for any issue operation** |
| `07-agile/` | Boards and sprints | Board CRUD; sprint lifecycle (create/start/archive); column management; backlog | When working with board or sprint configuration |
| `08-entities/` | Projects, portfolios, goals (new Entity API) | POST /v3/entities/{type}/ where type=project\|portfolio\|goal; entity links; key results | When using the entities API for project/portfolio management |
| `09-tasks/` | Additional task operations | Supplementary task endpoints; bulk field updates; some operations duplicated from 06 | Check `06-tasks/` first; use this for operations not found there |
| `10-notifications/` | Notification settings | Notification subscription management | Rarely needed for agent workflows |
| `11-mobile/` | Mobile API specifics | Mobile-specific endpoints and response formats | Not relevant for agent workflows |
| `12-dashboards/` | Dashboard creation | Dashboard CRUD; widget configuration | When creating or modifying dashboards programmatically |
| `12-reports/` | Reports | Reporting endpoints; data export | When generating reports or exporting data |
| `13-automation/` | Autoactions, triggers, macros | Rule conditions and actions; variable substitution syntax; webhook actions; execution logs | When setting up automation rules or debugging trigger execution |
| `14-templates/` | Issue templates | Template CRUD; applying templates to issues | When working with Tracker issue templates |
| `15-sla/` | SLA rules | SLA configuration; timer logic | When checking or debugging SLA configuration |
| `16-integrations/` | External integrations | Third-party tool integration patterns; external link management | When connecting external tools (Jira, GitHub, etc.) |
| `17-devtools/` | Developer tools, webhooks | Webhook setup; event types; payload structure; retry logic | When setting up webhooks for event-driven integrations |
| `18-api/` | API reference — auth, errors, all endpoints | Auth details; error codes; full endpoint reference by resource; pagination; rate limits | **Read first if unfamiliar with Tracker API** — canonical endpoint reference |

---

## Feature Deep-Dives

For per-resource detail (request shapes, examples, edge cases), see:

- [endpoints/tasks.md](endpoints/tasks.md) — Issue / Task operations
- [endpoints/bulk.md](endpoints/bulk.md) — Bulk update / create
- [endpoints/search.md](endpoints/search.md) — Filter-based search
- [endpoints/automation.md](endpoints/automation.md) — Triggers, macros, autoactions
- [endpoints/agile.md](endpoints/agile.md) — Boards and sprints
- [endpoints/entities.md](endpoints/entities.md) — Projects, portfolios, goals
- [endpoints/queues.md](endpoints/queues.md) — Queue management
- [endpoints/fields.md](endpoints/fields.md) — Global and local fields
- [endpoints/comments.md](endpoints/comments.md) — Comments, reactions, checklists
- [endpoints/worklog.md](endpoints/worklog.md) — Time tracking
- [endpoints/attachments.md](endpoints/attachments.md) — File attachments
- [endpoints/import.md](endpoints/import.md) — Import API

## Common Workflows

See [endpoints/workflows.md](endpoints/workflows.md) for end-to-end patterns
(create task + links + file, bulk update, sprint setup, trigger configuration, etc.).

---

## API Gaps / Known Limitations

- **Template API** — issue templates can be viewed in UI but there is no stable public API to create or apply them programmatically
- **SLA API** — SLA configuration (`15-sla/`) is read-only via API; rules must be created and modified in the UI
- **Notification API** — notification subscription management (`10-notifications/`) has limited write support; most configuration is UI-only
- **Dashboard widget API** — dashboard creation (`12-dashboards/`) supports adding dashboards but widget configuration options are incomplete and underdocumented
- **Webhook structure** — `17-devtools/` documents webhook setup but payload schema for all event types is not fully documented; test webhooks in a dev queue before relying on specific fields
- **Workflow structure** — statuses, transitions, and required fields per transition cannot be created or modified via API; use the Tracker UI for all workflow configuration
- **Rate limits** — not prominently documented; in practice, bulk endpoints should be preferred over high-frequency individual calls to avoid throttling
