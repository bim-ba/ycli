# Скачать файл по слагу страницы и имени файла




Скачать файл по слагу страницы, на которую он загружен, и имени файла.


Если страница перемещена (вместе с файлами), выполняется попытка найти новый адрес по редиректам.


## Request






GET


    
        
```
https://api.wiki.yandex.net/v1/pages/attachments/download_by_url
```


        
            
            
        
    




### Query parameters



| Name | Description |
| --- | --- |
| url | Type: string Min length: 1 Pattern: ^(?P<tag>((\.templates\.\d+)&#124;(\w&#124;\-)[\w\-\.:\+]*)(/(\w&#124;\-)[\w\-\.:\+]*)*/?)/.files/(?P<filename>.+)$ Example: `` |
| download | Type: boolean Загрузить файл вместо отображения в браузере вне зависимости от MIME-типа Default: false |


## Responses




## 200 OK



OK

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attachments#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attachments#path-parameters)
  - [Query parameters](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attachments#query-parameters)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attachments#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attachments#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attachments#body)
  - [UserIdentity](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attachments#entity-UserIdentity)
  - [UserSchema](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attachments#entity-UserSchema)
  - [FileCheckStatusType](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attachments#entity-FileCheckStatusType)
  - [AttachmentSchema](https://yandex.ru/support/wiki/ru/api-ref/attachments/ru/api-ref/attachments/pagesattachments__attachments#entity-AttachmentSchema)


