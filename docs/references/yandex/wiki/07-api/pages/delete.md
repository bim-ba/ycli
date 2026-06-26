# Удалить страницу




Удаление страницы.


Ответ содержит параметр `recovery_token`, который можно использовать для восстановления страницы с помощью метода [Восстановить страницу по токену](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/recovery_tokens/recovery_tokens__recover_page_by_token).


## Request






DELETE


    
        
```
https://api.wiki.yandex.net/v1/pages/{idx}
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| idx | Type: integer |


## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "recovery_token": "example"
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| recovery_token | Type: string<uuid4> Example: example |

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__clone_page#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__clone_page#path-parameters)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__clone_page#body)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__clone_page#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__clone_page#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__clone_page#body1)
  - [B2BOperationType](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__clone_page#entity-B2BOperationType)
  - [B2BOperationIdentity](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__clone_page#entity-B2BOperationIdentity)


