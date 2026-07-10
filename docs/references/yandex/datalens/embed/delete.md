---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/deleteEmbed
title: "Yandex DataLens | DataLens API: Delete embed"
author: "Yandex Cloud"
extracted: "2026-07-09T13:33:26Z"
updated: 2026-03-16
---

Deletes the specified embedding.

# HTTP request

```
POST https://api.datalens.tech/rpc/deleteEmbed
```

# Body parameters

**Request schema: application/json**

```
{
  "embedId": "string"
}
```

| Field | Description |
| --- | --- |
| embedId | **string** Required field. ID of the embedding to delete. |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{
  "embedId": "string"
}
```

| Field | Description |
| --- | --- |
| embedId | **string** Required field. ID of the deleted embedding. |
