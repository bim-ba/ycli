---
name: yandex-360-datalens
metadata:
  category: workflow
description: Use when reading Yandex DataLens through ycli — which DataLens instance the credentials reach, and how to sign in to it — via the `ycli datalens` CLI, the `datalens_*` MCP tools, or the DataLensClient SDK.
---

# Yandex 360 DataLens

Drive Yandex DataLens via `ycli` through the CLI, the `datalens_*` MCP tools, or the `DataLensClient` SDK.

**In progress.** ycli wraps DataLens section by section. Today it wraps one operation: the details of the DataLens instance. Workbooks, connections, datasets, charts and dashboards are not wrapped yet; this skill grows with each section.

## When to use

- Checking that the credentials reach DataLens, and which instance they reach
- Setting up the credentials DataLens needs, which differ from Tracker, Wiki and Forms

## When NOT to use

- Reading or editing Tracker issues — use `yandex-360-tracker`
- Reading or editing Wiki pages — use `yandex-360-wiki`
- Reading or editing Forms — use `yandex-360-forms`
- Workbooks, connections, datasets, charts, dashboards — not wrapped yet

## Surfaces

- **CLI** — `uv run ycli datalens <group> <cmd>`
- **MCP** — `datalens_*` tools. Reads carry `readOnlyHint=True`.
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
