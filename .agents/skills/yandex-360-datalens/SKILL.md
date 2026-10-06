---
name: yandex-360-datalens
description: >-
  Use when reading or changing Yandex DataLens through ycli — collections and
  workbooks, what they hold, creating, moving and deleting them, exporting a
  workbook and importing it as a new one, the roles on them, finding entries
  anywhere with their relations, revisions and permissions, renaming and locking
  an entry, connections to data sources, datasets and their rows, the data of a
  chart, the members of the organization, which DataLens instance the
  credentials reach, and how to sign in to it — via the `ycli datalens` CLI, the
  `datalens_*` MCP tools, or the DataLensClient SDK.
---
# Yandex 360 DataLens

Drive Yandex DataLens via `ycli` through the CLI, the `datalens_*` MCP tools, or the `DataLensClient` SDK.

**In progress.** ycli wraps DataLens section by section. Today it wraps collections (the folders that hold workbooks) and workbooks, reads and writes, with the export of a workbook as one document and its import as a new workbook; entries as such (finding them, their relations, revisions and permissions, renaming, locks); connections and datasets, reads and writes, with the rows of a dataset and the data of a saved chart; the members of the organization; and the details of the DataLens instance. Charts and dashboards are found and listed as entries but their content is not opened or changed yet; this skill grows with each section.

## When to use

- Finding a collection or a workbook: listing the root and descending
- Listing what a workbook holds: its connections, datasets, charts and dashboards
- Creating, renaming, moving or deleting collections and workbooks
- Exporting everything a workbook holds as one document, and making a new workbook from it
- Seeing or changing who has which role on a collection or a workbook
- Finding an entry anywhere by kind or name, what it uses and what uses it, its revisions
- Checking what you may do with entries, workbooks and collections
- Renaming an entry, or locking it while you edit
- Finding the user, group or service account to give a role to
- Reading, creating, changing or deleting a connection to a database, a file or an API
- Reading, creating, changing, checking or deleting a dataset, and reading its rows
- Reading the data a saved chart shows
- Checking that the credentials reach DataLens, and which instance they reach
- Setting up the credentials DataLens needs, which differ from Tracker, Wiki and Forms

## When NOT to use

- Reading or editing Tracker issues — use `yandex-360-tracker`
- Reading or editing Wiki pages — use `yandex-360-wiki`
- Reading or editing Forms — use `yandex-360-forms`
- Opening or changing the content of a chart or dashboard — not wrapped yet

## Surfaces

- **CLI** — `uv run ycli datalens <group> <cmd>`
- **MCP** — `datalens_*` tools, reads and writes. Write tools carry honest annotations (`readOnlyHint=False`, explicit `destructiveHint`); `ycli mcp start --read-only` hides them.
- **SDK** — `from ycli.yandex.datalens.client import DataLensClient` → `DataLensClient(auth=IAMTokenAuth(SecretStr(…)), cloud_organization_id=…)` (`IAMTokenAuth` from `ycli.yandex.core.auth`)

---

## 1. Auth and hosts

Public API (`api.datalens.tech`), every operation is `POST /rpc/<name>`:

```text
Authorization: Bearer $YANDEX_CLOUD_IAM_TOKEN
x-dl-org-id: $YANDEX_CLOUD_ORGANIZATION_ID
x-dl-api-version: 3
```

DataLens differs from the other services in both credentials:

- **The token is an IAM token, not an OAuth token.** Set `YANDEX_CLOUD_IAM_TOKEN` (`yc iam create-token`; it lives up to 12 hours) or a service account's key in `YANDEX_CLOUD_SERVICE_ACCOUNT_KEY_FILE`. A Yandex ID OAuth token (`YANDEX_ID_OAUTH_TOKEN`) is not taken. ycli holds one way to sign in at a time.
- **The organization is a Yandex Cloud organization**, in `YANDEX_CLOUD_ORGANIZATION_ID`; the Yandex 360 organization id does not name it.

**Not configured is not a failure.** With an OAuth token, or without a Yandex Cloud organization, `ycli auth status` lists `datalens` as not configured (`"configured": false`, `detail` says what to set) and still exits 0; `ycli doctor` skips it. A `ycli datalens …` command then exits 2 with the same text and sends nothing.

**403 `LICENSE_IS_REQUIRED`** means the account has no DataLens seat in that organization: the instance details still answer, every other operation is refused.

---

## 2. Reading

| Operation | CLI | MCP tool |
|-----------|-----|----------|
| Auth probe (the DataLens instance) | `uv run ycli datalens tenant details-get` | `datalens_tenant_details_get` |
| Probe only this service | `uv run ycli datalens auth status` | — |
| What the root holds | `uv run ycli datalens collections content-list` | `datalens_collections_content_list` |
| What a collection holds | `uv run ycli datalens collections content-list <collection_id> [--mode onlyWorkbooks] [--all]` | `datalens_collections_content_list` |
| One collection | `uv run ycli datalens collections get <collection_id>` | `datalens_collections_get` |
| Several collections by id | `uv run ycli datalens collections list-by-ids <id> <id>…` | `datalens_collections_list_by_ids` |
| Path from the root | `uv run ycli datalens collections breadcrumbs-list <collection_id>` | `datalens_collections_breadcrumbs_list` |
| What you may create in the root | `uv run ycli datalens collections permissions-get-root` | `datalens_collections_permissions_get_root` |
| Who has which role | `uv run ycli datalens collections access-bindings-list <collection_id> [--get-inherited-bindings]` | `datalens_collections_access_bindings_list` |
| Workbooks of the root, or of one collection | `uv run ycli datalens workbooks list [--collection-id <id>] [--filter-string …] [--all]` | `datalens_workbooks_list` |
| One workbook | `uv run ycli datalens workbooks get <workbook_id>` | `datalens_workbooks_get` |
| Several workbooks by id | `uv run ycli datalens workbooks list-by-ids <id> <id>…` | `datalens_workbooks_list_by_ids` |
| What a workbook holds | `uv run ycli datalens workbooks entries-list <workbook_id> [--scope dash] [--scope dataset] [--all]` | `datalens_workbooks_entries_list` |
| Who has which role on a workbook | `uv run ycli datalens workbooks access-bindings-list <workbook_id>` | `datalens_workbooks_access_bindings_list` |
| Find entries anywhere (give a scope or ids) | `uv run ycli datalens entries list --scope dash [--filters '{"name": "sales"}'] [--all]` | `datalens_entries_list` |
| What an entry uses, or what uses it | `uv run ycli datalens entries relations-list <entry_id>… --link-direction from\|to` | `datalens_entries_relations_list` |
| Revisions of an entry | `uv run ycli datalens entries revisions-list <entry_id>` | `datalens_entries_revisions_list` |
| What you may do with entries | `uv run ycli datalens entries permissions-get <entry_id>…` | `datalens_entries_permissions_get` |
| What you may do with many entries, workbooks and collections | `uv run ycli datalens permissions get-bulk --entry-id … --workbook-id … --collection-id …` | `datalens_permissions_get_bulk` |
| How far an export of a workbook is | `uv run ycli datalens workbookexports status-get <export_id>` | `datalens_workbookexports_status_get` |
| The exported workbook, as one document | `uv run ycli datalens workbookexports result-get <export_id>` | `datalens_workbookexports_result_get` |
| How far an import is | `uv run ycli datalens workbookimports status-get <import_id>` | `datalens_workbookimports_status_get` |
| Users, groups and service accounts (to give a role to) | `uv run ycli datalens members list [--search …] [--tab-id GROUP] [--all]` | `datalens_members_list` |
| One connection (never its password or token) | `uv run ycli datalens connections get <connection_id>` | `datalens_connections_get` |
| One dataset: sources, joins, fields with their guids | `uv run ycli datalens datasets get <dataset_id>` | `datalens_datasets_get` |
| Rows of a dataset (one page) | `uv run ycli datalens datasets data-get <dataset_id> --columns <guid> --columns <guid> [--limit 100] [--offset 100 --sort '{"guid": "…", "direction": "asc"}']` | `datalens_datasets_data_get` |
| Check a dataset or a change to it, saving nothing | `uv run ycli datalens datasets validate <dataset_id> --body-file change.json` | `datalens_datasets_validate` |
| The data a saved chart shows, as tables | `uv run ycli datalens charts data-get <chart_id> [--params '{"year": "2026"}']` | `datalens_charts_data_get` |

**`workbooks list` does not descend.** It lists one collection (the root by default); to find a workbook anywhere, walk `collections content-list`.

**An entry's `scope` is its kind**: `connection`, `dataset`, `widget` (a chart), `dash`, `report`. `entries-list` takes `--order-by '{"field": "name", "direction": "asc"}'` and `--filters '{"name": "sales"}'` as JSON objects.

**Content is mixed.** `content-list` returns collections, workbooks and entries in one list; `entity` says which (`collection`, `workbook`, `entry`); a kind DataLens adds later comes as it is, with its own `entity`. The root has no id: leave the id out (MCP: `collection_id` null).

---

## 3. Writing

An operation takes the fields of its request as arguments, under one name on every surface: `--parent-id` in the CLI, `parent_id` in a tool and in the SDK.

| Operation | CLI | MCP tool |
|-----------|-----|----------|
| Create a collection | `uv run ycli datalens collections create --title … [--parent-id <id>] [--description …]` | `datalens_collections_create` |
| Rename or describe | `uv run ycli datalens collections update <collection_id> [--title …] [--description …]` | `datalens_collections_update` |
| Move one | `uv run ycli datalens collections move <collection_id> [--parent-id <id>] [--title …]` | `datalens_collections_move` |
| Move several | `uv run ycli datalens collections move-bulk <id> <id>… [--parent-id <id>]` | `datalens_collections_move_bulk` |
| Delete one | `uv run ycli datalens collections delete <collection_id>` | `datalens_collections_delete` |
| Delete several | `uv run ycli datalens collections delete-bulk <id> <id>…` | `datalens_collections_delete_bulk` |
| Give or take away roles | `uv run ycli datalens collections access-bindings-update <collection_id> --delta '<json>'…` | `datalens_collections_access_bindings_update` |
| Create a workbook | `uv run ycli datalens workbooks create --title … [--collection-id <id>] [--description …]` | `datalens_workbooks_create` |
| Rename or describe a workbook | `uv run ycli datalens workbooks update <workbook_id> [--title …] [--description …]` | `datalens_workbooks_update` |
| Move one or several workbooks | `uv run ycli datalens workbooks move <workbook_id> [--collection-id <id>]` · `move-bulk <id> <id>…` | `datalens_workbooks_move` · `datalens_workbooks_move_bulk` |
| Delete one or several workbooks | `uv run ycli datalens workbooks delete <workbook_id>` · `delete-bulk <id> <id>…` | `datalens_workbooks_delete` · `datalens_workbooks_delete_bulk` |
| Give or take away roles on a workbook | `uv run ycli datalens workbooks access-bindings-update <workbook_id> --delta '<json>'…` | `datalens_workbooks_access_bindings_update` |
| Start exporting a workbook | `uv run ycli datalens workbookexports start <workbook_id>` | `datalens_workbookexports_start` |
| Stop an export | `uv run ycli datalens workbookexports cancel <export_id>` | `datalens_workbookexports_cancel` |
| Make a workbook from an export | `uv run ycli datalens workbookimports start --body-file export.json --title … [--collection-id <id>]` | `datalens_workbookimports_start` |
| Rename an entry | `uv run ycli datalens entries rename <entry_id> --name …` | `datalens_entries_rename` |
| Create a connection | `uv run ycli datalens connections create --body-file conn.yaml` | `datalens_connections_create` |
| Change a connection | `uv run ycli datalens connections update <connection_id> --data '{"host": "db2"}'` | `datalens_connections_update` |
| Delete a connection | `uv run ycli datalens connections delete <connection_id>` | `datalens_connections_delete` |
| Create a dataset (empty is valid) | `uv run ycli datalens datasets create --name … --workbook-id <id> --dataset '{"sources": [], "result_schema": []}'` | `datalens_datasets_create` |
| Save a dataset as given | `uv run ycli datalens datasets update <dataset_id> --body-file dataset.json` | `datalens_datasets_update` |
| Delete a dataset | `uv run ycli datalens datasets delete <dataset_id>` | `datalens_datasets_delete` |
| Lock an entry for editing | `uv run ycli datalens entrylocks create <entry_id> --data '{"duration": 300000}'` | `datalens_entrylocks_create` |
| Hold a lock longer | `uv run ycli datalens entrylocks extend <entry_id> --data '{"lockToken": "…", "duration": 600000}'` | `datalens_entrylocks_extend` |
| Release a lock | `uv run ycli datalens entrylocks delete <entry_id> --params '{"lockToken": "…"}'` | `datalens_entrylocks_delete` |

**No parent is the root.** Leave `--parent-id` / `parent_id` (a collection) or `--collection-id` / `collection_id` (a workbook) out to create in the root or to move there: `move <id>` with no destination moves it to the root.

**A workbook is exported and imported in steps.** `workbookexports start` answers an export id at once; ask `workbookexports status-get` until `status` is `success` (`pending` before, `error` if it failed), then `workbookexports result-get`. Its `data` (the `export` and its `hash`, together) is what `workbookimports start` takes: `… result-get <export_id> | jq '{data}' > export.json`, then `workbookimports start --body-file export.json --title …`. The new workbook exists at once and is filled as the import runs; `workbookimports status-get` says when it is done. The result of an export that is not over, or was cancelled, answers 409; an id nothing knows answers 404.

**Deleting a collection or a workbook deletes what it holds**: nested collections, workbooks and their entries. The reply lists what was deleted.

**Roles change by deltas.** `access-bindings-update` does not replace the list: each delta adds or removes one role of one subject, and the roles it does not name stay.

```json
{"action": "ADD", "accessBinding": {"roleId": "datalens.collections.viewer", "subject": {"id": "<user id>", "type": "userAccount"}}}
```

The subject's `id` is the `sub` of a member (`members list`). `action` is `ADD` or `REMOVE`; subject `type` is one of `userAccount`, `federatedUser`, `serviceAccount`, `group`, `invitee`, `system`. It answers with an operation; `done` says whether it has been applied.

**A lock is held by its token.** `entrylocks create` answers with the token alone: keep it, `extend` and `delete` take it. The duration is in milliseconds. An entry that is already locked answers 423 `ERR.US.ENTRY_IS_LOCKED` with who holds the lock and until when; releasing an entry that is not locked answers 404.

**Permissions come as a map by id.** `entries permissions-get` and `permissions get-bulk` answer `{<id>: {"permissions": {…}}}`; an id that does not exist answers `{<id>: {"error": "NOT_FOUND"}}` in the same map, and an id of a wrong form refuses the whole request. `entries list` needs `--scope`, `--scopes` or `--id`; an entry you may not read comes with `isLocked: true` and little else.

**A connection is its kind.** `type` (`clickhouse`, `postgres`, `gsheets`, `json_api`… 29 kinds) says which fields it takes; over MCP read them with `schema_get(service="datalens", name="ConnectionCreate")`, then the definition of the kind. `connections get` answers with the kind in `db_type` and never with the password or the token.

**Give a secret in a file.** A password or a token goes in `--body-file` (a file outside the repository, mode 600), not in `-F` or `--data`: a command line stays in the shell history. `--dry-run` prints a secret as `***`, and a model prints it as `**********`; only the request itself carries it.

**A dataset is changed whole.** Read it with `datasets get`, change `dataset` (sources, `result_schema`, filters), and send it back as `data.dataset` of `datasets update`; `--body-file` holds it under `data`. Try the change with `datasets validate` first: it saves nothing and answers `code`, `message` and `dataset_errors`. Read the dataset again after every save: content of an older revision is refused (`ERR.DS_API.DATASET_REVISION_MISMATCH`). A source or a field of a kind ycli does not know comes and goes back as it is. Over MCP the body is read with `schema_get(service="datalens", name="DatasetUpdate")`.

**Rows are asked for by guid.** `datasets data-get` takes the guids of fields (`dataset.result_schema[].guid`), not their titles. One call is one page: `--limit` rows (100 by default) from `--offset`, and an offset above zero needs `--sort`, or the API refuses the request.
