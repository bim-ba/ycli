---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/getQlChart
title: "Yandex DataLens | DataLens API: 🚧 [Experimental] Get QL chart"
author: "Yandex Cloud"
extracted: "2026-07-09T13:30:19Z"
updated: 2026-03-16
---

# HTTP request

Returns the specified QL chart.

```
POST https://api.datalens.tech/rpc/getQLChart
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
| chartId | **string** Required field. ID of the QL chart to return. You can find it in the chart settings in DataLens interface. |
| workbookId | **string \| null** ID of the workbook the QL chart belongs to. If navigation across folders is enabled and the QL chart belongs to a folder, the value must be `null`. |
| revId | **string** Version ID for the QL chart. If the field is empty, you will get the current version of the QL chart. |
| includePermissions | **boolean** Include information on configured permissions in the response. |
| includeLinks | **boolean** Include information on configured links in the response. |
| includeFavorite | **boolean** Include favorite status in the response. |
| branch | **enum** `saved`, `published` |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
"unknown"
```
