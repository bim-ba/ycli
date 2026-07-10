---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/deleteEmbeddingSecret
title: "Yandex DataLens | DataLens API: Delete embedding secret"
author: "Yandex Cloud"
extracted: "2026-07-09T13:34:08Z"
updated: 2026-03-16
---

Deletes the specified key for embedding.

# HTTP request

```
POST https://api.datalens.tech/rpc/deleteEmbeddingSecret
```

# Body parameters

**Request schema: application/json**

```
{
  "embeddingSecretId": "string"
}
```

| Field | Description |
| --- | --- |
| embeddingSecretId | **string** Required field. ID of the key for embedding to delete. |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{
  "embeddingSecretId": "string"
}
```

| Field | Description |
| --- | --- |
| embeddingSecretId | **string** Required field. ID of the deleted key for embedding. |
