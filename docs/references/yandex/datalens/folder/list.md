---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/listDirectory
title: "Yandex DataLens | DataLens API: List directory"
author: "Yandex Cloud"
extracted: "2026-07-09T13:35:01Z"
---

Lists entries from the specified directory.

# HTTP request

```
POST https://api.datalens.tech/rpc/listDirectory
```

# Body parameters

**Request schema: application/json**

```
{
  "path": "string",
  "createdBy": "unknown",
  "orderBy": {
    "field": "string",
    "direction": "string"
  },
  "filters": {
    "name": "string"
  },
  "page": "number",
  "pageSize": "number",
  "includePermissionsInfo": "boolean"
}
```

| Field | Description |
| --- | --- |
| path | **string** Directory path to list entries from. |
| createdBy | Any of **string** \| **string** Filter entries by creator. |
| orderBy | **[OrderBy](https://yandex.cloud/ru/docs/datalens/openapi-ref/listDirectory#OrderBy)** Required field. Sorting configuration. |
| filters | **[Filters](https://yandex.cloud/ru/docs/datalens/openapi-ref/listDirectory#Filters)** Filtering configuration. |
| page | **number** Page number for pagination. |
| pageSize | **number** Number of entries per page. |
| includePermissionsInfo | **boolean** Include permission information in response. |

# OrderBy

Sorting configuration.

| Field | Description |
| --- | --- |
| field | **enum** Required field. Field to order by entries: `createdAt` — date of field creation;, `name` — name of the field. |
| direction | **enum** Required field. Sorting direction. `desc` — descending;, `asc` — ascending. |

# Filters

Filtering configuration.

| Field | Description |
| --- | --- |
| name | **string** Filter entries by name. |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{
  "nextPageToken": "boolean",
  "breadCrumbs": [
    {
      "title": "string",
      "path": "string",
      "entryId": "string",
      "isLocked": "boolean",
      "permissions": {
        "execute": "boolean",
        "read": "boolean",
        "edit": "boolean",
        "admin": "boolean"
      }
    }
  ],
  "entries": [
    {
      "entryId": "string",
      "key": "string",
      "scope": "string",
      "type": "string",
      "meta": "object | null",
      "createdAt": "string",
      "updatedAt": "string",
      "createdBy": "string",
      "updatedBy": "string",
      "savedId": "string",
      "publishedId": "string | null",
      "hidden": "boolean",
      "workbookId": "string",
      "workbookTitle": "string | null",
      "collectionId": "string | null",
      "collectionTitle": "string | null",
      "isFavorite": "boolean",
      "isLocked": "boolean",
      "permissions": {
        "execute": "boolean",
        "read": "boolean",
        "edit": "boolean",
        "admin": "boolean"
      },
      "name": "string"
    }
  ]
}
```

| Field | Description |
| --- | --- |
| nextPageToken | **boolean** Required field. Indicates if there are more pages. |
| breadCrumbs[] | **[BreadCrumbsItem](https://yandex.cloud/ru/docs/datalens/openapi-ref/listDirectory#BreadCrumbsItem)** Required field. Navigation breadcrumbs for the current path. |
| entries[] | **[EntriesItem](https://yandex.cloud/ru/docs/datalens/openapi-ref/listDirectory#EntriesItem)** Required field. List of directory entries. |

# BreadCrumbsItem

Navigation breadcrumbs for the current path.

| Field | Description |
| --- | --- |
| title | **string** Required field. Title of the breadcrumb item. |
| path | **string** Required field. Path of the breadcrumb item. |
| entryId | **string** Required field. Entry ID of the breadcrumb item. |
| isLocked | **boolean** Required field. Indicates if the item is locked. |
| permissions | **[Permissions](https://yandex.cloud/ru/docs/datalens/openapi-ref/listDirectory#Permissions)** Required field. Permissions for the breadcrumb item. |

# Permissions

| Field | Description |
| --- | --- |
| execute | **boolean** Required field. Indicates if there are permissions to execute. |
| read | **boolean** Required field. Indicates if there are permissions to read. |
| edit | **boolean** Required field. Indicates if there are permissions to edit. |
| admin | **boolean** Required field. Indicates if there are permissions for admin. |

# EntriesItem

| Field | Description |
| --- | --- |
| entryId | **string** Required field. Unique identifier of the entry. |
| key | **string** Required field. Key identifier of the entry. |
| scope | **string** Required field. Type of the entry (e.g., dash, dataset, connection). |
| type | **string** Required field. Specified type of the entry from scope (e.g. type of the connection or visualization type for charts). |
| meta | **object \| null** Required field. Metadata associated with the entry. |
| createdAt | **string** Required field. Creation timestamp. |
| updatedAt | **string** Required field. Last update timestamp. |
| createdBy | **string** Required field. Creator of the entry. |
| updatedBy | **string** Required field. Last updater of the entry. |
| savedId | **string** Required field. Saved version ID. |
| publishedId | **string \| null** Required field. Published version ID. |
| hidden | **boolean** Required field. Indicates if the entry is hidden. |
| workbookId | **string** Required field. ID of the workbook the entry belongs to. |
| workbookTitle | **string \| null** Workbook name. |
| collectionId | **string \| null** Required field. ID of the collection the entry belongs to. |
| collectionTitle | **string \| null** Collection name |
| isFavorite | **boolean** Required field. Indicates if the entry is marked as favorite. |
| isLocked | **boolean** Required field. Indicates if the entry is locked. |
| permissions | **[Permissions](https://yandex.cloud/ru/docs/datalens/openapi-ref/listDirectory#Permissions)** Required field. Permissions for the entry. |
| name | **string** Required field. Name of the entry. |
