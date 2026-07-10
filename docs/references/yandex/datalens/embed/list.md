---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/listEmbeds
title: "Yandex DataLens | DataLens API: List embeds"
author: "Yandex Cloud"
extracted: "2026-07-09T13:33:20Z"
updated: 2026-03-16
---

Lists embeddings of the specified entry.

# HTTP request

```
POST https://api.datalens.tech/rpc/listEmbeds
```

# Body parameters

**Request schema: application/json**

```
{
  "entryId": "string"
}
```

| Field | Description |
| --- | --- |
| entryId | **string** Required field. ID of the entry to list embeddings for. |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
"array"
```
