---
name: yandex-360-datalens
description: >-
  Use when reading or changing Yandex DataLens through ycli — collections,
  workbooks and the entries they hold (connections, datasets, charts, reports,
  dashboards and the rest), the roles on them, the export and import of a
  workbook, embedding, the audit, the members of the organization, and how to
  sign in to DataLens — via the `ycli datalens` CLI, the `datalens_*` MCP tools,
  or the DataLensClient SDK.
metadata:
  category: workflow
---
# Yandex 360 DataLens

Drive Yandex DataLens via `ycli` through the CLI, the `datalens_*` MCP tools, or the `DataLensClient` SDK.

**In progress.** ycli wraps DataLens section by section, and this skill grows with each one. Wrapped today, reads and writes unless said otherwise (one line a section):

- collections (the folders that hold workbooks) and workbooks
- the export of a workbook as one document and its import as a new workbook
- entries as such: finding them, their relations, revisions and permissions, renaming, locks
- connections
- datasets, with their rows
- charts built in the wizard, in QL and in the editor, and the data of a saved chart
- reports
- dashboards
- the embeds of an entry and the keys for embedding that sign them
- the roles on a shared entry
- the audit (reads)
- saved SQL queries (experimental in the API; written from its document, not measured)
- cloud environments and their storage bucket (experimental in the API; the listing measured, the rest written from the document and never called)
- REST catalogs and Lakehouse operations (experimental in the API; the listing of catalogs measured, the rest written from the document and never called)
- Trino clusters and their resource presets (experimental in the API; the listing of clusters measured, the rest written from the document and never called)
- Spark applications: listing, reading, making, cancelling one and reading its log (experimental in the API; written from the document, not measured)
- the members of the organization and the details of the DataLens instance (reads)
- the licences (seats) of the instance: reads measured; giving a licence and setting the limit written from the document, never called

## When to use

- Finding a collection or a workbook: listing the root and descending
- Listing what a workbook holds: its connections, datasets, charts and dashboards
- Creating, renaming, moving or deleting collections and workbooks
- Exporting everything a workbook holds as one document, and making a new workbook from it
- Listing, creating, changing or deleting the embeds of a chart or a dashboard, and the keys for embedding of a workbook
- Seeing or changing who has which role on a collection, a workbook or a shared entry
- Asking the audit which entries changed in a period, and what one user may do with an entry
- Finding an entry anywhere by kind or name, what it uses and what uses it, its revisions
- Checking what you may do with entries, workbooks and collections
- Renaming an entry, or locking it while you edit
- Finding the user, group or service account to give a role to
- Reading, creating, changing or deleting a connection to a database, a file or an API
- Reading, creating, changing, checking or deleting a dataset, and reading its rows
- Reading the data a saved chart shows
- Reading, creating, saving or deleting a chart of the wizard, a QL chart or a chart of the editor
- Reading, creating, saving or deleting a dashboard
- Checking that the credentials reach DataLens, and which instance they reach
- Setting up the credentials DataLens needs, which differ from Tracker, Wiki and Forms

## When NOT to use

- Reading or editing Tracker issues — use `yandex-360-tracker`
- Reading or editing Wiki pages — use `yandex-360-wiki`
- Reading or editing Forms — use `yandex-360-forms`

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
| Keys for embedding of a workbook (never the private key) | `uv run ycli datalens embeddingsecrets list <workbook_id>` · `get <embedding_secret_id>` | `datalens_embeddingsecrets_list` · `datalens_embeddingsecrets_get` |
| Where an entry is embedded | `uv run ycli datalens embeds list <entry_id>` | `datalens_embeds_list` |
| Who has which role on a shared entry | `uv run ycli datalens sharedentries access-bindings-list <entry_id> [--get-inherited-bindings]` | `datalens_sharedentries_access_bindings_list` |
| Entries changed in a period (deleted ones too) | `uv run ycli datalens audit entries-updates-list --from 2026-10-01T00:00:00Z [--to …] [--all]` | `datalens_audit_entries_updates_list` |
| What one user may do with entries | `uv run ycli datalens audit entry-permissions-get <entry_id>… --user-id <user_id>` | `datalens_audit_entry_permissions_get` |
| One saved SQL query (experimental) | `uv run ycli datalens sqlqueries get <sql_query_id>` | `datalens_sqlqueries_get` |
| Who holds a licence (a seat) | `uv run ycli datalens licensing licenses-list [--status active] [--user-ids <id>]… [--all]` | `datalens_licensing_licenses_list` |
| How many licences there may be, and how many are active | `uv run ycli datalens licensing limit-get` | `datalens_licensing_limit_get` |
| The cloud environments of the instance (experimental) | `uv run ycli datalens cloudenvironments list [--filter 'status="READY"'] [--all]` · `get <id>` | `datalens_cloudenvironments_list` · `datalens_cloudenvironments_get` |
| What a cloud environment's bucket holds (experimental) | `uv run ycli datalens cloudenvironmentstorage bucket-objects-list <cloud_environment_id> [--prefix …]` · `bucket-object-metadata-get <id> --path …` | `datalens_cloudenvironmentstorage_bucket_objects_list` · `…_bucket_object_metadata_get` |
| The REST catalogs of the instance (experimental) | `uv run ycli datalens restcatalogs list [--cloud-environment-id <id>] [--all]` | `datalens_restcatalogs_list` |
| How far a Lakehouse operation is (experimental) | `uv run ycli datalens lakehouseoperations get <operation_id>` | `datalens_lakehouseoperations_get` |
| The Trino clusters of the instance (experimental) | `uv run ycli datalens trinoclusters list [--collection-id <id>] [--all]` · `get <id>` | `datalens_trinoclusters_list` · `datalens_trinoclusters_get` |
| The sizes a Trino cluster's machines may have (experimental) | `uv run ycli datalens trinoclusters resource-presets-list <cloud_environment_id>` · `resource-preset-get <id> --cloud-environment-id <id>` | `datalens_trinoclusters_resource_presets_list` · `…_resource_preset_get` |
| The applications of a Spark cluster, and the log of one (experimental) | `uv run ycli datalens sparkapplications list <cluster_id>` · `get <cluster_id> --application-id <id>` · `log-list <cluster_id> --application-id <id> [--page-token …]` | `datalens_sparkapplications_list` · `…_get` · `…_log_list` |
| Users, groups and service accounts (to give a role to) | `uv run ycli datalens members list [--search …] [--tab-id GROUP] [--all]` | `datalens_members_list` |
| One connection (never its password or token) | `uv run ycli datalens connections get <connection_id>` | `datalens_connections_get` |
| One dataset: sources, joins, fields with their guids | `uv run ycli datalens datasets get <dataset_id>` | `datalens_datasets_get` |
| Rows of a dataset (one page) | `uv run ycli datalens datasets data-get <dataset_id> --columns <guid> --columns <guid> [--limit 100] [--offset 100 --sort '{"guid": "…", "direction": "asc"}']` | `datalens_datasets_data_get` |
| Check a dataset or a change to it, saving nothing | `uv run ycli datalens datasets validate <dataset_id> --body-file change.json` | `datalens_datasets_validate` |
| The data a saved chart shows, as tables | `uv run ycli datalens charts data-get <chart_id> [--params '{"year": "2026"}']` | `datalens_charts_data_get` |
| One chart, by how it is built | `uv run ycli datalens charts wizard get <chart_id>` · `charts ql get <chart_id>` · `charts editor get <chart_id>` | `datalens_charts_wizard_get` · `datalens_charts_ql_get` · `datalens_charts_editor_get` |
| One report: its slides and what stands on them | `uv run ycli datalens reports get <entry_id>` | `datalens_reports_get` |
| One dashboard (large: write it to a file) | `uv run ycli -o json datalens dashboards get <dashboard_id> > dash.json` | `datalens_dashboards_get` |

**`workbooks list` does not descend.** It lists one collection (the root by default); to find a workbook anywhere, walk `collections content-list`.

**Saving a report through the API loses part of it (measured, 2026-10-06).** `reports update` and `reports create` do not keep the `layout` of the elements of a slide (it comes back `null`) and drop part of `settings` (`autoupdateInterval`, `globalParams`, `loadPriority`, `maxConcurrentRequests`, `silentLoading`), `showInTOC` of an element and `autoHeight` of a tab: DataLens drops them without a word, though ycli sends them. A report saved this way loses where its elements stood. Do not update an existing report without telling the person first; a dashboard has no such loss.

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
| Make a key for embedding (prints the private key, once) | `uv run ycli -o json datalens embeddingsecrets create --title … --workbook-id <id> > secret.json` | `datalens_embeddingsecrets_create` |
| Delete a key for embedding | `uv run ycli datalens embeddingsecrets delete <embedding_secret_id>` | `datalens_embeddingsecrets_delete` |
| Embed an entry | `uv run ycli datalens embeds create --title … --embedding-secret-id <id> --entry-id <id> --public-params-mode --settings '{}'` | `datalens_embeds_create` |
| Save an embed as given | `uv run ycli datalens embeds update <embed_id> --title … --embedding-secret-id <id> --no-public-params-mode --settings '{}' [--unsigned-params …]` | `datalens_embeds_update` |
| Delete an embed | `uv run ycli datalens embeds delete <embed_id>` | `datalens_embeds_delete` |
| Give or take away roles on a shared entry | `uv run ycli datalens sharedentries access-bindings-update <entry_id> --delta '<json>'…` | `datalens_sharedentries_access_bindings_update` |
| Save a SQL query in a workbook (experimental) | `uv run ycli datalens sqlqueries create --workbook-id <id> --name … --connection-id <id> --query '…'` | `datalens_sqlqueries_create` |
| Save a SQL query anew | `uv run ycli datalens sqlqueries update <sql_query_id> --connection-id <id> --query '…'` | `datalens_sqlqueries_update` |
| Run a saved SQL query | `uv run ycli datalens sqlqueries run <sql_query_id> [--params '{"since": "2026-10-01"}']` | `datalens_sqlqueries_run` |
| Delete a saved SQL query | `uv run ycli datalens sqlqueries delete <sql_query_id>` | `datalens_sqlqueries_delete` |
| Give users a licence (billed; not measured) | `uv run ycli datalens licensing licenses-assign <user_id>…` | `datalens_licensing_licenses_assign` |
| Set how many licences there may be (billed; not measured) | `uv run ycli datalens licensing limit-set <value>` | `datalens_licensing_limit_set` |
| Rename an entry | `uv run ycli datalens entries rename <entry_id> --name …` | `datalens_entries_rename` |
| Create a connection | `uv run ycli datalens connections create --body-file conn.yaml` | `datalens_connections_create` |
| Change a connection | `uv run ycli datalens connections update <connection_id> --data '{"host": "db2"}'` | `datalens_connections_update` |
| Delete a connection | `uv run ycli datalens connections delete <connection_id>` | `datalens_connections_delete` |
| Create a dataset (empty is valid) | `uv run ycli datalens datasets create --name … --workbook-id <id> --dataset '{"sources": [], "result_schema": []}'` | `datalens_datasets_create` |
| Save a dataset as given | `uv run ycli datalens datasets update <dataset_id> --body-file dataset.json` | `datalens_datasets_update` |
| Delete a dataset | `uv run ycli datalens datasets delete <dataset_id>` | `datalens_datasets_delete` |
| Create a chart | `uv run ycli datalens charts wizard create --workbook-id <id> --name … --body-file chart.json` · `charts ql create --template ql …` · `charts editor create --body-file chart.json` | `datalens_charts_wizard_create` · `datalens_charts_ql_create` · `datalens_charts_editor_create` |
| Save a chart as given | `uv run ycli datalens charts wizard update <chart_id> --mode save --body-file chart.json` · `charts ql update <entry_id> --template ql --mode save …` · `charts editor update --mode save --body-file chart.json` | `datalens_charts_wizard_update` · `datalens_charts_ql_update` · `datalens_charts_editor_update` |
| Delete a chart | `uv run ycli datalens charts wizard delete <chart_id>` · `charts ql delete` · `charts editor delete` | `datalens_charts_wizard_delete` · `datalens_charts_ql_delete` · `datalens_charts_editor_delete` |
| Create a report (at least one slide) | `uv run ycli datalens reports create --workbook-id <id> --name … --meta null --body-file report.json` | `datalens_reports_create` |
| Save a report (loses the layout of slide elements: ask first) | `uv run ycli datalens reports update <entry_id> --mode save --body-file report.json` | `datalens_reports_update` |
| Delete a report | `uv run ycli datalens reports delete <entry_id>` | `datalens_reports_delete` |
| Create a dashboard | `uv run ycli datalens dashboards create --body-file dash.json` | `datalens_dashboards_create` |
| Save a dashboard as given | `uv run ycli datalens dashboards update --mode save --body-file dash.json [--lock-token …]` | `datalens_dashboards_update` |
| Delete a dashboard | `uv run ycli datalens dashboards delete <dashboard_id>` | `datalens_dashboards_delete` |
| Lock an entry for editing | `uv run ycli datalens entrylocks create <entry_id> --data '{"duration": 300000}'` | `datalens_entrylocks_create` |
| Hold a lock longer | `uv run ycli datalens entrylocks extend <entry_id> --data '{"lockToken": "…", "duration": 600000}'` | `datalens_entrylocks_extend` |
| Release a lock | `uv run ycli datalens entrylocks delete <entry_id> --params '{"lockToken": "…"}'` | `datalens_entrylocks_delete` |

**No parent is the root.** Leave `--parent-id` / `parent_id` (a collection) or `--collection-id` / `collection_id` (a workbook) out to create in the root or to move there: `move <id>` with no destination moves it to the root.

**A workbook is exported and imported in steps.** `workbookexports start` answers an export id at once; ask `workbookexports status-get` until `status` is `success` (`pending` before, `error` if it failed), then `workbookexports result-get`. Its `data` (the `export` and its `hash`, together) is what `workbookimports start` takes: `… result-get <export_id> | jq '{data}' > export.json`, then `workbookimports start --body-file export.json --title …`. The new workbook exists at once and is filled as the import runs; `workbookimports status-get` says when it is done. A cancelled export ends with the status `error` and the notification `WORKBOOK_EXPORT_CANCELLED`; cancelling one that is over changes nothing. The result of an export that is not over, or was cancelled, answers 409; an id nothing knows answers 404.

**After an import, give the connections their secrets again.** A password or a token is not in the exported document: the status of the export and of the import carries a notification for each connection (`NOTIF.WB_EXPORT.CONN.CHECK_CREDENTIALS`, `NOTIF.WB_IMPORT.CONN.CHECK_CREDENTIALS`), and the imported connection works once `connections update` has given it the secret.

**Write the exported document to a file, do not read it.** A workbook with a dashboard exports to hundreds of kilobytes (287 KB for 27 entries, measured): redirect `workbookexports result-get` to a file and hand the file to `workbookimports start --body-file`; an agent that takes the document into its context spends it on nothing.

**A shared entry lies in a collection, not in a workbook.** A connection or a dataset created with `--collection-id` (and no `--workbook-id`) is one: workbooks may use it, and it has roles of its own, `datalens.sharedEntries.*` (`admin`, `viewer`), changed by deltas as on a collection. `sharedentries access-bindings-list` of an entry that lies in a workbook, or of an id nothing knows, answers an empty list, not an error. A change of roles answers an operation that may not be done yet (`done: false`): read the roles again to see it.

**The audit is asked with a start time.** `audit entries-updates-list` requires `--from` (ISO-8601 with its zone) and lists every entry changed since, deleted ones included (`isDeleted`), with who changed it. `audit entry-permissions-get` answers by entry id: `permissions` (`execute`, `read`, `edit`, `admin`), or `error` for an entry that does not exist; the user's id is the one `createdBy` of an entry gives.

**Cloud environments are experimental, and all but their listing is not measured.** A cloud environment is a cloud and a subnet DataLens runs clusters in, with a storage bucket. `cloudenvironments list` is measured (an instance with none answers an empty list; a filter is `field="value"` over `name`, `cloud_id`, `status`, `created_by_id`, the quotes included). `cloudenvironments create`, `update` and `delete` make and change resources in a cloud, which may be billed: they are written from the published document and were never called; ask the person before any of them. Each answers an operation that is not done yet. The four `cloudenvironmentstorage` commands (the paths in the bucket, the size of an object, a signed link to read or to put one) are written from the document too; a signed link works for whoever holds it. An id nothing knows answers 403 Permission denied, not 404: it is not a lack of rights.

**Spark applications are experimental, and not measured.** Every command takes the Spark cluster (without it the API answers 400; a cluster nothing knows answers 403, not 404), and the owner's instance has none, so the section is written from the published document. `sparkapplications log-list` answers one fragment of the log and the token of the next: give it back as `--page-token` to read on. `sparkapplications create` takes exactly one of three kinds, `--spark-application` (a JAR), `--pyspark-application` (a Python file) or `--spark-connect-application`, each a JSON object; over MCP the kind is the field of `body` that holds the application (`sparkApplication`, `pysparkApplication`, `sparkConnectApplication`). `create` and `cancel` were never called: ask the person before either.

**Trino clusters are experimental, and billed while they run.** `trinoclusters list` is measured (an instance with none answers an empty list). Everything else is written from the published document and was never called: `create`, `start`, `stop`, `delete`, `catalog-create` and `catalog-delete` make or change cloud resources; ask the person before any of them. Each answers an operation to follow with `lakehouseoperations get`. The resource presets are read for a cloud environment, which is required (without it the API answers 400). An id nothing knows answers 403 Permission denied, not 404; a collection nothing knows, given to `list`, answered 500.

**REST catalogs and Lakehouse operations are experimental too.** `restcatalogs list` is measured (an instance with none answers an empty list). `restcatalogs create` makes a bucket in a cloud, which may be billed: written from the document, never called; ask the person first. It answers an operation, as making a cloud environment does: `lakehouseoperations get <operation_id>` says whether it is `done`, and then its `error` or its `response`.

**A licence is a seat DataLens bills for.** Yandex's pricing counts the seats of the instance (the number of seats times the cost of one), so `licensing licenses-assign` and `licensing limit-set` change what the organization pays: ask the person before either. Both are written from the published document and were never called. The reads are measured: `licenses-list` answers whose each licence is, its type (`creator` or `viewer`) and whether it is active; `limit-get` answers the limit in force with the count of active licences, and `next: null` when no change is set.

**Saved SQL queries are experimental, and not measured.** DataLens marks the whole section experimental; ycli wraps it from the published document, and no reply of it was checked against the service. An organization whose SQL editor is off answers `403 SQL_EDITOR_NOT_ALLOWED` to every call. A query runs over a connection to PostgreSQL, ClickHouse, MySQL, Greenplum or Trino; `sqlqueries run` runs the text as it is saved, so a text that changes data changes it. `sqlqueries update` takes the connection and the text every time.

**The private key of a key for embedding is given once.** `embeddingsecrets create` answers the id and the private key; `get` and `list` never return the key again, so write it to a file at once (`-o json … > secret.json`, a file nobody else reads) and do not paste it anywhere. Through MCP the key comes in the tool's result, into the agent's context: hand it over at once and do not repeat it.

**An embed is saved whole.** `embeds update` replaces the embed: the API requires the title, the key, the mode of parameters and the settings every time, and a list left out (`--deps-ids`, `--unsigned-params`, `--private-params`) is saved empty. Read the embed with `embeds list` first and name what is to stay. Deleting an embed twice answers 404.

**Deleting a collection or a workbook deletes what it holds**: nested collections, workbooks and their entries. The reply lists what was deleted.

**Roles change by deltas.** `access-bindings-update` does not replace the list: each delta adds or removes one role of one subject, and the roles it does not name stay.

```json
{"action": "ADD", "accessBinding": {"roleId": "datalens.collections.viewer", "subject": {"id": "<user id>", "type": "userAccount"}}}
```

The subject's `id` is the `sub` of a member (`members list`). `action` is `ADD` or `REMOVE`; subject `type` is one of `userAccount`, `federatedUser`, `serviceAccount`, `group`, `invitee`, `system`. It answers with an operation; `done` says whether it has been applied.

**A lock is held by its token.** `entrylocks create` answers with the token alone: keep it, `extend` and `delete` take it. The duration is in milliseconds. An entry that is already locked answers 423 `ERR.US.ENTRY_IS_LOCKED` with who holds the lock and until when; releasing an entry that is not locked answers 404.

**Permissions come as a map by id.** `entries permissions-get` and `permissions get-bulk` answer `{<id>: {"permissions": {…}}}`; an id that does not exist answers `{<id>: {"error": "NOT_FOUND"}}` in the same map, and an id of a wrong form refuses the whole request. `entries list` needs `--scope`, `--scopes` or `--id`; an entry you may not read comes with `isLocked: true` and little else.

**A connection is its kind.** `type` (`clickhouse`, `postgres`, `gsheets`, `json_api`… 29 kinds) says which fields it takes; over MCP read them with `schema_get(service="datalens", name="ConnectionCreate")`, then the definition of the kind. `connections get` answers with the kind in `db_type` and never with the password or the token. A connection to Google Sheets cannot be created through the API (`type: gsheets` answers 400 "This connection type is not editable"): make it in the DataLens interface, where its kind is `gsheets_v2`, then read it and build datasets on it here.

**Give a secret in a file.** A password or a token comes from a file outside the repository, mode 600: in `--body-file`, or as one field with `-F password=@secret.txt`. Typed after `-F` or in `--data` it stays in the shell history. Write the file of one field with no line break at its end (`printf %s 'secret' > secret.txt`), or the break goes out with the secret. `--dry-run` prints a secret as `***`, and a model prints it as `**********`; only the request itself carries it.

**A dataset is changed whole.** Read it with `datasets get`, change `dataset` (sources, `result_schema`, filters), and send it back as `data.dataset` of `datasets update`; `--body-file` holds it under `data`. Try the change with `datasets validate` first: it saves nothing and answers `code`, `message` and `dataset_errors`. Read the dataset again after every save: content of an older revision is refused (`ERR.DS_API.DATASET_REVISION_MISMATCH`). A source or a field of a kind ycli does not know comes and goes back as it is. Over MCP the body is read with `schema_get(service="datalens", name="DatasetUpdate")`.

**Rows are asked for by guid.** `datasets data-get` takes the guids of fields (`dataset.result_schema[].guid`), not their titles. One call is one page: `--limit` rows (100 by default) from `--offset`, and an offset above zero needs `--sort`, or the API refuses the request.

**A chart is read by how it is built.** An entry of the scope `widget` is a chart, and its `type` says which command reads it: `…_wizard_node` is `charts wizard`, `…_ql_node` is `charts ql`, the rest (`table_node`, `d3_node`, `markdown_node`, `advanced-chart_node`, `control_node`) is `charts editor`. A chart is changed whole, like a dataset: read it, change `entry.data`, send it back with `--mode save` (a draft) or `--mode publish`. `--body-file` gives the request itself (`data`, `workbookId`, `name`), and a flag lies over it. Over MCP the content of a wizard chart is read with `schema_get(service="datalens", name="WizardChartData")`. QL charts take `--template ql`, the only value the API accepts today, and come flat, with no `entry` around them.

**A dashboard is large and changed whole.** A real one is 100 KB and more, which may be over what a client shows of a tool's reply: read a big one into a file with the CLI and work on the file. To change it, read it, change `entry.data` (tabs, and the charts, selectors and texts on them) and send it back in `--body-file` as `{"entry": {"entryId": …, "data": …, "meta": …, "revId": …}}` with `--mode save` or `--mode publish`. A new dashboard needs `counter`, `salt`, `settings` and `tabs` in its `data`; a tab may be empty. Over MCP the entry is read with `schema_get(service="datalens", name="DashboardUpdate")`.
