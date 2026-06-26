# Удалить строки




## Request






DELETE


    
        
```
https://api.wiki.yandex.net/v1/grids/{idx}/rows
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
  "row_ids": [
    "example"
  ]
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| row_ids | Type: string[] Min items: 1 Example [ "example" ] |
| revision | Type: string Example: example |



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

- [Request](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__add_columns#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__add_columns#path-parameters)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__add_columns#body)
  - [ColumnType](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__add_columns#entity-ColumnType)
  - [WidthUnits](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__add_columns#entity-WidthUnits)
  - [ColumnPinTypes](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__add_columns#entity-ColumnPinTypes)
  - [BGColor](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__add_columns#entity-BGColor)
  - [TextFormat](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__add_columns#entity-TextFormat)
  - [TicketField](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__add_columns#entity-TicketField)
  - [NewColumnSchema](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__add_columns#entity-NewColumnSchema)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__add_columns#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__add_columns#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__add_columns#body1)


