---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/moveWorkbook
title: "Yandex DataLens | DataLens API: Move workbook"
author: "Yandex Cloud"
extracted: "2026-07-09T13:32:07Z"
updated: 2026-03-16
---

# HTTP request

```
POST https://api.datalens.tech/rpc/moveWorkbook
```

# Body parameters

**Request schema: application/json**

```
{
  "workbookId": "string",
  "collectionId": "string | null",
  "title": "string"
}
```

| Field | Description |
| --- | --- |
| workbookId | **string** Required field. |
| collectionId | **string \| null** Required field. |
| title | **string** |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{
  "workbookId": "string",
  "collectionId": "string | null",
  "title": "string",
  "description": "string | null",
  "tenantId": "string",
  "meta": "unknown",
  "createdBy": "string",
  "createdAt": "string",
  "updatedBy": "string",
  "updatedAt": "string",
  "status": "string"
}
```

| Field | Description |
| --- | --- |
| workbookId | **string** Required field. |
| collectionId | **string \| null** Required field. |
| title | **string** Required field. |
| description | **string \| null** Required field. |
| tenantId | **string** Required field. |
| meta | All of **[Meta0](https://yandex.cloud/ru/docs/datalens/openapi-ref/moveWorkbook#Meta0)** & **object** (map<**string**, **unknown**>) |
| createdBy | **string** Required field. |
| createdAt | **string** Required field. |
| updatedBy | **string** Required field. |
| updatedAt | **string** Required field. |
| status | **enum** `creating`, `deleting`, `active` |

| Field | Description |
| --- | --- |
| importId | **string** |
