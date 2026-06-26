# Получить статус операции копирования




## Request






GET


    
        
```
https://api.wiki.yandex.net/v1/operations/clone/{task_id}
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| task_id | Type: string Example: `` |


## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "status": "scheduled",
  "progress": {
    "percentage": 0.5,
    "details": "example"
  },
  "result": {
    "page": {
      "id": 0,
      "slug": "example"
    }
  }
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| status | Type: Status An enumeration. Enum: scheduled, in_progress, success, failed |
| progress | Type: Progress Example { "percentage": 0.5, "details": "example" } |
| result | Type: PageCloneResponse Example { "page": { "id": 0, "slug": "example" } } |




### Status



An enumeration.


**Type**: string


*Enum:* `scheduled`, `in_progress`, `success`, `failed`




### Progress



| Name | Description |
| --- | --- |
| details | Type: string Example: example |
| percentage | Type: number |

**Example**
    
        
```
{
  "percentage": 0.5,
  "details": "example"
}
```


        
            
            
        
    



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


        
            
            
        
    



### PageCloneResponse



| Name | Description |
| --- | --- |
| page | All of 1 type PageSchema Type: PageSchema Example { "id": 0, "slug": "example" } Клонированная страница Example { "id": 0, "slug": "example" } |

**Example**
    
        
```
{
  "page": {
    "id": 0,
    "slug": "example"
  }
}
```

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/Operacii/ru/api-ref/Operacii/operations__get_clone_inline_grid_operation_status#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/Operacii/ru/api-ref/Operacii/operations__get_clone_inline_grid_operation_status#path-parameters)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/Operacii/ru/api-ref/Operacii/operations__get_clone_inline_grid_operation_status#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/Operacii/ru/api-ref/Operacii/operations__get_clone_inline_grid_operation_status#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/Operacii/ru/api-ref/Operacii/operations__get_clone_inline_grid_operation_status#body)
  - [Status](https://yandex.ru/support/wiki/ru/api-ref/Operacii/ru/api-ref/Operacii/operations__get_clone_inline_grid_operation_status#entity-Status)
  - [Progress](https://yandex.ru/support/wiki/ru/api-ref/Operacii/ru/api-ref/Operacii/operations__get_clone_inline_grid_operation_status#entity-Progress)
  - [PageSchema](https://yandex.ru/support/wiki/ru/api-ref/Operacii/ru/api-ref/Operacii/operations__get_clone_inline_grid_operation_status#entity-PageSchema)
  - [GridCloneResponse](https://yandex.ru/support/wiki/ru/api-ref/Operacii/ru/api-ref/Operacii/operations__get_clone_inline_grid_operation_status#entity-GridCloneResponse)


