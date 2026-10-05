---
name: yandex-360-datalens
metadata:
  category: workflow
description: Use when reading or changing Yandex DataLens through ycli — collections and workbooks, what they hold, creating, moving and deleting them, the roles on them, which DataLens instance the credentials reach, and how to sign in to it — via the `ycli datalens` CLI, the `datalens_*` MCP tools, or the DataLensClient SDK.
---

# Yandex 360 DataLens

Drive Yandex DataLens via `ycli` through the CLI, the `datalens_*` MCP tools, or the `DataLensClient` SDK.

**In progress.** ycli wraps DataLens section by section. Today it wraps collections (the folders that hold workbooks) and workbooks, reads and writes, and the details of the DataLens instance. Connections, datasets, charts and dashboards are listed as the entries of a workbook but not opened or changed yet; this skill grows with each section.

## When to use

- Finding a collection or a workbook: listing the root and descending
- Listing what a workbook holds: its connections, datasets, charts and dashboards
- Creating, renaming, moving or deleting collections and workbooks
- Seeing or changing who has which role on a collection or a workbook
- Checking that the credentials reach DataLens, and which instance they reach
- Setting up the credentials DataLens needs, which differ from Tracker, Wiki and Forms

## When NOT to use

- Reading or editing Tracker issues — use `yandex-360-tracker`
- Reading or editing Wiki pages — use `yandex-360-wiki`
- Reading or editing Forms — use `yandex-360-forms`
- Opening or changing a connection, dataset, chart or dashboard — not wrapped yet

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

**`workbooks list` does not descend.** It lists one collection (the root by default); to find a workbook anywhere, walk `collections content-list`.

**An entry's `scope` is its kind**: `connection`, `dataset`, `widget` (a chart), `dash`, `report`. `entries-list` takes `--order-by '{"field": "name", "direction": "asc"}'` and `--filters '{"name": "sales"}'` as JSON objects.

**Content is mixed.** `content-list` returns collections, workbooks and entries in one list; `entity` says which (`collection`, `workbook`, `entry`). The root has no id: leave the id out (MCP: `collection_id` null).

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
| Lock an entry for editing | `uv run ycli datalens entrylocks create <entry_id> --data '{"duration": 300000}'` | `datalens_entrylocks_create` |
| Hold a lock longer | `uv run ycli datalens entrylocks extend <entry_id> --data '{"lockToken": "…", "duration": 600000}'` | `datalens_entrylocks_extend` |
| Release a lock | `uv run ycli datalens entrylocks delete <entry_id> --params '{"lockToken": "…"}'` | `datalens_entrylocks_delete` |

**No parent is the root.** Leave `--parent-id` / `parent_id` (a collection) or `--collection-id` / `collection_id` (a workbook) out to create in the root or to move there: `move <id>` with no destination moves it to the root.

**Deleting a collection or a workbook deletes what it holds**: nested collections, workbooks and their entries. The reply lists what was deleted.

**Roles change by deltas.** `access-bindings-update` does not replace the list: each delta adds or removes one role of one subject, and the roles it does not name stay.

```json
{"action": "ADD", "accessBinding": {"roleId": "datalens.collections.viewer", "subject": {"id": "<user id>", "type": "userAccount"}}}
```

`action` is `ADD` or `REMOVE`; subject `type` is one of `userAccount`, `federatedUser`, `serviceAccount`, `group`, `invitee`, `system`. It answers with an operation; `done` says whether it has been applied.

**A lock is held by its token.** `entrylocks create` answers with the token alone: keep it, `extend` and `delete` take it. The duration is in milliseconds. An entry that is already locked answers 423 `ERR.US.ENTRY_IS_LOCKED` with who holds the lock and until when; releasing an entry that is not locked answers 404.
