# Обновить таблицу




## Request






POST


    
        
```
https://api.wiki.yandex.net/v1/grids/{idx}
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
  "title": "example",
  "default_sort": [
    {}
  ]
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| default_sort | Type: object[] [additional] Type: SortDirection An enumeration. Enum: asc, desc Example [ {} ] | [additional] | Type: SortDirection An enumeration. Enum: asc, desc |
| [additional] | Type: SortDirection An enumeration. Enum: asc, desc |
| revision | Type: string Example: example |
| title | Type: string Min length: 1 Max length: 255 Example: example |




### SortDirection



An enumeration.


**Type**: string


*Enum:* `asc`, `desc`



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

- [Request](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__delete_grid#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__delete_grid#path-parameters)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__delete_grid#responses)
- [204 No Content](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__delete_grid#204-no-content)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__delete_grid#body)


