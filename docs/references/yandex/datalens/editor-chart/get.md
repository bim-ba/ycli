---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/getEditorChart
title: "Yandex DataLens | DataLens API: 🚧 [Experimental] Get editor chart"
author: "Yandex Cloud"
extracted: "2026-07-09T13:32:41Z"
---

Returns the specified Editor chart.

# HTTP request

```
POST https://api.datalens.tech/rpc/getEditorChart
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
| chartId | **string** Required field. ID of the Editor chart to return. You can find it in the chart settings in DataLens interface. |
| workbookId | **string \| null** ID of the workbook the Editor chart belongs to. If navigation across folders is enabled and the Editor chart belongs to a folder, the value must be null. |
| revId | **string** Version ID for the Editor chart. |
| includePermissions | **boolean** Include information on configured permissions in the response. |
| includeLinks | **boolean** Include information on configured links in the response. |
| includeFavorite | **boolean** Include favorite status in the response. |
| branch | **enum** `saved` |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{
  "isFavorite": "boolean",
  "permissions": {
    "execute": "boolean",
    "read": "boolean",
    "edit": "boolean",
    "admin": "boolean"
  },
  "entry": "unknown"
}
```

# Permissions

| Field | Description |
| --- | --- |
| execute | **boolean** Required field. Permission to execute. |
| read | **boolean** Required field. Permission to read. |
| edit | **boolean** Required field. Permission to edit. |
| admin | **boolean** Required field. Permission to administer. |

# EditorTableNode

| Field | Description |
| --- | --- |
| version | **enum** Required field. Editor version. Аvailable values: `1` |
| entryId | **string** Required field. Unique identifier of the entry. |
| key | Any of **null** \| **string** \| **null** Key identifier of the entry. |
| createdAt | **string** Required field. Creation timestamp. |
| createdBy | **string** Required field. Creator of the entry. |
| updatedAt | **string** Required field. Last update timestamp. |
| updatedBy | **string** Required field. Last updater of the entry. |
| revId | **string** Required field. Version ID for the Editor chart. |
| savedId | **string** Required field. Saved version ID. |
| publishedId | **string \| null** Required field. Published version ID. |
| tenantId | **string** Required field. Tenant ID. |
| hidden | **boolean** Required field. Indicates if the entry is hidden. |
| public | **boolean** Required field. Indicates if the entry is public. |
| workbookId | Any of **null** \| **string** \| **null** |
| scope | **enum** Required field. Type of the entry. For charts takes value: `widget` |
| meta | **object \| null** Required field. Metadata associated with the entry. |
| links | **object \| null** Link information. |
| annotation | **object \| null** Annotation information. |
| type | **enum** Required field. For Table Editor charts takes value: `table_node` |
| data | **[Data](https://yandex.cloud/ru/docs/datalens/openapi-ref/getEditorChart#Data)** Required field. Chart data. |

# Data

| Field | Description |
| --- | --- |
| meta | **string** Required field. Configuration from the Meta tab. |
| params | **string** Required field. Configuration from the Params tab. |
| sources | **string** Required field. Configuration from the Sources tab. |
| controls | **string** Required field. Configuration from the Controls tab. |
| prepare | **string** Required field. Configuration from the Prepare tab. |
| config | **string** Required field. Configuration from the Config tab. |

# EditorGravityChartsNode

| Field | Description |
| --- | --- |
| version | **enum** Required field. Editor version. Аvailable values: `1` |
| entryId | **string** Required field. Unique identifier of the entry. |
| key | Any of **null** \| **string** \| **null** Key identifier of the entry. |
| createdAt | **string** Required field. Creation timestamp. |
| createdBy | **string** Required field. Creator of the entry. |
| updatedAt | **string** Required field. Last update timestamp. |
| updatedBy | **string** Required field. Last updater of the entry. |
| revId | **string** Required field. Version ID for the Editor chart. |
| savedId | **string** Required field. Saved version ID. |
| publishedId | **string \| null** Required field. Published version ID. |
| tenantId | **string** Required field. Tenant ID. |
| hidden | **boolean** Required field. Indicates if the entry is hidden. |
| public | **boolean** Required field. Indicates if the entry is public. |
| workbookId | Any of **null** \| **string** \| **null** ID of the workbook the Editor chart belongs to. |
| scope | **enum** Required field. Type of the entry. For charts takes value: `widget` |
| meta | **object \| null** Required field. Metadata associated with the entry. |
| links | **object \| null** Link information. |
| annotation | **object \| null** Annotation information. |
| type | **enum** Required field. For D3 Editor charts takes value: `d3_node` |
| data | **[Data](https://yandex.cloud/ru/docs/datalens/openapi-ref/getEditorChart#Data)** Required field. Chart data. |

# EditorMarkdownNode

| Field | Description |
| --- | --- |
| version | **enum** Required field. Editor version. Аvailable values: `1` |
| entryId | **string** Required field. Unique identifier of the entry. |
| key | Any of **null** \| **string** \| **null** Key identifier of the entry. |
| createdAt | **string** Required field. Creation timestamp. |
| createdBy | **string** Required field. Creator of the entry. |
| updatedAt | **string** Required field. Last update timestamp. |
| updatedBy | **string** Required field. Last updater of the entry. |
| revId | **string** Required field. Version ID for the Editor chart. |
| savedId | **string** Required field. Saved version ID. |
| publishedId | **string \| null** Required field. Published version ID. |
| tenantId | **string** Required field. Tenant ID. |
| hidden | **boolean** Required field. Indicates if the entry is hidden. |
| public | **boolean** Required field. Indicates if the entry is public. |
| workbookId | Any of **null** \| **string** \| **null** ID of the workbook the Editor chart belongs to. |
| scope | **enum** Required field. Type of the entry. For charts takes value: `widget` |
| meta | **object \| null** Required field. Metadata associated with the entry. |
| links | **object \| null** Link information. |
| annotation | **object \| null** Annotation information. |
| type | **enum** Required field. For Markdown Editor charts takes value: `markdown_node` |
| data | **[Data](https://yandex.cloud/ru/docs/datalens/openapi-ref/getEditorChart#Data-1)** Required field. Chart data. |

# Data

| Field | Description |
| --- | --- |
| meta | **string** Required field. Configuration from the Meta tab. |
| params | **string** Required field. Configuration from the Params tab. |
| sources | **string** Required field. Configuration from the Sources tab. |
| controls | **string** Required field. Configuration from the Controls tab. |
| prepare | **string** Required field. Configuration from the Prepare tab. |

# EditorAdvancedChartNode

| Field | Description |
| --- | --- |
| version | **enum** Required field. Editor version. Аvailable values: `1` |
| entryId | **string** Required field. Unique identifier of the entry. |
| key | Any of **null** \| **string** \| **null** Key identifier of the entry. |
| createdAt | **string** Required field. Creation timestamp. |
| createdBy | **string** Required field. Creator of the entry. |
| updatedAt | **string** Required field. Last update timestamp. |
| updatedBy | **string** Required field. Last updater of the entry. |
| revId | **string** Required field. Version ID for the Editor chart. |
| savedId | **string** Required field. Saved version ID. |
| publishedId | **string \| null** Required field. Published version ID. |
| tenantId | **string** Required field. Tenant ID. |
| hidden | **boolean** Required field. Indicates if the entry is hidden. |
| public | **boolean** Required field. Indicates if the entry is public. |
| workbookId | Any of **null** \| **string** \| **null** ID of the workbook the Editor chart belongs to. |
| scope | **enum** Required field. Type of the entry. For charts takes value: `widget` |
| meta | **object \| null** Required field. Metadata associated with the entry. |
| links | **object \| null** Link information. |
| annotation | **object \| null** Annotation information. |
| type | **enum** Required field. For Advanced Editor charts takes value: `advanced-chart_node` |
| data | **[Data](https://yandex.cloud/ru/docs/datalens/openapi-ref/getEditorChart#Data-1)** Required field. Chart data. |

# EditorSelectorNode

| Field | Description |
| --- | --- |
| version | **enum** Required field. Editor version. Аvailable values: `1` |
| entryId | **string** Required field. Unique identifier of the entry. |
| key | Any of **null** \| **string** \| **null** Key identifier of the entry. |
| createdAt | **string** Required field. Creation timestamp. |
| createdBy | **string** Required field. Creator of the entry. |
| updatedAt | **string** Required field. Last update timestamp. |
| updatedBy | **string** Required field. Last updater of the entry. |
| revId | **string** Required field. Version ID for the Editor chart. |
| savedId | **string** Required field. Saved version ID. |
| publishedId | **string \| null** Required field. Published version ID. |
| tenantId | **string** Required field. Tenant ID. |
| hidden | **boolean** Required field. Indicates if the entry is hidden. |
| public | **boolean** Required field. Indicates if the entry is public. |
| workbookId | Any of **null** \| **string** \| **null** ID of the workbook the Editor chart belongs to. |
| scope | **enum** Required field. Type of the entry. For charts takes value: `widget` |
| meta | **object \| null** Required field. Metadata associated with the entry. |
| links | **object \| null** Link information. |
| annotation | **object \| null** Annotation information. |
| type | **enum** Required field. For Editor JS selectors takes value: `control_node` |
| data | **[Data](https://yandex.cloud/ru/docs/datalens/openapi-ref/getEditorChart#Data-2)** Required field. Chart data. |

# Data

| Field | Description |
| --- | --- |
| meta | **string** Required field. Configuration from the Meta tab. |
| params | **string** Required field. Configuration from the Params tab. |
| sources | **string** Required field. Configuration from the Sources tab. |
| controls | **string** Required field. Configuration from the Controls tab. |
