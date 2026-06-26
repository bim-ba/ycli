# Получить список подстраниц




Возвращает все подстраницы (всех уровней, не только первого) данной страницы, доступных текущему пользователю.

Ответ может содержать меньше результатов чем page_size, в зависимости от того, к какому количеству страниц есть доступ.


## Request






GET


    
        
```
https://api.wiki.yandex.net/v1/pages/{idx}/descendants
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| idx | Type: integer |


### Query parameters



| Name | Description |
| --- | --- |
| actuality | Type: string An enumeration. Enum: actual, obsolete |
| cursor | Type: string Example: `` |
| include_self | Type: boolean Включить в ответ текущую страницу Default: false |
| page_size | Type: integer Число результатов на странице выдачи. Default: 50 Min value: 1 Max value: 100 |


## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "results": [
    {
      "id": 0,
      "slug": "example"
    }
  ],
  "next_cursor": "example",
  "prev_cursor": "example",
  "page_id": 0
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| page_id | Type: integer Для обратной совместимости, если задан курсор - всегда равен 1 |
| results | Type: PageSchema[] Example [ { "id": 0, "slug": "example" } ] |
| next_cursor | Type: string Example: example |
| prev_cursor | Type: string Example: example |




### PageSchema



| Name | Description |
| --- | --- |
| id | Type: integer |
| slug | Type: string Example: example |

**Example**
    
        
```
{
  "id": 0,
  "slug": "example"
}
```

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__descendants_by_slug#request)
  - [Query parameters](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__descendants_by_slug#query-parameters)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__descendants_by_slug#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__descendants_by_slug#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__descendants_by_slug#body)
  - [PageSchema](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__descendants_by_slug#entity-PageSchema)


