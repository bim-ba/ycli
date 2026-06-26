# Создать сессию загрузки файла




Создает сессию для загрузки файла. Порядок загрузки файла:


1. Создать сессию загрузки файла.
2. Загрузить файл по частям с помощью метода [Загрузить фрагмент файла](https://yandex.ru/support/wiki/ru/api-ref/upload_sessions/ru/api-ref/upload_sessions/upload_sessions__upload_part).
3. Завершить сессию загрузки c помощью метода [Завершить сессию загрузки](https://yandex.ru/support/wiki/ru/api-ref/upload_sessions/ru/api-ref/upload_sessions/upload_sessions__complete_multipart_upload).


После завершения загрузки файл можно прикрепить к странице: [Добавить прикрепленный файл](https://yandex.ru/support/wiki/ru/api-ref/upload_sessions/ru/api-ref/attachments/pagesattachments__attach_file).


## Request






POST


    
        
```
https://api.wiki.yandex.net/v1/upload_sessions
```


        
            
            
        
    





### Body


application/json
    
        
```
{
  "file_name": "example",
  "file_size": 0
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| file_name | Type: string Example: example |
| file_size | Type: integer |



## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "session_id": "example",
  "file_name": "example",
  "file_size": 0,
  "status": "not_started",
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
  "finished_at": "2025-01-01T00:00:00Z",
  "storage_type": "mds"
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| created_at | Type: string<date-time> Example: 2025-01-01T00:00:00Z |
| file_name | Type: string Example: example |
| file_size | Type: integer |
| session_id | Type: string<uuid4> Example: example |
| status | Type: UploadSessionStatusType An enumeration. Enum: not_started, in_progress, finished, aborted, used, cleanup |
| user | Type: UserSchema Example { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" } |
| finished_at | Type: string<date-time> Example: 2025-01-01T00:00:00Z |
| storage_type | Type: StorageType An enumeration. Enum: mds, s3, custom_s3 |




### UploadSessionStatusType



An enumeration.


**Type**: string


*Enum:* `not_started`, `in_progress`, `finished`, `aborted`, `used`, `cleanup`




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


        
            
            
        
    



### StorageType



An enumeration.


**Type**: string


*Enum:* `mds`, `s3`, `custom_s3`

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/upload_sessions/ru/api-ref/upload_sessions/upload_sessions__abort_all#request)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/upload_sessions/ru/api-ref/upload_sessions/upload_sessions__abort_all#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/upload_sessions/ru/api-ref/upload_sessions/upload_sessions__abort_all#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/upload_sessions/ru/api-ref/upload_sessions/upload_sessions__abort_all#body)


