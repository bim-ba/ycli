# Переместить строки




## Request






POST


    
        
```
https://api.wiki.yandex.net/v1/grids/{idx}/rows/move
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
  "after_row_id": "example",
  "row_id": "example",
  "rows_count": 0
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| row_id | Type: string Example: example |
| after_row_id | Type: string Example: example |
| position | Type: integer |
| revision | Type: string Example: example |
| rows_count | Type: integer Exclusive min: false |



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

- [Request](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__move_columns#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__move_columns#path-parameters)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__move_columns#body)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__move_columns#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__move_columns#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__move_columns#body1)


