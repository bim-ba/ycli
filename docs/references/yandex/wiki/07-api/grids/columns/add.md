# Добавить столбцы




## Request






POST


    
        
```
https://api.wiki.yandex.net/v1/grids/{idx}/columns
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| idx | Type: string<uuid4> Example: `` |



### Body


application/json
    
        
```
{
  "revision": "example",
  "position": 0,
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


        
            
            
        
    

| Name | Description |
| --- | --- |
| columns | Type: NewColumnSchema[] Example [ { "id": "example", "slug": "example", "title": "example", "type": "string", "required": true, "width": 0, "width_units": "%", "pinned": "left", "color": "blue", "multiple": true, "format": "yfm", "ticket_field": "assignee", "select_options": [ "example" ], "mark_rows": true, "description": "example" } ] |
| position | Type: integer |
| revision | Type: string Example: example |




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




### NewColumnSchema



| Name | Description |
| --- | --- |
| required | Type: boolean |
| slug | Type: string Example: example |
| title | Type: string Min length: 1 Max length: 255 Example: example |
| type | Type: ColumnType An enumeration. Enum: string, number, date, select, staff, checkbox, ticket, ticket_field |
| color | Type: BGColor An enumeration. Enum: blue, yellow, pink, red, green, mint, grey, orange, magenta, purple, copper, ocean |
| description | Type: string Описание Max length: 1024 Example: example |
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


        
            
            
        
    


## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "revision": "example"
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| revision | Type: string Example: example |

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__remove_columns#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__remove_columns#path-parameters)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__remove_columns#body)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__remove_columns#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__remove_columns#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__remove_columns#body1)


