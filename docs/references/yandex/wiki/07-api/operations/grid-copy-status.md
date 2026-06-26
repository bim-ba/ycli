# Получить статус операции копирования встроенной таблицы




## Request






GET


    
        
```
https://api.wiki.yandex.net/v1/operations/clone_inline_grid/{task_id}
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
    "grid": {
      "id": 0,
      "slug": "example"
    },
    "page": null,
    "grid_id": "example"
  }
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| status | Type: Status An enumeration. Enum: scheduled, in_progress, success, failed |
| progress | Type: Progress Example { "percentage": 0.5, "details": "example" } |
| result | Type: GridCloneResponse Example { "grid": { "id": 0, "slug": "example" }, "page": null, "grid_id": "example" } |




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


        
            
            
        
    



### GridCloneResponse



| Name | Description |
| --- | --- |
| grid_id | Any of 2 types Type: string<uuid4> Example: example Type: integer Example: example |
| page | All of 1 type PageSchema Type: PageSchema Example { "id": 0, "slug": "example" } Страница на которую была скопирована динамическая таблица Example { "id": 0, "slug": "example" } |
| grid | All of 1 type PageSchema Type: PageSchema Example { "id": 0, "slug": "example" } На переходный период схема страницы устаревшего типа таблиц Example { "id": 0, "slug": "example" } |

**Example**
    
        
```
{
  "grid": {
    "id": 0,
    "slug": "example"
  },
  "page": null,
  "grid_id": "example"
}
```

---

