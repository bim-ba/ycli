---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/createEmbeddingSecret
title: "Yandex DataLens | DataLens API: Create embedding secret"
author: "Yandex Cloud"
extracted: "2026-07-09T13:33:51Z"
updated: 2026-03-16
---

Creates the key for embedding.

# HTTP request

```
POST https://api.datalens.tech/rpc/createEmbeddingSecret
```

# Body parameters

**Request schema: application/json**

```
{
  "title": "string",
  "workbookId": "string"
}
```

| Field | Description |
| --- | --- |
| title | **string** Required field. Name of the key for embedding to be created. |
| workbookId | **string** Required field. ID of the workbook to associate with the key for embedding. |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{
  "embeddingSecretId": "string",
  "privateKey": "string"
}
```

| Field | Description |
| --- | --- |
| embeddingSecretId | **string** Required field. ID of the newly created key for embedding. |
| privateKey | **string** Required field. Private key for accessing the embedding. |
