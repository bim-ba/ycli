# API Яндекс Вики — Полная документация

> Источник: https://yandex.ru/support/wiki/ru/api-ref/about

---

# API Яндекс Вики


API Яндекс Вики предназначен для веб-сервисов и приложений, которые работают со страницами в Вики вашей организации от имени пользователя. При выполнении запросов к API действуют те же права доступа, которые есть в Вики у пользователя, от имени которого выполняются запросы. Например, если у пользователя нет прав на редактирование страницы, соответствующие запросы к API будут недоступны.


О том, как получить доступ приложений к API Яндекс Вики, читайте в разделе [Доступ к API](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/access).


Документацию API других сервисов Яндекс 360 для бизнеса можно найти на странице [Справка Яндекс 360 для бизнеса](https://360.yandex.ru/business/help/#dev-block).

---

# Доступ к API


- [Заголовки](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/access#headers)
- [Получить доступ к API по протоколу OAuth](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/access#about_oauth)
- [Получить доступ к API по IAM-токену](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/access#iam-token)

Если администратор организации отключил доступ к API, настроить интеграцию не получится.


При работе с API Яндекс Вики запросы выполняются от имени пользователя. Чтобы выполнять те или иные действия через API, пользователь, от имени которого выполняется запрос, должен иметь соответствующие права в Вики. Например, если у пользователя нет прав на редактирование страницы, соответствующие запросы к API будут недоступны. Подробнее о правах доступа пользователей читайте в разделе [Роли](https://yandex.ru/support/wiki/roles.html).


Для доступа к API Яндекс Вики можно использовать один из способов авторизации:


- По протоколу OAuth 2.0 — используется как в организации Яндекс 360 для бизнеса, так и в Yandex Cloud Organization. Подробнее см. [Получить доступ к API по протоколу OAuth](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/access#about_oauth).
- С помощью IAM-токена — используется только в организации Yandex Cloud. Подробнее см. [Получить доступ к API по IAM-токену](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/access#iam-token).


При авторизации в API Яндекс Вики нельзя использовать [сервисный аккаунт](https://yandex.cloud/ru/docs/iam/concepts/users/service-accounts) Yandex Cloud, отправляйте запросы только с аккаунта пользователя.


## Заголовки



В запросах к API Яндекс Вики указывайте заголовки:


- `Host: api.wiki.yandex.net`
- Заголовок авторизации:


  - `Authorization: OAuth <OAuth-токен>` — при доступе по протоколу OAuth 2.0.
  - `Authorization: Bearer <IAM-токен>` — при доступе с помощью IAM-токена.
- Идентификатор организации:


  - `X-Org-Id` — для организации Яндекс 360 для бизнеса.
  - `X-Cloud-Org-Id` — для организации Yandex Cloud Organization.


Чтобы узнать идентификатор организации, в сервисе [Яндекс Трекер](https://tracker.yandex.ru/admin/orgs) откройте страницу **Администрирование** → [**Организации**](https://tracker.yandex.ru/admin/orgs) и скопируйте значение поля **идентификатор**.


> Пример:
> 
> 
>     
>         
> ```
> Host: api.wiki.yandex.net
> Authorization: OAuth y0__xAbc*********
> X-Org-Id: 1234******
> ```


## Получить доступ к API по протоколу OAuth



Если вы используете федеративный аккаунт, авторизуйтесь с помощью [IAM-токена](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/access#iam-token).


Чтобы получить токен:


1. Перейдите по ссылке [https://oauth.yandex.ru](https://oauth.yandex.ru).
2. На странице **Ваши приложения** нажмите  **Создать**.
3. В открывшемся окне выберите вариант **Для доступа к API или отладки** и нажмите **Перейти к созданию**.
4. Укажите название приложения и почту для связи.
5. Добавьте разрешения для доступа к данным пользователя. Чтобы выбрать разрешение, начните вводить его название в поле **Название доступа**:


  - **Запись в Вики (wiki:write)** — все операции с данными: создание, удаление, редактирование.
  - **Чтение из Вики (wiki:read)** — только чтение данных.
6. Нажмите **Создать приложение**.
7. В личном кабинете [Яндекс OAuth](https://oauth.yandex.ru) выберите созданное ранее приложение и скопируйте его идентификатор из поля **ClientID**.
8. Сформируйте ссылку для запроса токена:


    
        
```
https://oauth.yandex.ru/authorize?response_type=token&client_id=<идентификатор_приложения>
```
9. Войдите в аккаунт, от имени которого вы будете работать с API, и перейдите по сформированной ссылке.


На странице появится последовательность символов — это OAuth-токен. Скопируйте его и сохраните.


Чтобы проверить наличие доступа к API, выполните какой-либо запрос. Если доступ не был получен, запрос вернет ответ с кодом `401 Unauthorized`.


Например, можно выполнить запрос информации о странице `mypage` с помощью curl:



Unix
Windows



    
        
```
curl -X GET 'https://api.wiki.yandex.net/v1/pages?slug=mypage' \
     -H 'Authorization: OAuth y0__xAbc******' \
     -H 'X-Org-Id: 1234******'
```


        
            
            
        
    



    
        
```
curl -X GET "https://api.wiki.yandex.net/v1/pages?slug=mypage" ^
     -H "Authorization: OAuth y0__xAbc******" ^
     -H "X-Org-Id: 1234******"
```


        
            
            
        
    



## Получить доступ к API по IAM-токену



Если вы используете Вики в составе организации Yandex Cloud, для авторизации в API можно использовать IAM-токен.


IAM-токен — уникальная последовательность символов, которая выдается пользователю после прохождения аутентификации. С помощью этого токена пользователь авторизуется в API Яндекс Вики и выполняет операции с ресурсами. Подробнее об этом способе аутентификации читайте в [документации сервиса идентификации и контроля доступа](https://yandex.cloud/ru/docs/iam/concepts/authorization/iam-token).


- [Как получить IAM-токен для аккаунта на Яндексе](https://yandex.cloud/ru/docs/iam/operations/iam-token/create)
- [Как получить IAM-токен для федеративного аккаунта](https://yandex.cloud/ru/docs/iam/operations/iam-token/create-for-federation)


IAM-токен действует не больше 12 часов и ограничен временем жизни cookie у [федерации](https://yandex.cloud/ru/docs/organization/concepts/add-federation). После истечения срока жизни токена вернется ошибка с кодом `401 Unauthorized`.

---

# Wiki Public API



version: 1.0.0


### Формат ошибок



В общем виде сообщение об ошибке представляет собой следующую структуру:


    
        
```
{
    "debug_message": "",
    "details": {},
    "error_code": ""
}
```


        
            
            
        
    

Например:


    
        
```
{
    "debug_message": "Validation failed",
    "details": {
        "body": {
            "data": [
                {
                    "debug_message": "field required",
                    "error_code": "value_error.missing"
                }
            ]
        }
    },
    "error_code": "VALIDATION_ERROR"
}
```


        
            
            
        
    

В первую очередь нужно ориентироваться на error_code. В debug_message представлено текстовое описание ошибки. В detail, при необходимости, будет дополнительная информация (или null, если такой необходимости нет).


#### Формат сообщения в случае ошибки валидации



    
        
```
{
    "debug_message": "Validation failed",
    "details": {
        "<source>": {
            "<field>": [
                {
                    "debug_message": "<validation debug message>",
                    "error_code": "<validation error code>"
                }
            ]
        }
    },
    "error_code": "VALIDATION_ERROR"
}
```


        
            
            
        
    

`<source>` — источник данных в котором произошла ошибка валидации, возможные значения `[body, query]`


`<field>` — имя поля, не прошедшее валидацию, значением является список, в котором хранятся локальные debug_message и error_code с деталями об ошибке.


## Sections



- [Страницы](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/pages/)
- [Прикрепленные файлы](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/attachments/)
- [Ресурсы страниц](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/pagesresources/)
- [Комментарии](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/comments/)
- [Динамические таблицы](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/grids/)
- [Пользователи](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/users/)
- [Сессии загрузки](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/upload_sessions/)
- [Операции](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/Operacii/)
- [Восстановление страниц](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/recovery_tokens/)

---

