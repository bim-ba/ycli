---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/moveCollection
title: "Yandex DataLens | DataLens API: Move collection"
author: "Yandex Cloud"
extracted: "2026-07-09T13:27:41Z"
updated: 2026-03-16
---

# HTTP request

```
POST https://api.datalens.tech/rpc/moveCollection
```

# Body parameters

**Request schema: application/json**

```
{
  "collectionId": "string",
  "parentId": "string | null",
  "title": "string"
}
```

| Field | Description |
| --- | --- |
| collectionId | **string** Required field. |
| parentId | **string \| null** Required field. |
| title | **string** |

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
