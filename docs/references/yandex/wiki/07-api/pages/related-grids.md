# Получить динамические таблицы, связанные со страницей




Возвращает список динамических таблиц, привязанных к странице


## Request






GET


    
        
```
https://api.wiki.yandex.net/v1/pages/{idx}/grids
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| idx | Type: integer |


### Query parameters



| Name | Description |
| --- | --- |
| cursor | Type: string Example: `` |
| order_by | Type: string Если указано, отсортировать выдачу по полю в направлении direction Enum: title, created_at |
| order_direction | All of: OrderDirection OrderDirection Type: string An enumeration. Enum: asc, desc Если указано поле order_by, направление сортировки Default: asc Example: `` |
| page_id | Type: integer legacy Номер страницы выдачи Default: 1 Min value: 1 |
| page_size | Type: integer Число результатов на странице выдачи. Default: 25 Min value: 1 Max value: 50 |


## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "results": [
    {
      "id": "example",
      "title": "example",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "next_cursor": "example",
  "prev_cursor": "example",
  "has_next": true,
  "page_id": 0
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| has_next | Type: boolean Для обратной совместимости, если задан курсор — то смотреть на ..._cursor |
| page_id | Type: integer Для обратной совместимости, если задан курсор — всегда равен 1 |
| results | Type: PageGridsSchema[] Example [ { "id": "example", "title": "example", "created_at": "2025-01-01T00:00:00Z" } ] |
| next_cursor | Type: string Example: example |
| prev_cursor | Type: string Example: example |




### PageGridsSchema



| Name | Description |
| --- | --- |
| created_at | Type: string<date-time> Example: 2025-01-01T00:00:00Z |
| id | Type: string<uuid4> Example: example |
| title | Type: string Example: example |

**Example**
    
        
```
{
  "id": "example",
  "title": "example",
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__append_content#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__append_content#path-parameters)
  - [Query parameters](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__append_content#query-parameters)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__append_content#body)
  - [Location](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__append_content#entity-Location)
  - [PageAppendContentBodySchema](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__append_content#entity-PageAppendContentBodySchema)
  - [PageAppendContentSectionSchema](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__append_content#entity-PageAppendContentSectionSchema)
  - [PageAppendContentAnchorSchema](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__append_content#entity-PageAppendContentAnchorSchema)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__append_content#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__append_content#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__append_content#body1)
  - [PageType](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__append_content#entity-PageType)
  - [PageDetailsSchema](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__append_content#entity-PageDetailsSchema)
  - [RedirectSchema](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__append_content#entity-RedirectSchema)
  - [BreadcrumbSchema](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__append_content#entity-BreadcrumbSchema)
  - [PageAttributesSchema](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__append_content#entity-PageAttributesSchema)


