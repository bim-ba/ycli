# Ресурсы страниц



## Endpoints



- [Получить информацию о ресурсах страницы](https://yandex.ru/support/wiki/ru/api-ref/pagesresources/ru/api-ref/pagesresources/pagesresources__resources)

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/pagesresources/ru/api-ref/pagesresources/pagesresources__resources#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/pagesresources/ru/api-ref/pagesresources/pagesresources__resources#path-parameters)
  - [Query parameters](https://yandex.ru/support/wiki/ru/api-ref/pagesresources/ru/api-ref/pagesresources/pagesresources__resources#query-parameters)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/pagesresources/ru/api-ref/pagesresources/pagesresources__resources#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/pagesresources/ru/api-ref/pagesresources/pagesresources__resources#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/pagesresources/ru/api-ref/pagesresources/pagesresources__resources#body)
  - [ResourceType](https://yandex.ru/support/wiki/ru/api-ref/pagesresources/ru/api-ref/pagesresources/pagesresources__resources#entity-ResourceType)
  - [UserIdentity](https://yandex.ru/support/wiki/ru/api-ref/pagesresources/ru/api-ref/pagesresources/pagesresources__resources#entity-UserIdentity)
  - [UserSchema](https://yandex.ru/support/wiki/ru/api-ref/pagesresources/ru/api-ref/pagesresources/pagesresources__resources#entity-UserSchema)
  - [FileCheckStatusType](https://yandex.ru/support/wiki/ru/api-ref/pagesresources/ru/api-ref/pagesresources/pagesresources__resources#entity-FileCheckStatusType)
  - [AttachmentSchema](https://yandex.ru/support/wiki/ru/api-ref/pagesresources/ru/api-ref/pagesresources/pagesresources__resources#entity-AttachmentSchema)
  - [PageGridsSchema](https://yandex.ru/support/wiki/ru/api-ref/pagesresources/ru/api-ref/pagesresources/pagesresources__resources#entity-PageGridsSchema)
  - [Resource](https://yandex.ru/support/wiki/ru/api-ref/pagesresources/ru/api-ref/pagesresources/pagesresources__resources#entity-Resource)


# Получить информацию о ресурсах страницы




## Request






GET


    
        
```
https://api.wiki.yandex.net/v1/pages/{idx}/resources
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| idx | Type: integer |


### Query parameters



| Name | Description |
| --- | --- |
| cursor | Type: string Example: `` |
| order_by | Type: string Если указано, отсортировать выдачу по полю в направлении direction Enum: name_title, created_at |
| order_direction | All of: OrderDirection OrderDirection Type: string An enumeration. Enum: asc, desc Если указано поле order_by, направление сортировки Default: asc Example: `` |
| page_size | Type: integer Число результатов на странице выдачи. Default: 50 Min value: 1 Max value: 100 |
| q | Type: string Поиск по заголовку Max length: 255 Example: `` |
| types | Type: string Необходимые типы ресурсов, через запятую. Возможные значения: attachment, grid Example: `` |


## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "results": [
    {
      "type": "attachment",
      "item": {
        "id": 0,
        "name": "example",
        "download_url": "example",
        "size": "example",
        "description": "example",
        "user": {},
        "created_at": "2025-01-01T00:00:00Z",
        "mimetype": "example",
        "has_preview": true,
        "check_status": "ready"
      }
    }
  ],
  "next_cursor": "example",
  "prev_cursor": "example"
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| results | Type: Resource[] Example [ { "type": "attachment", "item": { "id": 0, "name": "example", "download_url": "example", "size": "example", "description": "example", "user": { "id": 0, "identity": {}, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" }, "created_at": "2025-01-01T00:00:00Z", "mimetype": "example", "has_preview": true, "check_status": "ready" } } ] |
| next_cursor | Type: string Example: example |
| prev_cursor | Type: string Example: example |




### ResourceType



An enumeration.


**Type**: string


*Enum:* `attachment`, `grid`




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


        
            
            
        
    



### PageGridsSchema



| Name | Description |
| --- | --- |
| created_at | Type: string<date-time> Example: 2025-01-01T00:00:00Z |
| id | Type: string<uuid4> Example: example |
| title | Type: string Example: example |

**Example**
    
        
```
{
  "id": "example",
  "title": "example",
  "created_at": "2025-01-01T00:00:00Z"
}
```


        
            
            
        
    



### Resource



| Name | Description |
| --- | --- |
| item | Any of 2 types AttachmentSchema Type: AttachmentSchema Example { "id": 0, "name": "example", "download_url": "example", "size": "example", "description": "example", "user": { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" }, "created_at": "2025-01-01T00:00:00Z", "mimetype": "example", "has_preview": true, "check_status": "ready" } PageGridsSchema Type: PageGridsSchema Example { "id": "example", "title": "example", "created_at": "2025-01-01T00:00:00Z" } Example { "id": 0, "name": "example", "download_url": "example", "size": "example", "description": "example", "user": { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" }, "created_at": "2025-01-01T00:00:00Z", "mimetype": "example", "has_preview": true, "check_status": "ready" } |
| type | Type: ResourceType An enumeration. Enum: attachment, grid |

**Example**
    
        
```
{
  "type": "attachment",
  "item": {
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
}
```

---

