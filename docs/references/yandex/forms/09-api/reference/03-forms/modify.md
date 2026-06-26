---
source: https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view
title: "Modify form - Forms |"
word_count: 1386
token_estimate: 11890
extracted: "2026-05-22T18:09:55Z"
mode: quality
---

# Body

application/json

```
{
  "id": "example",
  "name": "example",
  "dir_id": "example",
  "collab_id": "example",
  "created": "2025-01-01T00:00:00Z",
  "language": "example",
  "is_published": true,
  "is_public": true,
  "is_banned": true,
  "is_favourite": true,
  "allow_multiple_answers": true,
  "show_last_answer": true,
  "metric": 0,
  "texts": {
    "submit": "example",
    "back": "example",
    "next": "example",
    "title": "example",
    "subtitle": "example",
    "redirect": "example"
  },
  "styles": {
    "id": 0,
    "name": "example",
    "custom": {},
    "images": {
      "page": null,
      "form": null
    }
  },
  "follow": "5m",
  "file_storage": "example",
  "validator_url": "example",
  "captcha": "std",
  "auto_publication": {
    "enabled": true,
    "date_open": "2025-01-01T00:00:00Z",
    "date_close": "2025-01-01T00:00:00Z"
  },
  "max_count": 0,
  "iframe": true,
  "footer": true,
  "teaser": true,
  "stats": true,
  "share": true,
  "fill_again": true,
  "quiz": {
    "show_results": true,
    "show_correct": true,
    "calc_method": "range",
    "pass_scores": 0.5,
    "items": [
      {
        "title": "example",
        "description": "example",
        "image": null
      }
    ]
  },
  "need_auth": true,
  "followers": [
    {
      "id": 0,
      "uid": "example",
      "cloud_uid": "example",
      "login": "example",
      "display": "example",
      "email": "example",
      "is_superuser": true,
      "is_staff": true,
      "avatar": "example",
      "type": "user"
    }
  ]
}
```

| Name | Description |
|------|-------------|
| `id` | **Type:** string. Form identifier. Pattern: `^[a-fA-F\d]{24}$`. Example: `example` |
| `allow_multiple_answers` | **Type:** boolean. Allow the user to fill out the form multiple times |
| `auto_publication` | **Type:** [SurveyAutoPublicationOut](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view#entity-SurveyAutoPublicationOut). Form auto-publication settings. Example: `{"enabled": true, "date_open": "2025-01-01T00:00:00Z", "date_close": "2025-01-01T00:00:00Z"}` |
| `captcha` | **Type:** [CaptchaType](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view#entity-CaptchaType) (enumeration; enum: `std`, `ocr`, `nbg`). Require captcha before submitting the form. Example: `std` |
| `collab_id` | **Type:** string. Meta-organization ID. Example: `example` |
| `created` | **Type:** string&lt;date-time&gt;. Form creation date. Example: `2025-01-01T00:00:00Z` |
| `dir_id` | **Type:** string. Organization ID in 360. Example: `example` |
| `file_storage` | **Type:** string. Link for the user file storage. Example: `example` |
| `fill_again` | **Type:** boolean. Fill out the form again, default True |
| `follow` | **Type:** [FollowType](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view#entity-FollowType) (enumeration; enum: `5m`, `1h`, `1d`). Setting for integration error notification emails. Example: `5m` |
| `followers` | **Type:** array, any of 2 types — [FollowerUserOut](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view#entity-FollowerUserOut) or [FollowerMailListOut](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view#entity-FollowerMailListOut). List of users who follow integration errors. Example: `[{"id": 0, "uid": "example", "cloud_uid": "example", "login": "example", "display": "example", "email": "example", "is_superuser": true, "is_staff": true, "avatar": "example", "type": "user"}]` |
| `footer` | **Type:** boolean. Show footer |
| `iframe` | **Type:** boolean. Allow publication only in iframe |
| `is_banned` | **Type:** boolean. Form is blocked |
| `is_favourite` | **Type:** boolean. Form is in favorites |
| `is_public` | **Type:** boolean. Form is public |
| `is_published` | **Type:** boolean. Form is published |
| `language` | **Type:** string. Language at form creation. Example: `example` |
| `max_count` | **Type:** integer. Maximum number of responses for the form |
| `metric` | **Type:** integer. Metrica counter |
| `name` | **Type:** string. Form name. Example: `example` |
| `need_auth` | **Type:** boolean. Setting requires authorization to fill out the form |
| `quiz` | **Type:** [SurveyQuizOut](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view#entity-SurveyQuizOut). Settings for tests and quizzes. Example: `{"show_results": true, "show_correct": true, "calc_method": "range", "pass_scores": 0.5, "items": [{"title": "example", "description": "example", "image": null}]}` |
| `share` | **Type:** boolean. Share the form, default True |
| `show_last_answer` | **Type:** boolean. Pre-fill the form with the user's previous answer |
| `stats` | **Type:** boolean. Show statistics on the response submission page |
| `styles` | **Type:** [SurveyStylesOut](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view#entity-SurveyStylesOut). Styles for form design. Example: `{"id": 0, "name": "example", "custom": {}, "images": {"page": null, "form": null}}` |
| `teaser` | **Type:** boolean. Show teaser |
| `texts` | **Type:** [SurveyTextsOut](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view#entity-SurveyTextsOut). Button texts and message after form submission. Example: `{"submit": "example", "back": "example", "next": "example", "title": "example", "subtitle": "example", "redirect": "example"}` |
| `validator_url` | **Type:** string. URL for external validation of form questions. Example: `example` |

# SurveyTextsOut

| Name | Description |
|------|-------------|
| `back` | **Type:** string. Text of the Back button. Example: `example` |
| `next` | **Type:** string. Text of the Next button. Example: `example` |
| `submit` | **Type:** string. Text of the Submit button. Example: `example` |
| `subtitle` | **Type:** string. Text on the page after submitting the response. Example: `example` |
| `title` | **Type:** string. Heading on the page after submitting the response. Example: `example` |
| `redirect` | **Type:** string. Text of the website redirect button. Example: `example` |

**Example**

```
{
  "submit": "example",
  "back": "example",
  "next": "example",
  "title": "example",
  "subtitle": "example",
  "redirect": "example"
}
```

# FileCheckStatusType

An enumeration.

**Type**: string

*Enum:* `check`, `ready`, `infected`, `error`, `deleted`

# ImageOut

| Name | Description |
|------|-------------|
| `links` | **Type:** Links (object). List of links to different image sizes. Example: `{}`. Each value (`[additional]`): **Type:** string&lt;uri&gt;, min length `1`, max length `2083`, example `https://example.com` |
| `check_status` | **Type:** [FileCheckStatusType](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view#entity-FileCheckStatusType) (enumeration; enum: `check`, `ready`, `infected`, `error`, `deleted`). Image upload status. Example: `check` |
| `id` | **Type:** integer. Image ID |
| `name` | **Type:** string. Original image file name. Example: `example` |

**Example**

```
{
  "id": 0,
  "links": {},
  "name": "example",
  "check_status": "check"
}
```

# SurveyStylesImagesOut

| Name | Description |
|------|-------------|
| `form` | **Type:** [ImageOut](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view#entity-ImageOut). Background image for the form backdrop. Example: `{"id": 0, "links": {}, "name": "example", "check_status": "check"}` |
| `page` | **Type:** [ImageOut](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view#entity-ImageOut). Background image behind the text. Example: `{"id": 0, "links": {}, "name": "example", "check_status": "check"}` |

**Example**

```
{
  "page": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  },
  "form": null
}
```

# SurveyStylesOut

| Name | Description |
|------|-------------|
| `custom` | **Type:** object. Custom style settings for the form. Example: `{}` |
| `id` | **Type:** integer. Form style ID |
| `images` | **Type:** [SurveyStylesImagesOut](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view#entity-SurveyStylesImagesOut). Images for form styling. Example: `{"page": {"id": 0, "links": {}, "name": "example", "check_status": "check"}, "form": null}` |
| `name` | **Type:** string. Form style name. Example: `example` |

**Example**

```
{
  "id": 0,
  "name": "example",
  "custom": {},
  "images": {
    "page": {
      "id": 0,
      "links": {},
      "name": "example",
      "check_status": null
    },
    "form": null
  }
}
```

# SurveyQuizItemOut

| Name | Description |
|------|-------------|
| `title` | **Type:** string. Heading on the page after completing the test. Example: `example` |
| `description` | **Type:** string. Description on the page after completing the test. Example: `example` |
| `image` | **Type:** [ImageOut](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view#entity-ImageOut). Image for the page after completing the test. Example: `{"id": 0, "links": {}, "name": "example", "check_status": "check"}` |

**Example**

```
{
  "title": "example",
  "description": "example",
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
}
```

# SurveyQuizOut

| Name | Description |
|------|-------------|
| `calc_method` | **Type:** [QuizCalcMethodType](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view#entity-QuizCalcMethodType) (enumeration; enum: `range`, `scores`). Score calculation method. Example: `range` |
| `items` | **Type:** [SurveyQuizItemOut](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_modify_survey_public_view#entity-SurveyQuizItemOut)[]. List of score ranges for test results. Example: `[{"title": "example", "description": "example", "image": {"id": 0, "links": {}, "name": "example", "check_status": "check"}}]` |
| `show_correct` | **Type:** boolean. Whether to show correct answers |
| `show_results` | **Type:** boolean. Whether to show test results |
| `pass_scores` | **Type:** number. Score threshold for passing the test |

**Example**

```
{
  "show_results": true,
  "show_correct": true,
  "calc_method": "range",
  "pass_scores": 0.5,
  "items": [
    {
      "title": "example",
      "description": "example",
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": null
      }
    }
  ]
}
```

# FollowerUserOut

| Name | Description |
|------|-------------|
| `id` | **Type:** integer. User ID |
| `avatar` | **Type:** string. User avatar. Example: `example` |
| `cloud_uid` | **Type:** string. User cloud uid. Example: `example` |
| `display` | **Type:** string. User display name. Example: `example` |
| `email` | **Type:** string. User email. Example: `example` |
| `is_staff` | **Type:** boolean. Technical support staff flag |
| `is_superuser` | **Type:** boolean. Superuser flag |
| `login` | **Type:** string. User login. Example: `example` |
| `type` | **Type:** string. Follower type. Default: `user`. Const: `user` |
| `uid` | **Type:** string. User passport uid. Example: `example` |

**Example**

```
{
  "id": 0,
  "uid": "example",
  "cloud_uid": "example",
  "login": "example",
  "display": "example",
  "email": "example",
  "is_superuser": true,
  "is_staff": true,
  "avatar": "example",
  "type": "user"
}
```

# FollowerMailListOut

| Name | Description |
|------|-------------|
| `id` | **Type:** string. Mailing list ID (address). Example: `example` |
| `email` | **Type:** string. Mailing list email address. Example: `example` |
| `type` | **Type:** string. Follower type. Default: `mail_list`. Const: `mail_list` |

**Example**

```
{
  "id": "example",
  "email": "example",
  "type": "mail_list"
}
```
