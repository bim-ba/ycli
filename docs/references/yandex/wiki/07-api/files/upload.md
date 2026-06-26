# Добавить прикрепленный файл




Добавить на страницу файл из указанной сессии загрузки. [Как создать сессию загрузки файла](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/upload_sessions/upload_sessions__create_upload_session)


## Request






POST


    
        
```
https://api.wiki.yandex.net/v1/pages/{idx}/attachments
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| idx | Type: integer |



### Body


application/json
    
        
```
{
  "upload_sessions": [
    "example"
  ]
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| upload_sessions | Type: string<uuid4>[] Example [ "example" ] |



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
  ]
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| results | Type: AttachmentSchema[] Example [ { "id": 0, "name": "example", "download_url": "example", "size": "example", "description": "example", "user": { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" }, "created_at": "2025-01-01T00:00:00Z", "mimetype": "example", "has_preview": true, "check_status": "ready" } ] |




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

- [Request](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__download_by_file_id#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__download_by_file_id#path-parameters)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__download_by_file_id#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__download_by_file_id#200-ok)


