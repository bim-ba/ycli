# Получить прикрепленные файлы




## Request






GET


    
        
```
https://api.wiki.yandex.net/v1/pages/{idx}/attachments
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| idx | Type: integer |


### Query parameters



| Name | Description |
| --- | --- |
| cursor | Type: string Example: `` |
| order_by | Type: string Если указано, отсортировать выдачу по полю в направлении direction Enum: name, size, created_at |
| order_direction | All of: OrderDirection OrderDirection Type: string An enumeration. Enum: asc, desc Если указано поле order_by, направление сортировки Default: asc Example: `` |
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
      "name": "example",
      "download_url": "example",
      "size": "example",
      "description": "example",
      "user": {
        "id": 0,
        "identity": {
          "uid": "example",
          "cloud_uid": "example"
        },
        "username": "example",
        "display_name": "example",
        "is_dismissed": true,
        "affiliation": "example"
      },
      "created_at": "2025-01-01T00:00:00Z",
      "mimetype": "example",
      "has_preview": true,
      "check_status": "ready"
    }
  ],
  "next_cursor": "example",
  "prev_cursor": "example"
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| results | Type: AttachmentSchema[] Example [ { "id": 0, "name": "example", "download_url": "example", "size": "example", "description": "example", "user": { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" }, "created_at": "2025-01-01T00:00:00Z", "mimetype": "example", "has_preview": true, "check_status": "ready" } ] |
| next_cursor | Type: string Example: example |
| prev_cursor | Type: string Example: example |




### UserIdentity



| Name | Description |
| --- | --- |
| cloud_uid | Type: string Example: example |
| uid | Type: string Example: example |

**Example**
    
        
```
{
  "uid": "example",
  "cloud_uid": "example"
}
```


        
            
            
        
    



### UserSchema



| Name | Description |
| --- | --- |
| affiliation | Type: string Example: example |
| display_name | Type: string Example: example |
| id | Type: integer |
| is_dismissed | Type: boolean |
| username | Type: string Example: example |
| identity | Type: UserIdentity Example { "uid": "example", "cloud_uid": "example" } |

**Example**
    
        
```
{
  "id": 0,
  "identity": {
    "uid": "example",
    "cloud_uid": "example"
  },
  "username": "example",
  "display_name": "example",
  "is_dismissed": true,
  "affiliation": "example"
}
```


        
            
            
        
    



### FileCheckStatusType



An enumeration.


**Type**: string


*Enum:* `check`, `ready`, `deleted`, `infected`, `error`




### AttachmentSchema



| Name | Description |
| --- | --- |
| created_at | Type: string<date-time> Example: 2025-01-01T00:00:00Z |
| description | Type: string Example: example |
| download_url | Type: string Example: example |
| has_preview | Type: boolean |
| id | Type: integer |
| mimetype | Type: string Example: example |
| name | Type: string Example: example |
| size | Type: string Example: example |
| check_status | All of 1 type FileCheckStatusType Type: FileCheckStatusType An enumeration. Enum: check, ready, deleted, infected, error Default: ready |
| user | Type: UserSchema Example { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" } |

**Example**
    
        
```
{
  "id": 0,
  "name": "example",
  "download_url": "example",
  "size": "example",
  "description": "example",
  "user": {
    "id": 0,
    "identity": {
      "uid": "example",
      "cloud_uid": "example"
    },
    "username": "example",
    "display_name": "example",
    "is_dismissed": true,
    "affiliation": "example"
  },
  "created_at": "2025-01-01T00:00:00Z",
  "mimetype": "example",
  "has_preview": true,
  "check_status": "ready"
}
```

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attach_file#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attach_file#path-parameters)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attach_file#body)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attach_file#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attach_file#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attach_file#body1)
  - [UserIdentity](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attach_file#entity-UserIdentity)
  - [UserSchema](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attach_file#entity-UserSchema)
  - [FileCheckStatusType](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attach_file#entity-FileCheckStatusType)
  - [AttachmentSchema](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attach_file#entity-AttachmentSchema)


