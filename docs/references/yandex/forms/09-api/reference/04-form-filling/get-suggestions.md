---
source: https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view
title: "Get suggestions for filling out the form - Form Filling |"
word_count: 2813
token_estimate: 19782
extracted: "2026-05-22T18:11:14Z"
mode: quality
---

Returns suggestions (prompts) for filling out the form.

Parameters:

-   **survey**: form ID, its slug, or a combination of the form ID and a verification key
-   **question**: question slug (string identifier)
-   **text**: text to search for
-   **id**: comma-separated list of suggestion object identifiers; allows retrieving suggestion objects by their IDs
-   **parent\_id**: comma-separated list of suggestion object identifiers for organizing Master-Detail relationships

# Request

GET

```
https://api.forms.yandex.net/v1/surveys/{survey}/suggest
```

## Path parameters

| Name | Description |
|------|-------------|
| *survey* | **Type**: string *Example:* `` |

## Query parameters

| Name | Description |
|------|-------------|
| *id* | **Type**: string *Default:* `` *Example:* `` |
| *parent_id* | **Type**: string *Default:* `` *Example:* `` |
| *question* | **Type**: string *Default:* `` *Example:* `` |
| *text* | **Type**: string *Default:* `` *Example:* `` |

# Responses

# 200 OK

OK

## Body

application/json

```
[
  {
    "layer": "country",
    "id": "example",
    "text": "example",
    "orig_id": "example"
  }
]
```
**Type**: array

**Type**: array

**One of 26 types**

-   **SuggestCountryOut**

    **Type**: [SuggestCountryOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestCountryOut)

    **Example**

    ```
    {
      "layer": "country",
      "id": "example",
      "text": "example",
      "orig_id": "example"
    }
    ```

-   **SuggestCityOut**

    **Type**: [SuggestCityOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestCityOut)

    **Example**

    ```
    {
      "layer": "city",
      "id": "example",
      "text": "example",
      "country_id": "example",
      "population": 0,
      "orig_id": "example"
    }
    ```

-   **SuggestUniversityOut**

    **Type**: [SuggestUniversityOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestUniversityOut)

    **Example**

    ```
    {
      "layer": "university",
      "id": "example",
      "text": "example",
      "city": "example",
      "region": "example"
    }
    ```

-   **SuggestAddressOut**

    **Type**: [SuggestAddressOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestAddressOut)

    **Example**

    ```
    {
      "layer": "address",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestGenderOut**

    **Type**: [SuggestGenderOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestGenderOut)

    **Example**

    ```
    {
      "layer": "gender",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestUserEmailOut**

    **Type**: [SuggestUserEmailOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestUserEmailOut)

    **Example**

    ```
    {
      "layer": "user_email_list",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestWebMasterOut**

    **Type**: [SuggestWebMasterOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestWebMasterOut)

    **Example**

    ```
    {
      "layer": "web_master_site",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestAbcServiceOut**

    **Type**: [SuggestAbcServiceOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestAbcServiceOut)

    **Example**

    ```
    {
      "layer": "abc_service",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestMusicGenreOut**

    **Type**: [SuggestMusicGenreOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestMusicGenreOut)

    **Example**

    ```
    {
      "layer": "music_genre",
      "id": "example",
      "text": "example",
      "tracks_count": 0
    }
    ```

-   **SuggestStaffOrganizationOut**

    **Type**: [SuggestStaffOrganizationOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestStaffOrganizationOut)

    **Example**

    ```
    {
      "layer": "staff_organization",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestStaffOfficeOut**

    **Type**: [SuggestStaffOfficeOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestStaffOfficeOut)

    **Example**

    ```
    {
      "layer": "staff_office",
      "id": "example",
      "text": "example",
      "address": "example"
    }
    ```

-   **SuggestStaffGroupOut**

    **Type**: [SuggestStaffGroupOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestStaffGroupOut)

    **Example**

    ```
    {
      "layer": "staff_group",
      "id": "example",
      "text": "example",
      "url": "example",
      "type": "example",
      "role_scope": "example"
    }
    ```

-   **SuggestStaffPersonOut**

    **Type**: [SuggestStaffPersonOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestStaffPersonOut)

    **Example**

    ```
    {
      "layer": "staff_login",
      "id": "example",
      "text": "example",
      "full_name": "example",
      "yandex_uid": "example",
      "uid": "example",
      "email": "example",
      "group_id": "example",
      "avatar": "example",
      "department": "example"
    }
    ```

-   **SuggestStaffRoomOut**

    **Type**: [SuggestStaffRoomOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestStaffRoomOut)

    **Example**

    ```
    {
      "layer": "staff_room",
      "id": "example",
      "text": "example",
      "office_id": "example",
      "floor_number": "example",
      "floor_id": "example"
    }
    ```

-   **SuggestWikiTableOut**

    **Type**: [SuggestWikiTableOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestWikiTableOut)

    **Example**

    ```
    {
      "layer": "wiki_table_source",
      "id": "example",
      "text": "example",
      "orig_id": "example",
      "row_id": "example",
      "parent_id": "example",
      "display_text": "example"
    }
    ```

-   **SuggestYtTableOut**

    **Type**: [SuggestYtTableOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestYtTableOut)

    **Example**

    ```
    {
      "layer": "yt_table_source",
      "id": "example",
      "text": "example",
      "orig_id": "example",
      "row_id": "example",
      "parent_id": "example",
      "display_text": "example"
    }
    ```

-   **SuggestDirUserOut**

    **Type**: [SuggestDirUserOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestDirUserOut)

    **Example**

    ```
    {
      "layer": "dir_user",
      "id": "example",
      "text": "example",
      "login": "example",
      "avatar": "example",
      "yandex_uid": "example",
      "uid": "example",
      "cloud_uid": "example",
      "email": "example"
    }
    ```

-   **SuggestDirGroupOut**

    **Type**: [SuggestDirGroupOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestDirGroupOut)

    **Example**

    ```
    {
      "layer": "dir_group",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestDirDepartmentOut**

    **Type**: [SuggestDirDepartmentOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestDirDepartmentOut)

    **Example**

    ```
    {
      "layer": "dir_department",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestTrackerQueueOut**

    **Type**: [SuggestTrackerQueueOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestTrackerQueueOut)

    **Example**

    ```
    {
      "layer": "tracker_queue",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestTrackerProjectOut**

    **Type**: [SuggestTrackerProjectOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestTrackerProjectOut)

    **Example**

    ```
    {
      "layer": "tracker_project",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestTrackerBoardOut**

    **Type**: [SuggestTrackerBoardOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestTrackerBoardOut)

    **Example**

    ```
    {
      "layer": "tracker_board",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestTrackerSprintOut**

    **Type**: [SuggestTrackerSprintOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestTrackerSprintOut)

    **Example**

    ```
    {
      "layer": "tracker_sprint",
      "id": "example",
      "text": "example",
      "board": "example"
    }
    ```

-   **SuggestTrackerComponentOut**

    **Type**: [SuggestTrackerComponentOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestTrackerComponentOut)

    **Example**

    ```
    {
      "layer": "tracker_component",
      "id": "example",
      "text": "example",
      "queue": "example"
    }
    ```

-   **SuggestTrackerIssueOut**

    **Type**: [SuggestTrackerIssueOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestTrackerIssueOut)

    **Example**

    ```
    {
      "layer": "tracker_issue",
      "id": "example",
      "text": "example",
      "queue": "example",
      "status": "example"
    }
    ```

-   **SuggestTrackerFieldOut**

    **Type**: [SuggestTrackerFieldOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestTrackerFieldOut)

    **Example**

    ```
    {
      "layer": "tracker_field",
      "id": "example",
      "slug": "example",
      "text": "example",
      "queue": "example"
    }
    ```
**One of 26 types**

-   **SuggestCountryOut**

    **Type**: [SuggestCountryOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestCountryOut)

    **Example**

    ```
    {
      "layer": "country",
      "id": "example",
      "text": "example",
      "orig_id": "example"
    }
    ```

-   **SuggestCityOut**

    **Type**: [SuggestCityOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestCityOut)

    **Example**

    ```
    {
      "layer": "city",
      "id": "example",
      "text": "example",
      "country_id": "example",
      "population": 0,
      "orig_id": "example"
    }
    ```

-   **SuggestUniversityOut**

    **Type**: [SuggestUniversityOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestUniversityOut)

    **Example**

    ```
    {
      "layer": "university",
      "id": "example",
      "text": "example",
      "city": "example",
      "region": "example"
    }
    ```

-   **SuggestAddressOut**

    **Type**: [SuggestAddressOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestAddressOut)

    **Example**

    ```
    {
      "layer": "address",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestGenderOut**

    **Type**: [SuggestGenderOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestGenderOut)

    **Example**

    ```
    {
      "layer": "gender",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestUserEmailOut**

    **Type**: [SuggestUserEmailOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestUserEmailOut)

    **Example**

    ```
    {
      "layer": "user_email_list",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestWebMasterOut**

    **Type**: [SuggestWebMasterOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestWebMasterOut)

    **Example**

    ```
    {
      "layer": "web_master_site",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestAbcServiceOut**

    **Type**: [SuggestAbcServiceOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestAbcServiceOut)

    **Example**

    ```
    {
      "layer": "abc_service",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestMusicGenreOut**

    **Type**: [SuggestMusicGenreOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestMusicGenreOut)

    **Example**

    ```
    {
      "layer": "music_genre",
      "id": "example",
      "text": "example",
      "tracks_count": 0
    }
    ```

-   **SuggestStaffOrganizationOut**

    **Type**: [SuggestStaffOrganizationOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestStaffOrganizationOut)

    **Example**

    ```
    {
      "layer": "staff_organization",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestStaffOfficeOut**

    **Type**: [SuggestStaffOfficeOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestStaffOfficeOut)

    **Example**

    ```
    {
      "layer": "staff_office",
      "id": "example",
      "text": "example",
      "address": "example"
    }
    ```

-   **SuggestStaffGroupOut**

    **Type**: [SuggestStaffGroupOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestStaffGroupOut)

    **Example**

    ```
    {
      "layer": "staff_group",
      "id": "example",
      "text": "example",
      "url": "example",
      "type": "example",
      "role_scope": "example"
    }
    ```

-   **SuggestStaffPersonOut**

    **Type**: [SuggestStaffPersonOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestStaffPersonOut)

    **Example**

    ```
    {
      "layer": "staff_login",
      "id": "example",
      "text": "example",
      "full_name": "example",
      "yandex_uid": "example",
      "uid": "example",
      "email": "example",
      "group_id": "example",
      "avatar": "example",
      "department": "example"
    }
    ```

-   **SuggestStaffRoomOut**

    **Type**: [SuggestStaffRoomOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestStaffRoomOut)

    **Example**

    ```
    {
      "layer": "staff_room",
      "id": "example",
      "text": "example",
      "office_id": "example",
      "floor_number": "example",
      "floor_id": "example"
    }
    ```

-   **SuggestWikiTableOut**

    **Type**: [SuggestWikiTableOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestWikiTableOut)

    **Example**

    ```
    {
      "layer": "wiki_table_source",
      "id": "example",
      "text": "example",
      "orig_id": "example",
      "row_id": "example",
      "parent_id": "example",
      "display_text": "example"
    }
    ```

-   **SuggestYtTableOut**

    **Type**: [SuggestYtTableOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestYtTableOut)

    **Example**

    ```
    {
      "layer": "yt_table_source",
      "id": "example",
      "text": "example",
      "orig_id": "example",
      "row_id": "example",
      "parent_id": "example",
      "display_text": "example"
    }
    ```

-   **SuggestDirUserOut**

    **Type**: [SuggestDirUserOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestDirUserOut)

    **Example**

    ```
    {
      "layer": "dir_user",
      "id": "example",
      "text": "example",
      "login": "example",
      "avatar": "example",
      "yandex_uid": "example",
      "uid": "example",
      "cloud_uid": "example",
      "email": "example"
    }
    ```

-   **SuggestDirGroupOut**

    **Type**: [SuggestDirGroupOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestDirGroupOut)

    **Example**

    ```
    {
      "layer": "dir_group",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestDirDepartmentOut**

    **Type**: [SuggestDirDepartmentOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestDirDepartmentOut)

    **Example**

    ```
    {
      "layer": "dir_department",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestTrackerQueueOut**

    **Type**: [SuggestTrackerQueueOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestTrackerQueueOut)

    **Example**

    ```
    {
      "layer": "tracker_queue",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestTrackerProjectOut**

    **Type**: [SuggestTrackerProjectOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestTrackerProjectOut)

    **Example**

    ```
    {
      "layer": "tracker_project",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestTrackerBoardOut**

    **Type**: [SuggestTrackerBoardOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestTrackerBoardOut)

    **Example**

    ```
    {
      "layer": "tracker_board",
      "id": "example",
      "text": "example"
    }
    ```

-   **SuggestTrackerSprintOut**

    **Type**: [SuggestTrackerSprintOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestTrackerSprintOut)

    **Example**

    ```
    {
      "layer": "tracker_sprint",
      "id": "example",
      "text": "example",
      "board": "example"
    }
    ```

-   **SuggestTrackerComponentOut**

    **Type**: [SuggestTrackerComponentOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestTrackerComponentOut)

    **Example**

    ```
    {
      "layer": "tracker_component",
      "id": "example",
      "text": "example",
      "queue": "example"
    }
    ```

-   **SuggestTrackerIssueOut**

    **Type**: [SuggestTrackerIssueOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestTrackerIssueOut)

    **Example**

    ```
    {
      "layer": "tracker_issue",
      "id": "example",
      "text": "example",
      "queue": "example",
      "status": "example"
    }
    ```

-   **SuggestTrackerFieldOut**

    **Type**: [SuggestTrackerFieldOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_suggest_view#entity-SuggestTrackerFieldOut)

    **Example**

    ```
    {
      "layer": "tracker_field",
      "id": "example",
      "slug": "example",
      "text": "example",
      "queue": "example"
    }
    ```
**Example**

```
{
  "layer": "country",
  "id": "example",
  "text": "example",
  "orig_id": "example"
}
```

## SuggestCountryOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Country ID *Example:* `example` |
| *orig_id* | **Type**: string Country ID in the Yandex geolocation database *Example:* `example` |
| *text* | **Type**: string Country name *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `country` *Const:* `country` |

**Example**

```
{
  "layer": "country",
  "id": "example",
  "text": "example",
  "orig_id": "example"
}
```

## SuggestCityOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string City ID *Example:* `example` |
| *orig_id* | **Type**: string City ID in the Yandex geolocation database *Example:* `example` |
| *text* | **Type**: string City name *Example:* `example` |
| *country_id* | **Type**: string Country ID *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `city` *Const:* `city` |
| *population* | **Type**: integer City population from the Yandex geolocation database |

**Example**

```
{
  "layer": "city",
  "id": "example",
  "text": "example",
  "country_id": "example",
  "population": 0,
  "orig_id": "example"
}
```

## SuggestUniversityOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string University ID *Example:* `example` |
| *text* | **Type**: string University name *Example:* `example` |
| *city* | **Type**: string University city *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `university` *Const:* `university` |
| *region* | **Type**: string Region *Example:* `example` |

**Example**

```
{
  "layer": "university",
  "id": "example",
  "text": "example",
  "city": "example",
  "region": "example"
}
```

## SuggestAddressOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Address from geo-suggestion *Example:* `example` |
| *text* | **Type**: string Address from geo-suggestion *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `address` *Const:* `address` |

**Example**

```
{
  "layer": "address",
  "id": "example",
  "text": "example"
}
```

## SuggestGenderOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Gender slug *Example:* `example` |
| *text* | **Type**: string Gender name *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `gender` *Const:* `gender` |

**Example**

```
{
  "layer": "gender",
  "id": "example",
  "text": "example"
}
```

## SuggestUserEmailOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string User email address *Example:* `example` |
| *text* | **Type**: string User email address *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `user_email_list` *Const:* `user_email_list` |

**Example**

```
{
  "layer": "user_email_list",
  "id": "example",
  "text": "example"
}
```

## SuggestWebMasterOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Domain slug from Webmaster *Example:* `example` |
| *text* | **Type**: string Domain from Webmaster *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `web_master_site` *Const:* `web_master_site` |

**Example**

```
{
  "layer": "web_master_site",
  "id": "example",
  "text": "example"
}
```

## SuggestAbcServiceOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Service ID in ABC *Example:* `example` |
| *text* | **Type**: string Service name *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `abc_service` *Const:* `abc_service` |

**Example**

```
{
  "layer": "abc_service",
  "id": "example",
  "text": "example"
}
```

## SuggestMusicGenreOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Music genre slug *Example:* `example` |
| *text* | **Type**: string Music genre name *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `music_genre` *Const:* `music_genre` |
| *tracks_count* | **Type**: integer Number of tracks in the genre |

**Example**

```
{
  "layer": "music_genre",
  "id": "example",
  "text": "example",
  "tracks_count": 0
}
```

## SuggestStaffOrganizationOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Organization ID in Staff *Example:* `example` |
| *text* | **Type**: string Organization name *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `staff_organization` *Const:* `staff_organization` |

**Example**

```
{
  "layer": "staff_organization",
  "id": "example",
  "text": "example"
}
```

## SuggestStaffOfficeOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Office ID in Staff *Example:* `example` |
| *text* | **Type**: string Office name *Example:* `example` |
| *address* | **Type**: string Office address *Example:* `example` |
| *layer* | **Type**: string *Default:* `staff_office` *Const:* `staff_office` |

**Example**

```
{
  "layer": "staff_office",
  "id": "example",
  "text": "example",
  "address": "example"
}
```

## SuggestStaffGroupOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Group ID in Staff *Example:* `example` |
| *text* | **Type**: string Group name *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `staff_group` *Const:* `staff_group` |
| *role_scope* | **Type**: string Group scope *Example:* `example` |
| *type* | **Type**: string Group type *Example:* `example` |
| *url* | **Type**: string Group slug *Example:* `example` |

**Example**

```
{
  "layer": "staff_group",
  "id": "example",
  "text": "example",
  "url": "example",
  "type": "example",
  "role_scope": "example"
}
```

## SuggestStaffPersonOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Employee ID in Staff *Example:* `example` |
| *text* | **Type**: string Employee name *Example:* `example` |
| *avatar* | **Type**: string Employee avatar *Example:* `example` |
| *department* | **Type**: string Employee department in Staff *Example:* `example` |
| *email* | **Type**: string Employee email address *Example:* `example` |
| *full_name* | **Type**: string Employee full name *Example:* `example` |
| *group_id* | **Type**: string Group ID in Staff *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `staff_login` *Const:* `staff_login` |
| *uid* | **Type**: string Employee passport UID *Example:* `example` |
| *yandex_uid* | **Type**: string Employee passport UID *Example:* `example` |

**Example**

```
{
  "layer": "staff_login",
  "id": "example",
  "text": "example",
  "full_name": "example",
  "yandex_uid": "example",
  "uid": "example",
  "email": "example",
  "group_id": "example",
  "avatar": "example",
  "department": "example"
}
```

## SuggestStaffRoomOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Meeting room ID in Staff *Example:* `example` |
| *text* | **Type**: string Meeting room name *Example:* `example` |
| *floor_id* | **Type**: string Floor ID *Example:* `example` |
| *floor_number* | **Type**: string Floor number *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `staff_room` *Const:* `staff_room` |
| *office_id* | **Type**: string Office ID *Example:* `example` |

**Example**

```
{
  "layer": "staff_room",
  "id": "example",
  "text": "example",
  "office_id": "example",
  "floor_number": "example",
  "floor_id": "example"
}
```

## SuggestWikiTableOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Record ID for Wiki suggestion *Example:* `example` |
| *orig_id* | **Type**: string Record ID in Wiki *Example:* `example` |
| *text* | **Type**: string Record text *Example:* `example` |
| *display_text* | **Type**: string Text for display in the interface *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `wiki_table_source` *Const:* `wiki_table_source` |
| *parent_id* | **Type**: string Record ID in Wiki for linked suggestions *Example:* `example` |
| *row_id* | **Type**: string Universal record ID *Example:* `example` |

**Example**

```
{
  "layer": "wiki_table_source",
  "id": "example",
  "text": "example",
  "orig_id": "example",
  "row_id": "example",
  "parent_id": "example",
  "display_text": "example"
}
```

## SuggestYtTableOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Record ID for YT suggestion *Example:* `example` |
| *orig_id* | **Type**: string Record ID in YT *Example:* `example` |
| *text* | **Type**: string Record text *Example:* `example` |
| *display_text* | **Type**: string Text for display in the interface *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `yt_table_source` *Const:* `yt_table_source` |
| *parent_id* | **Type**: string Record ID in YT for linked suggestions *Example:* `example` |
| *row_id* | **Type**: string Universal record ID *Example:* `example` |

**Example**

```
{
  "layer": "yt_table_source",
  "id": "example",
  "text": "example",
  "orig_id": "example",
  "row_id": "example",
  "parent_id": "example",
  "display_text": "example"
}
```

## SuggestDirUserOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string User ID *Example:* `example` |
| *text* | **Type**: string User name *Example:* `example` |
| *avatar* | **Type**: string User avatar *Example:* `example` |
| *cloud_uid* | **Type**: string User cloud UID *Example:* `example` |
| *email* | **Type**: string User email address *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `dir_user` *Const:* `dir_user` |
| *login* | **Type**: string User login *Example:* `example` |
| *uid* | **Type**: string User passport UID *Example:* `example` |
| *yandex_uid* | **Type**: string User passport UID *Example:* `example` |

**Example**

```
{
  "layer": "dir_user",
  "id": "example",
  "text": "example",
  "login": "example",
  "avatar": "example",
  "yandex_uid": "example",
  "uid": "example",
  "cloud_uid": "example",
  "email": "example"
}
```

## SuggestDirGroupOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Group ID in collab *Example:* `example` |
| *text* | **Type**: string Group name *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `dir_group` *Const:* `dir_group` |

**Example**

```
{
  "layer": "dir_group",
  "id": "example",
  "text": "example"
}
```

## SuggestDirDepartmentOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Department ID in collab *Example:* `example` |
| *text* | **Type**: string Department name *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `dir_department` *Const:* `dir_department` |

**Example**

```
{
  "layer": "dir_department",
  "id": "example",
  "text": "example"
}
```

## SuggestTrackerQueueOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Queue key in Tracker *Example:* `example` |
| *text* | **Type**: string Queue name *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `tracker_queue` *Const:* `tracker_queue` |

**Example**

```
{
  "layer": "tracker_queue",
  "id": "example",
  "text": "example"
}
```

## SuggestTrackerProjectOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Project ID in Tracker *Example:* `example` |
| *text* | **Type**: string Project name in Tracker *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `tracker_project` *Const:* `tracker_project` |

**Example**

```
{
  "layer": "tracker_project",
  "id": "example",
  "text": "example"
}
```

## SuggestTrackerBoardOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Agile board ID in Tracker *Example:* `example` |
| *text* | **Type**: string Agile board name *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `tracker_board` *Const:* `tracker_board` |

**Example**

```
{
  "layer": "tracker_board",
  "id": "example",
  "text": "example"
}
```

## SuggestTrackerSprintOut

| Name | Description |
|------|-------------|
| *board* | **Type**: string Agile board name *Example:* `example` |
| *id* | **Type**: string Sprint ID in Tracker *Example:* `example` |
| *text* | **Type**: string Sprint name *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `tracker_sprint` *Const:* `tracker_sprint` |

**Example**

```
{
  "layer": "tracker_sprint",
  "id": "example",
  "text": "example",
  "board": "example"
}
```

## SuggestTrackerComponentOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Component ID in Tracker *Example:* `example` |
| *queue* | **Type**: string Component queue *Example:* `example` |
| *text* | **Type**: string Component name *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `tracker_component` *Const:* `tracker_component` |

**Example**

```
{
  "layer": "tracker_component",
  "id": "example",
  "text": "example",
  "queue": "example"
}
```

## SuggestTrackerIssueOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Issue ID in Tracker *Example:* `example` |
| *queue* | **Type**: string Issue queue *Example:* `example` |
| *status* | **Type**: string Issue status *Example:* `example` |
| *text* | **Type**: string Issue title *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `tracker_issue` *Const:* `tracker_issue` |

**Example**

```
{
  "layer": "tracker_issue",
  "id": "example",
  "text": "example",
  "queue": "example",
  "status": "example"
}
```

## SuggestTrackerFieldOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Field ID in Tracker (including local fields) *Example:* `example` |
| *slug* | **Type**: string Field slug *Example:* `example` |
| *text* | **Type**: string Field name *Example:* `example` |
| *layer* | **Type**: string Suggestion type *Default:* `tracker_field` *Const:* `tracker_field` |
| *queue* | **Type**: string Field queue (for local fields) *Example:* `example` |

**Example**

```
{
  "layer": "tracker_field",
  "id": "example",
  "slug": "example",
  "text": "example",
  "queue": "example"
}
```

# 404 Not Found

Not Found

## Body

application/json

```
{
  "code": "not_found",
  "detail": "example"
}
```

| Name | Description |
|------|-------------|
| *code* | **Type**: string Error code *Const:* `not_found` *Example:* `example` |
| *detail* | **Type**: string Error text *Example:* `example` |

# 408 Request Timeout

Request Timeout

## Body

application/json

```
{
  "code": "connect_timeout",
  "detail": "example"
}
```

| Name | Description |
|------|-------------|
| *code* | **Type**: string Error code *Const:* `connect_timeout` *Example:* `example` |
| *detail* | **Type**: string Error text *Example:* `example` |

# 422 Unprocessable Entity

Unprocessable Content

## Body

application/json

```
{}
```

| Name | Description |
|------|-------------|