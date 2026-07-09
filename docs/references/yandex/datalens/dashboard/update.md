---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDashboard
title: "Yandex DataLens | DataLens API: 🚧 [Experimental] Update dashboard"
author: "Yandex Cloud"
extracted: "2026-07-09T13:29:00Z"
---

# HTTP request

```
POST https://api.datalens.tech/rpc/updateDashboard
```

# Body parameters

**Request schema: application/json**

```
{
  "entry": {
    "entryId": "string",
    "data": {
      "counter": "integer",
      "salt": "string",
      "schemeVersion": "number",
      "tabs": [
        {
          "id": "string",
          "title": "string",
          "items": [
            {
              "<allOf>": [
                {
                  "id": "string",
                  "namespace": "string",
                  "type": "string"
                },
                "unknown"
              ]
            }
          ],
          "layout": [
            {
              "i": "string",
              "h": "number",
              "w": "number",
              "x": "number",
              "y": "number",
              "parent": "string"
            }
          ],
          "connections": [
            {
              "from": "string",
              "to": "string",
              "kind": "string"
            }
          ],
          "aliases": {
            "default": [
              "array"
            ]
          }
        }
      ],
      "settings": {
        "autoupdateInterval": "unknown",
        "maxConcurrentRequests": "unknown",
        "loadPriority": "string",
        "silentLoading": "boolean",
        "dependentSelectors": "boolean",
        "globalParams": {
          "string": "unknown"
        },
        "hideTabs": "boolean",
        "hideDashTitle": "boolean",
        "expandTOC": "boolean",
        "assistantEnabled": "boolean"
      },
      "supportDescription": "string",
      "accessDescription": "string"
    },
    "meta": "object | null",
    "revId": "string",
    "annotation": {
      "description": "string"
    }
  },
  "mode": "string"
}
```

| Field | Description |
| --- | --- |
| entry | **[Entry](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDashboard#Entry)** Required field. |
| mode | **enum** Required field. `save`, `publish` |

# Entry

| Field | Description |
| --- | --- |
| entryId | **string** Required field. |
| data | **[Data](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDashboard#Data)** Required field. |
| meta | **object \| null** Required field. |
| revId | **string** |
| annotation | **[Annotation](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDashboard#Annotation)** Required field. |

# Data

| Field | Description |
| --- | --- |
| counter | **integer** Required field. |
| salt | **string** Required field. |
| schemeVersion | **enum** Required field. `8` |
| tabs[] | **[TabsItem](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDashboard#TabsItem)** Required field. |
| settings | **[Settings](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDashboard#Settings)** Required field. |
| supportDescription | **string** |
| accessDescription | **string** |

# TabsItem

| Field | Description |
| --- | --- |
| id | **string** Required field. |
| title | **string** Required field. |
| items[] | **unknown** Required field. |
| layout[] | **[LayoutItem](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDashboard#LayoutItem)** Required field. |
| connections[] | **[ConnectionsItem](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDashboard#ConnectionsItem)** Required field. |
| aliases | **[Aliases](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDashboard#Aliases)** Required field. |

# LayoutItem

| Field | Description |
| --- | --- |
| i | **string** Required field. |
| h | **number** Required field. |
| w | **number** Required field. |
| x | **number** Required field. |
| y | **number** Required field. |
| parent | **string** |

# ConnectionsItem

| Field | Description |
| --- | --- |
| from | **string** Required field. |
| to | **string** Required field. |
| kind | **enum** Required field. `ignore` |

# Aliases

| Field | Description |
| --- | --- |
| default[] | **string** |

# Settings

| Field | Description |
| --- | --- |
| autoupdateInterval | Any of **number** \| **null** \| **null** |
| maxConcurrentRequests | Any of **number** \| **null** \| **null** |
| loadPriority | **enum** `charts`, `selectors` |
| silentLoading | **boolean** Required field. |
| dependentSelectors | **boolean** Required field. |
| globalParams | **object** (map<**string**, **unknown**>) |
| hideTabs | **boolean** Required field. |
| hideDashTitle | **boolean** |
| expandTOC | **boolean** Required field. |
| assistantEnabled | **boolean** |

# Annotation

| Field | Description |
| --- | --- |
| description | **string** Required field. |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{
  "entry": {
    "annotation": "object | null",
    "createdAt": "string",
    "createdBy": "string",
    "data": {
      "counter": "integer",
      "salt": "string",
      "schemeVersion": "number",
      "tabs": [
        {
          "id": "string",
          "title": "string",
          "items": [
            {
              "<allOf>": [
                {
                  "id": "string",
                  "namespace": "string",
                  "type": "string"
                },
                "unknown"
              ]
            }
          ],
          "layout": [
            {
              "i": "string",
              "h": "number",
              "w": "number",
              "x": "number",
              "y": "number",
              "parent": "string"
            }
          ],
          "connections": [
            {
              "from": "string",
              "to": "string",
              "kind": "string"
            }
          ],
          "aliases": {
            "default": [
              "array"
            ]
          }
        }
      ],
      "settings": {
        "autoupdateInterval": "unknown",
        "maxConcurrentRequests": "unknown",
        "loadPriority": "string",
        "silentLoading": "boolean",
        "dependentSelectors": "boolean",
        "globalParams": {
          "string": "unknown"
        },
        "hideTabs": "boolean",
        "hideDashTitle": "boolean",
        "expandTOC": "boolean",
        "assistantEnabled": "boolean"
      },
      "supportDescription": "string",
      "accessDescription": "string"
    },
    "entryId": "string",
    "hidden": "boolean",
    "key": "unknown",
    "links": "object | null",
    "meta": "object | null",
    "public": "boolean",
    "publishedId": "string | null",
    "revId": "string",
    "savedId": "string",
    "scope": "string",
    "tenantId": "string",
    "type": "string",
    "updatedAt": "string",
    "updatedBy": "string",
    "version": "number",
    "workbookId": "unknown"
  }
}
```

| Field | Description |
| --- | --- |
| entry | **[Entry](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDashboard#Entry-1)** Required field. |

# Entry

| Field | Description |
| --- | --- |
| annotation | **object \| null** |
| createdAt | **string** Required field. |
| createdBy | **string** Required field. |
| data | **[Data](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDashboard#Data-1)** Required field. |
| entryId | **string** Required field. |
| hidden | **boolean** Required field. |
| key | Any of **null** \| **string** \| **null** |
| links | **object \| null** |
| meta | **object \| null** Required field. |
| public | **boolean** Required field. |
| publishedId | **string \| null** Required field. |
| revId | **string** Required field. |
| savedId | **string** Required field. |
| scope | **enum** Required field. `dash` |
| tenantId | **string** Required field. |
| type | **enum** Required field. `` |
| updatedAt | **string** Required field. |
| updatedBy | **string** Required field. |
| version | **enum** Required field. `1` |
| workbookId | Any of **null** \| **string** \| **null** |

# Data

| Field | Description |
| --- | --- |
| counter | **integer** Required field. |
| salt | **string** Required field. |
| schemeVersion | **enum** Required field. `8` |
| tabs[] | **[TabsItem](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDashboard#TabsItem-1)** Required field. |
| settings | **[Settings](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDashboard#Settings-1)** Required field. |
| supportDescription | **string** |
| accessDescription | **string** |

# TabsItem

| Field | Description |
| --- | --- |
| id | **string** Required field. |
| title | **string** Required field. |
| items[] | **unknown** Required field. |
| layout[] | **[LayoutItem](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDashboard#LayoutItem-1)** Required field. |
| connections[] | **[ConnectionsItem](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDashboard#ConnectionsItem-1)** Required field. |
| aliases | **[Aliases](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDashboard#Aliases-1)** Required field. |

# LayoutItem

| Field | Description |
| --- | --- |
| i | **string** Required field. |
| h | **number** Required field. |
| w | **number** Required field. |
| x | **number** Required field. |
| y | **number** Required field. |
| parent | **string** |

# ConnectionsItem

| Field | Description |
| --- | --- |
| from | **string** Required field. |
| to | **string** Required field. |
| kind | **enum** Required field. `ignore` |

# Aliases

| Field | Description |
| --- | --- |
| default[] | **string** |

# Settings

| Field | Description |
| --- | --- |
| autoupdateInterval | Any of **number** \| **null** \| **null** |
| maxConcurrentRequests | Any of **number** \| **null** \| **null** |
| loadPriority | **enum** `charts`, `selectors` |
| silentLoading | **boolean** Required field. |
| dependentSelectors | **boolean** Required field. |
| globalParams | **object** (map<**string**, **unknown**>) |
| hideTabs | **boolean** Required field. |
| hideDashTitle | **boolean** |
| expandTOC | **boolean** Required field. |
| assistantEnabled | **boolean** |
