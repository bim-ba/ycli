---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/createWorkbook
title: "Yandex DataLens | DataLens API: Create workbook"
author: "Yandex Cloud"
extracted: "2026-07-09T13:31:25Z"
updated: 2026-03-16
---

# HTTP request

```
POST https://api.datalens.tech/rpc/createWorkbook
```

# Body parameters

**Request schema: application/json**

```
{
  "collectionId": "string | null",
  "title": "string",
  "description": "string"
}
```

| Field | Description |
| --- | --- |
| collectionId | **string \| null** |
| title | **string** Required field. |
| description | **string** |

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
  "status": "string",
  "operation": {
    "id": "string",
    "description": "string",
    "createdBy": "string",
    "createdAt": {
      "seconds": "string",
      "nanos": "number"
    },
    "modifiedAt": {
      "seconds": "string",
      "nanos": "number"
    },
    "metadata": {},
    "done": "boolean"
  }
}
```

| Field | Description |
| --- | --- |
| workbookId | **string** Required field. |
| collectionId | **string \| null** Required field. |
| title | **string** Required field. |
| description | **string \| null** Required field. |
| tenantId | **string** Required field. |
| meta | All of **[Meta0](https://yandex.cloud/ru/docs/datalens/openapi-ref/createWorkbook#Meta0)** & **object** (map<**string**, **unknown**>) |
| createdBy | **string** Required field. |
| createdAt | **string** Required field. |
| updatedBy | **string** Required field. |
| updatedAt | **string** Required field. |
| status | **enum** `creating`, `deleting`, `active` |
| operation | **[Operation](https://yandex.cloud/ru/docs/datalens/openapi-ref/createWorkbook#Operation)** Required field. |

| Field | Description |
| --- | --- |
| importId | **string** |

# Operation

| Field | Description |
| --- | --- |
| id | **string** Required field. |
| description | **string** Required field. |
| createdBy | **string** Required field. |
| createdAt | **[CreatedAt](https://yandex.cloud/ru/docs/datalens/openapi-ref/createWorkbook#CreatedAt)** Required field. |
| modifiedAt | **[ModifiedAt](https://yandex.cloud/ru/docs/datalens/openapi-ref/createWorkbook#ModifiedAt)** Required field. |
| metadata | **[Metadata](https://yandex.cloud/ru/docs/datalens/openapi-ref/createWorkbook#Metadata)** Required field. |
| done | **boolean** Required field. |

# CreatedAt

| Field | Description |
| --- | --- |
| seconds | **string** Required field. |
| nanos | **number** |

# ModifiedAt

| Field | Description |
| --- | --- |
| seconds | **string** Required field. |
| nanos | **number** |

| Field | Description |
| --- | --- |
| Empty |  |
