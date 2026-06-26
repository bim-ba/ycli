# Переместить столбцы




## Request






POST


    
        
```
https://api.wiki.yandex.net/v1/grids/{idx}/columns/move
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
  "column_slug": "example",
  "columns_count": 0
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| column_slug | Type: string Example: example |
| position | Type: integer |
| columns_count | Type: integer Exclusive min: false |
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

- [Request](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__clone_grid#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__clone_grid#path-parameters)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__clone_grid#body)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__clone_grid#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__clone_grid#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__clone_grid#body1)
  - [B2BOperationType](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__clone_grid#entity-B2BOperationType)
  - [B2BOperationIdentity](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__clone_grid#entity-B2BOperationIdentity)


