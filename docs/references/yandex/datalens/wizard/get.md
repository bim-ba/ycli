---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/getWizardChart
title: "Yandex DataLens | DataLens API: 🚧 [Experimental] Get wizard chart"
author: "Yandex Cloud"
extracted: "2026-07-09T13:31:01Z"
updated: 2026-03-16
---

# HTTP request

```
POST https://api.datalens.tech/rpc/getWizardChart
```

# Body parameters

**Request schema: application/json**

```
{
  "chartId": "string",
  "workbookId": "string | null",
  "revId": "string",
  "includePermissions": "boolean",
  "includeLinks": "boolean",
  "includeFavorite": "boolean",
  "branch": "string"
}
```

| Field | Description |
| --- | --- |
| chartId | **string** Required field. |
| workbookId | **string \| null** |
| revId | **string** |
| includePermissions | **boolean** |
| includeLinks | **boolean** |
| includeFavorite | **boolean** |
| branch | **enum** `saved`, `published` |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
"unknown"
```
