---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/listEmbeddingSecrets
title: "Yandex DataLens | DataLens API: List embedding secrets"
author: "Yandex Cloud"
extracted: "2026-07-09T13:34:01Z"
updated: 2026-03-16
---

Lists keys for embedding of the specified workbook.

# HTTP request

```
POST https://api.datalens.tech/rpc/listEmbeddingSecrets
```

# Body parameters

**Request schema: application/json**

```
{
  "workbookId": "string"
}
```

| Field | Description |
| --- | --- |
| workbookId | **string** Required field. ID of the workbook to list its keys for embedding. |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
"array"
```
