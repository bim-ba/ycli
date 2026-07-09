---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/deleteCollection
title: "Yandex DataLens | DataLens API: Delete collection"
author: "Yandex Cloud"
extracted: "2026-07-09T13:26:39Z"
updated: 2026-03-16
---

# HTTP request

```
POST https://api.datalens.tech/rpc/deleteCollection
```

# Body parameters

**Request schema: application/json**

```
{
  "collectionId": "string"
}
```

| Field | Description |
| --- | --- |
| collectionId | **string** Required field. |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{
  "collections": [
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
  ]
}
```

# CollectionsItem

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
