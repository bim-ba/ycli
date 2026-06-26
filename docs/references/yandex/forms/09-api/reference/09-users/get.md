---
source: https://yandex.ru/support/forms/en/api-ref/users/events_v1_views_users_get_user_view
title: "Get current user information - Users |"
word_count: 88
token_estimate: 651
extracted: "2026-05-22T18:14:30Z"
mode: quality
---

Returns information about the user making the request.

# Request

GET

```
https://api.forms.yandex.net/v1/users/me
```

# Responses

# 200 OK

OK

## Body

application/json

```
{
  "id": 0,
  "uid": "example",
  "cloud_uid": "example",
  "login": "example",
  "display": "example",
  "email": "example"
}
```

| Name | Description |
|------|-------------|
| `id` | **Type:** integer — User ID |
| `cloud_uid` | **Type:** string — User cloud UID. Example: `example` |
| `display` | **Type:** string — User display name. Example: `example` |
| `email` | **Type:** string — User email. Example: `example` |
| `login` | **Type:** string — User login. Example: `example` |
| `uid` | **Type:** string — User Passport UID. Example: `example` |

Previous

Next