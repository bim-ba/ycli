# Копировать таблицу




## Request






POST


    
        
```
https://api.wiki.yandex.net/v1/grids/{idx}/clone
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| idx | Type: string<uuid4> Example: `` |



### Body


application/json
    
        
```
{
  "target": "example",
  "title": "example",
  "with_data": false
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| target | Type: string Слаг (slug) страницы, на которую нужно скопировать таблицу. Если страницы нет, она будет создана. Example: example |
| title | Type: string Если передан, название после копирования Min length: 1 Max length: 255 Example: example |
| with_data | Type: boolean Default: false |



## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "operation": {
    "type": "clone",
    "id": "example"
  },
  "dry_run": false,
  "status_url": "example"
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| operation | Type: B2BOperationIdentity Example { "type": "clone", "id": "example" } |
| status_url | Type: string URL, по которому вернется прогресс операции Example: example |
| dry_run | Type: boolean Default: false |




### B2BOperationType



An enumeration.


**Type**: string


*Enum:* `clone`, `clone_inline_grid`




### B2BOperationIdentity



| Name | Description |
| --- | --- |
| id | Type: string Example: example |
| type | Type: B2BOperationType An enumeration. Enum: clone, clone_inline_grid |

**Example**
    
        
```
{
  "type": "clone",
  "id": "example"
}
```

---

