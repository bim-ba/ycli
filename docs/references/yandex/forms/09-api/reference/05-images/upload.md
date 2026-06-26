---
source: https://yandex.ru/support/forms/en/api-ref/images/events_v1_views_images_create_image_view
title: "Upload image - Images |"
word_count: 169
token_estimate: 1223
extracted: "2026-05-22T18:11:37Z"
mode: quality
---

Uploads an image to add to the form.

Parameters:

-   **survey\_id**: form ID
-   **image**: field containing the image data

# Request

POST

```
https://api.forms.yandex.net/v1/surveys/{survey_id}/images
```

## Path parameters

| Name | Description |
|------|-------------|
| `survey_id` | **Type:** string. Pattern: `^[a-fA-F\d]{24}$`. Example: `` |

## Body

multipart/form-data

```
{
  "image": "example"
}
```

| Name | Description |
|------|-------------|
| `image` | **Type:** string&lt;binary&gt;. Example: `example` |

# Responses

# 201 Created

Created

## Body

application/json

```
{
  "id": 0,
  "links": {},
  "name": "example",
  "check_status": "check"
}
```

| Name | Description |
|------|-------------|
| `links` | **Type:** Links (object). List of links to different image sizes. Example: `{}`. Each value (`[additional]`): **Type:** string&lt;uri&gt;, min length `1`, max length `2083`, example `https://example.com` |
| `check_status` | **Type:** [FileCheckStatusType](https://yandex.ru/support/forms/en/api-ref/images/events_v1_views_images_create_image_view#entity-FileCheckStatusType) (enumeration; enum: `check`, `ready`, `infected`, `error`, `deleted`). Image upload status. Example: `check` |
| `id` | **Type:** integer. Image ID |
| `name` | **Type:** string. Original image file name. Example: `example` |

## FileCheckStatusType

An enumeration.

**Type**: string

*Enum:* `check`, `ready`, `infected`, `error`, `deleted`

Previous

Next