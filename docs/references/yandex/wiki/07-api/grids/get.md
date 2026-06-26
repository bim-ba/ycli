# Получить таблицу




## Request






GET


    
        
```
https://api.wiki.yandex.net/v1/grids/{idx}
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| idx | Type: string<uuid4> Example: `` |


### Query parameters



| Name | Description |
| --- | --- |
| fields | Type: string Дополнительные поля, через запятую; см. описание формата ответа. Example: `` |
| filter | Type: string Отфильтровать строки; Например [slug] ~ wiki AND [slug2]<32 Example: `` |
| only_cols | Type: string Вернуть только определенные колонки. Слаг через запятую Example: `` |
| only_rows | Type: string Вернуть только определенные ряды. ID через запятую Example: `` |
| revision | Type: integer Загрузить старую версию динамической таблицы |
| sort | Type: string Отсортировать строки по колонкам; Например slug, -slug2, slug3 Example: `` |


## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "id": "example",
  "created_at": "2025-01-01T00:00:00Z",
  "title": "example",
  "page": {
    "id": 0,
    "slug": "example"
  },
  "structure": {
    "default_sort": [
      {
        "slug": "example",
        "title": "example",
        "direction": "asc"
      }
    ],
    "columns": [
      {
        "id": "example",
        "slug": "example",
        "title": "example",
        "type": "string",
        "required": true,
        "width": 0,
        "width_units": "%",
        "pinned": "left",
        "color": "blue",
        "multiple": true,
        "format": "yfm",
        "ticket_field": "assignee",
        "select_options": [
          "example"
        ],
        "mark_rows": true,
        "description": "example"
      }
    ]
  },
  "rich_text_format": null,
  "rows": [
    {
      "id": "example",
      "row": [
        0
      ],
      "pinned": true,
      "color": null
    }
  ],
  "revision": "example",
  "user_permissions": [
    "create_page"
  ],
  "attributes": {
    "created_at": "2025-01-01T00:00:00Z",
    "modified_at": "2025-01-01T00:00:00Z"
  },
  "template_id": 0
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| created_at | Type: string<date-time> Example: 2025-01-01T00:00:00Z |
| id | Any of 2 types Type: string<uuid4> Example: example Type: integer Example: example |
| page | Type: PageIdentity Example { "id": 0, "slug": "example" } |
| revision | Type: string Example: example |
| rich_text_format | Type: TextFormat An enumeration. Enum: yfm, wom, plain |
| rows | Type: GridRowSchema[] Example [ { "id": "example", "row": [ 0 ], "pinned": true, "color": "blue" } ] |
| structure | Type: GridStructureSchema Example { "default_sort": [ { "slug": "example", "title": "example", "direction": "asc" } ], "columns": [ { "id": "example", "slug": "example", "title": "example", "type": "string", "required": true, "width": 0, "width_units": "%", "pinned": "left", "color": "blue", "multiple": true, "format": "yfm", "ticket_field": "assignee", "select_options": [ "example" ], "mark_rows": true, "description": "example" } ] } |
| title | Type: string Example: example |
| attributes | All of 1 type GridAttributesSchema Type: GridAttributesSchema Example { "created_at": "2025-01-01T00:00:00Z", "modified_at": "2025-01-01T00:00:00Z" } По умолчанию поле не возвращается Укажите attributes в списке ?fields=attributes, ... для получения в ответе. Возвращает дополнительные атрибуты динамической таблицы. Example { "created_at": "2025-01-01T00:00:00Z", "modified_at": "2025-01-01T00:00:00Z" } |
| template_id | Type: integer |
| user_permissions | Type: UserPermission[] По умолчанию поле не возвращается Укажите user_permissions в списке ?fields=user_permissions, ... для получения в ответе. Возвращает права доступа страницы, которой принадлежит динамическая таблица. Example [ "create_page" ] |




### PageIdentity



| Name | Description |
| --- | --- |
| id | Type: integer Обязателен id либо slug, при передаче обоих id имеет приоритет и slug игнорируется. |
| slug | Type: string Example: example |

**Example**
    
        
```
{
  "id": 0,
  "slug": "example"
}
```


        
            
            
        
    



### SortDirection



An enumeration.


**Type**: string


*Enum:* `asc`, `desc`




### ColumnSortSchema



| Name | Description |
| --- | --- |
| direction | Type: SortDirection An enumeration. Enum: asc, desc |
| slug | Type: string Example: example |
| title | Type: string Example: example |

**Example**
    
        
```
{
  "slug": "example",
  "title": "example",
  "direction": "asc"
}
```


        
            
            
        
    



### ColumnType



An enumeration.


**Type**: string


*Enum:* `string`, `number`, `date`, `select`, `staff`, `checkbox`, `ticket`, `ticket_field`




### WidthUnits



An enumeration.


**Type**: string


*Enum:* `%`, `px`




### ColumnPinTypes



An enumeration.


**Type**: string


*Enum:* `left`, `right`




### BGColor



An enumeration.


**Type**: string


*Enum:* `blue`, `yellow`, `pink`, `red`, `green`, `mint`, `grey`, `orange`, `magenta`, `purple`, `copper`, `ocean`




### TextFormat



An enumeration.


**Type**: string


*Enum:* `yfm`, `wom`, `plain`




### TicketField



An enumeration.


**Type**: string


*Enum:* `assignee`, `components`, `created_at`, `deadline`, `description`, `end`, `estimation`, `fixversions`, `followers`, `last_comment_updated_at`, `original_estimation`, `parent`, `pending_reply_from`, `priority`, `project`, `queue`, `reporter`, `resolution`, `resolved_at`, `sprint`, `start`, `status`, `status_start_time`, `status_type`, `storypoints`, `subject`, `tags`, `type`, `updated_at`, `votes`




### ColumnSchema



| Name | Description |
| --- | --- |
| required | Type: boolean |
| slug | Type: string Example: example |
| title | Type: string Example: example |
| type | Type: ColumnType An enumeration. Enum: string, number, date, select, staff, checkbox, ticket, ticket_field |
| color | Type: BGColor An enumeration. Enum: blue, yellow, pink, red, green, mint, grey, orange, magenta, purple, copper, ocean |
| description | Type: string Описание Example: example |
| format | All of 1 type TextFormat Type: TextFormat An enumeration. Enum: yfm, wom, plain Только для text; None — текст без форматирования. Example: yfm |
| id | Type: string Example: example |
| mark_rows | Type: boolean Только для checkbox; Отмечает ряд как выполненный в интерфейсе |
| multiple | Type: boolean Только для select и staff; Включает множественный выбор. |
| pinned | Type: ColumnPinTypes An enumeration. Enum: left, right |
| select_options | Type: string[] Только для select; Задает варианты выбора Example [ "example" ] |
| ticket_field | All of 1 type TicketField Type: TicketField An enumeration. Enum: assignee, components, created_at, deadline, description, end, estimation, fixversions, followers, last_comment_updated_at, original_estimation, parent, pending_reply_from, priority, project, queue, reporter, resolution, resolved_at, sprint, start, status, status_start_time, status_type, storypoints, subject, tags, type, updated_at, votes Только для ticket-field; Example: assignee |
| width | Type: integer |
| width_units | Type: WidthUnits An enumeration. Enum: %, px |

**Example**
    
        
```
{
  "id": "example",
  "slug": "example",
  "title": "example",
  "type": "string",
  "required": true,
  "width": 0,
  "width_units": "%",
  "pinned": "left",
  "color": "blue",
  "multiple": true,
  "format": "yfm",
  "ticket_field": "assignee",
  "select_options": [
    "example"
  ],
  "mark_rows": true,
  "description": "example"
}
```


        
            
            
        
    



### GridStructureSchema



| Name | Description |
| --- | --- |
| columns | Type: ColumnSchema[] Example [ { "id": "example", "slug": "example", "title": "example", "type": "string", "required": true, "width": 0, "width_units": "%", "pinned": "left", "color": "blue", "multiple": true, "format": "yfm", "ticket_field": "assignee", "select_options": [ "example" ], "mark_rows": true, "description": "example" } ] |
| default_sort | Type: ColumnSortSchema[] Example [ { "slug": "example", "title": "example", "direction": "asc" } ] |

**Example**
    
        
```
{
  "default_sort": [
    {
      "slug": "example",
      "title": "example",
      "direction": "asc"
    }
  ],
  "columns": [
    {
      "id": "example",
      "slug": "example",
      "title": "example",
      "type": "string",
      "required": true,
      "width": 0,
      "width_units": "%",
      "pinned": "left",
      "color": "blue",
      "multiple": true,
      "format": "yfm",
      "ticket_field": "assignee",
      "select_options": [
        "example"
      ],
      "mark_rows": true,
      "description": "example"
    }
  ]
}
```


        
            
            
        
    



### TicketSchema



| Name | Description |
| --- | --- |
| key | Type: string Example: example |
| resolved | Type: boolean |

**Example**
    
        
```
{
  "key": "example",
  "resolved": true
}
```


        
            
            
        
    



### UserIdentity



| Name | Description |
| --- | --- |
| cloud_uid | Type: string Example: example |
| uid | Type: string Example: example |

**Example**
    
        
```
{
  "uid": "example",
  "cloud_uid": "example"
}
```


        
            
            
        
    



### UserSchema



| Name | Description |
| --- | --- |
| affiliation | Type: string Example: example |
| display_name | Type: string Example: example |
| id | Type: integer |
| is_dismissed | Type: boolean |
| username | Type: string Example: example |
| identity | Type: UserIdentity Example { "uid": "example", "cloud_uid": "example" } |

**Example**
    
        
```
{
  "id": 0,
  "identity": {
    "uid": "example",
    "cloud_uid": "example"
  },
  "username": "example",
  "display_name": "example",
  "is_dismissed": true,
  "affiliation": "example"
}
```


        
            
            
        
    



### UnresolvedUserSchema



| Name | Description |
| --- | --- |
| identity | Type: UserIdentity Example { "uid": "example", "cloud_uid": "example" } |
| username | Type: string Example: example |

**Example**
    
        
```
{
  "username": "example",
  "identity": {
    "uid": "example",
    "cloud_uid": "example"
  }
}
```


        
            
            
        
    



### TrackerEnumField



| Name | Description |
| --- | --- |
| display | Type: string Example: example |
| key | Type: string Example: example |

**Example**
    
        
```
{
  "display": "example",
  "key": "example"
}
```


        
            
            
        
    



### GridRowSchema



| Name | Description |
| --- | --- |
| id | Type: string Example: example |
| row | Type: arrayAny of 10 types Type: integer Type: number Type: boolean Type: string Example: example TicketSchema Type: TicketSchema Example { "key": "example", "resolved": true } Type: string[] Example [ "example" ] Type: arrayAny of 2 types UserSchema Type: UserSchema Example { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" } UnresolvedUserSchema Type: UnresolvedUserSchema Example { "username": "example", "identity": { "uid": "example", "cloud_uid": "example" } } Example [ { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" } ] UserSchema Type: UserSchema Example { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" } UnresolvedUserSchema Type: UnresolvedUserSchema Example { "username": "example", "identity": { "uid": "example", "cloud_uid": "example" } } TrackerEnumField Type: TrackerEnumField Example { "display": "example", "key": "example" } Example [ 0 ] |
| color | Type: BGColor An enumeration. Enum: blue, yellow, pink, red, green, mint, grey, orange, magenta, purple, copper, ocean |
| pinned | Type: boolean |

**Example**
    
        
```
{
  "id": "example",
  "row": [
    0
  ],
  "pinned": true,
  "color": "blue"
}
```


        
            
            
        
    



### UserPermission



An enumeration.


**Type**: string


*Enum:* `create_page`, `delete`, `edit`, `view`, `comment`, `change_authors`, `change_acl`, `set_redirect`, `manage_invite`, `view_invite`, `admin`




### GridAttributesSchema



| Name | Description |
| --- | --- |
| created_at | Type: string<date-time> Example: 2025-01-01T00:00:00Z |
| modified_at | Type: string<date-time> Example: 2025-01-01T00:00:00Z |

**Example**
    
        
```
{
  "created_at": "2025-01-01T00:00:00Z",
  "modified_at": "2025-01-01T00:00:00Z"
}
```

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_grid#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_grid#path-parameters)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_grid#body)
  - [SortDirection](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_grid#entity-SortDirection)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_grid#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_grid#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_grid#body1)


