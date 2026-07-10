---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/moveCollections
title: "Yandex DataLens | DataLens API: Move collections"
author: "Yandex Cloud"
extracted: "2026-07-09T13:27:46Z"
updated: 2026-03-16
---

# HTTP request

```
POST https://api.datalens.tech/rpc/moveCollections
```

# Body parameters

**Request schema: application/json**

```
{
  "collectionIds": [
    "string"
  ],
  "parentId": "string | null"
}
```

| Field | Description |
| --- | --- |
| collectionIds[] | **string** Required field. |
| parentId | **string \| null** Required field. |

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
