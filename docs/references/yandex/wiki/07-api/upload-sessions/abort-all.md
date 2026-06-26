# Прервать все сессии загрузки




Отменить все активные сессии загрузки файлов пользователя, чтобы освободить квоту


## Request






POST


    
        
```
https://api.wiki.yandex.net/v1/upload_sessions/abort_active_uploads
```


        
            
            
        
    




## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "status": "ok"
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| status | Type: string Default: ok |

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/upload_sessions/ru/api-ref/upload_sessions/upload_sessions__get_upload_session#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/upload_sessions/ru/api-ref/upload_sessions/upload_sessions__get_upload_session#path-parameters)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/upload_sessions/ru/api-ref/upload_sessions/upload_sessions__get_upload_session#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/upload_sessions/ru/api-ref/upload_sessions/upload_sessions__get_upload_session#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/upload_sessions/ru/api-ref/upload_sessions/upload_sessions__get_upload_session#body)
  - [UploadSessionStatusType](https://yandex.ru/support/wiki/ru/api-ref/upload_sessions/ru/api-ref/upload_sessions/upload_sessions__get_upload_session#entity-UploadSessionStatusType)
  - [UserIdentity](https://yandex.ru/support/wiki/ru/api-ref/upload_sessions/ru/api-ref/upload_sessions/upload_sessions__get_upload_session#entity-UserIdentity)
  - [UserSchema](https://yandex.ru/support/wiki/ru/api-ref/upload_sessions/ru/api-ref/upload_sessions/upload_sessions__get_upload_session#entity-UserSchema)
  - [StorageType](https://yandex.ru/support/wiki/ru/api-ref/upload_sessions/ru/api-ref/upload_sessions/upload_sessions__get_upload_session#entity-StorageType)


