---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/createCollection
title: "Yandex DataLens | DataLens API: Create collection"
author: "Yandex Cloud"
extracted: "2026-07-09T13:26:33Z"
updated: 2026-03-16
---

# HTTP request

```
POST https://api.datalens.tech/rpc/createCollection
```

# Body parameters

**Request schema: application/json**

```
{
  "title": "string",
  "description": "string",
  "parentId": "string | null"
}
```

| Field | Description |
| --- | --- |
| title | **string** Required field. |
| description | **string** |
| parentId | **string \| null** Required field. |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{
  "collectionId": "string",
  "title": "string",
  "description": "string | null",
  "parentId": "string | null",
  "tenantId": "string",
  "createdBy": "string",
  "createdAt": "string",
  "updatedBy": "string",
  "updatedAt": "string",
  "meta": {
    "string": "unknown"
  },
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
| collectionId | **string** Required field. |
| title | **string** Required field. |
| description | **string \| null** Required field. |
| parentId | **string \| null** Required field. |
| tenantId | **string** Required field. |
| createdBy | **string** Required field. |
| createdAt | **string** Required field. |
| updatedBy | **string** Required field. |
| updatedAt | **string** Required field. |
| meta | **object** (map<**string**, **unknown**>) Required field. |
| operation | **[Operation](https://yandex.cloud/ru/docs/datalens/openapi-ref/createCollection#Operation)** Required field. |

# Operation

| Field | Description |
| --- | --- |
| id | **string** Required field. |
| description | **string** Required field. |
| createdBy | **string** Required field. |
| createdAt | **[CreatedAt](https://yandex.cloud/ru/docs/datalens/openapi-ref/createCollection#CreatedAt)** Required field. |
| modifiedAt | **[ModifiedAt](https://yandex.cloud/ru/docs/datalens/openapi-ref/createCollection#ModifiedAt)** Required field. |
| metadata | **[Metadata](https://yandex.cloud/ru/docs/datalens/openapi-ref/createCollection#Metadata)** Required field. |
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
