# Удалить столбцы




## Request






DELETE


    
        
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
  "column_slugs": [
    "example"
  ]
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| column_slugs | Type: string[] Example [ "example" ] |
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

- [Request](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_cells#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_cells#path-parameters)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_cells#body)
  - [UserIdentityExtended](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_cells#entity-UserIdentityExtended)
  - [UpdateCellSchema](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_cells#entity-UpdateCellSchema)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_cells#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_cells#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_cells#body1)
  - [TicketSchema](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_cells#entity-TicketSchema)
  - [UserIdentity](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_cells#entity-UserIdentity)
  - [UserSchema](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_cells#entity-UserSchema)
  - [UnresolvedUserSchema](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_cells#entity-UnresolvedUserSchema)
  - [TrackerEnumField](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_cells#entity-TrackerEnumField)
  - [CellSchema](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__update_cells#entity-CellSchema)


