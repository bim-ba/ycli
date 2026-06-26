# API Яндекс Трекера — Полная документация

Источник: https://yandex.ru/support/tracker/ru/api-ref/about-api

---

# API Яндекс Трекера

Вы можете управлять Трекером с помощью HTTP-запросов к REST API.

API Яндекс Трекера предназначен для веб-сервисов и приложений, которые работают с задачами в Трекере вашей организации от имени пользователя. При этом возможность выполнять те или иные действия через API зависит от прав доступа пользователя, от имени которого выполняются запросы.

API Яндекс Трекера позволяет:

- искать, создавать и редактировать задачи;
- создавать и редактировать доски задач;
- просматривать настройки очереди;
- добавлять и редактировать поля задач.

Перед тем как начать работу с API Яндекс Трекера, ознакомьтесь с [общим форматом запросов](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/common-format).

О том, как получить доступ приложений к API Яндекс Трекера, читайте в разделе [Доступ к API](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/access).

Документацию API других сервисов Яндекс 360 для бизнеса можно найти на странице [Справка Яндекс 360 для бизнеса](https://360.yandex.ru/business/help/#dev-block).

---

# Доступ к API

- [Получить доступ к API по протоколу OAuth 2.0](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/access#about_OAuth)
- [Получить доступ к API по IAM-токену](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/access#iam-token)
- [Как использовать Python-клиент](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/access#about-python-client)

При работе с API Яндекс Трекера запросы выполняются от имени пользователя Трекера. Чтобы выполнять те или иные действия через API, пользователь, от имени которого выполняется запрос, должен иметь соответствующие права в Трекере. Например, если у пользователя нет прав на изменение настроек очереди, соответствующие запросы к API будут недоступны. Подробнее о правах доступа пользователей читайте в разделе [Роли и права доступа](https://yandex.ru/support/tracker/role-model.html).

Для доступа к API Яндекс Трекера можно использовать один из способов авторизации:

- По протоколу OAuth 2.0. Используется как в организациях Яндекс 360, так и в организациях Yandex Cloud. В этом случае в запросах к API Трекера указывайте заголовок:

`Authorization: OAuth <OAuth-токен>`

Подробнее в разделе [Получить доступ к API по протоколу OAuth 2.0](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/access#about_OAuth).

- С помощью IAM-токена. Доступен только в организациях Yandex Cloud, в том числе с использованием [сервисных аккаунтов](https://yandex.cloud/ru/docs/iam/concepts/users/service-accounts). В этом случае в запросах к API Трекера указывайте заголовок:

`Authorization: Bearer <IAM-токен>`

Подробнее в разделе [Получить доступ к API по IAM-токену](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/access#iam-token).

Помимо токена, в заголовках запроса нужно указать идентификатор вашей организации. Формат заголовков описан в разделе [Заголовки](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/common-format#headings).

Если вы используете для вызова API Python-клиент, укажите данные для авторизации при инициализации клиента: [Как использовать Python-клиент](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/access#about-python-client).

## Получить доступ к API по протоколу OAuth 2.0

Если вы используете федеративный или сервисный аккаунт, авторизуйтесь с помощью [IAM-токена](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/access#iam-token).

Чтобы получить токен:

1. Перейдите по ссылке [https://oauth.yandex.ru](https://oauth.yandex.ru).
2. На странице **Ваши приложения** нажмите  **Создать**.
3. В открывшемся окне выберите вариант **Для доступа к API или отладки** и нажмите **Перейти к созданию**.
4. Укажите название приложения и почту для связи.
5. Добавьте разрешения для доступа к данным пользователя. Чтобы выбрать разрешение, начните вводить его название в поле **Название доступа**:

- **Запись в трекер (tracker:write)** — все операции с данными: создание, удаление, редактирование.
- **Чтение из трекера (tracker:read)** — только чтение данных.

6. Нажмите **Создать приложение**.
7. В личном кабинете [Яндекс OAuth](https://oauth.yandex.ru) выберите созданное ранее приложение и скопируйте его идентификатор из поля **ClientID**.
8. Сформируйте ссылку для запроса токена:

```
https://oauth.yandex.ru/authorize?response_type=token&client_id=<идентификатор_приложения>
```

9. Войдите в аккаунт, от имени которого вы будете работать с API, и перейдите по сформированной ссылке.

На странице появится последовательность символов — это OAuth-токен. Скопируйте его и сохраните.

Чтобы проверить наличие доступа к API, выполните [запрос информации о текущем пользователе](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/users/get-user-info). Если доступ не был получен, запрос вернет ответ с кодом `401 Unauthorized`.

Пример запроса информации о текущем пользователе с помощью curl:

Unix
Windows

```
curl -X GET 'https://api.tracker.yandex.net/v3/myself' \
     -H 'Authorization: OAuth y0__xAbc******' \
     -H 'X-Org-ID: 1234******'
```

```
curl -X GET "https://api.tracker.yandex.net/v3/myself" ^
     -H "Authorization: OAuth y0__xAbc******" ^
     -H "X-Org-ID: 1234******"
```

## Получить доступ к API по IAM-токену

Если вы используете Трекер в составе организации Yandex Cloud, для авторизации в API можно использовать IAM-токен.

IAM-токен — уникальная последовательность символов, которая выдается пользователю после прохождения аутентификации. С помощью этого токена пользователь авторизуется в API Яндекс Трекера и выполняет операции с ресурсами.

Чтобы отправлять запросы к API Трекера от имени сервисного аккаунта, сначала обратитесь в [службу поддержки](https://yandex.ru/support/tracker/ru/api-ref/ru/feedback) с указанием id облачной организации и id сервисного аккаунта. В противном случае запросы к API будут завершаться ошибкой с кодом `401 Unauthorized`.

Подробнее об этом способе аутентификации читайте в [документации сервиса идентификации и контроля доступа](https://yandex.cloud/ru/docs/iam/concepts/authorization/iam-token).

- [Как получить IAM-токен для аккаунта на Яндексе](https://yandex.cloud/ru/docs/iam/operations/iam-token/create)
- [Как получить IAM-токен для сервисного аккаунта](https://yandex.cloud/ru/docs/iam/operations/iam-token/create-for-sa)
- [Как получить IAM-токен для федеративного аккаунта](https://yandex.cloud/ru/docs/iam/operations/iam-token/create-for-federation)

IAM-токен действует не больше 12 часов и ограничен временем жизни cookie у [федерации](https://yandex.cloud/ru/docs/organization/concepts/add-federation). После истечения срока жизни токена вернется ошибка с кодом `401 Unauthorized`.

## Как использовать Python-клиент

При разработке приложений на языке Python вы можете использовать пакет [yandex_tracker_client](https://github.com/yandex/yandex_tracker_client) — клиент, который облегчает работу с API Трекера.

Чтобы начать пользоваться клиентом:

1. Скачайте и установите на свой компьютер актуальную версию Python с сайта [https://www.python.org/downloads/](https://www.python.org/downloads/).
2. В командной строке вашей ОС выполните команду:

```
pip install yandex_tracker_client
```

3. Получите [OAuth-токен](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/access#about_OAuth) или [IAM-токен](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/access#iam-token) для авторизации.
4. Узнайте идентификатор вашей организации.

Чтобы узнать идентификатор организации, перейдите на страницу **Администрирование** → [**Организации**](https://tracker.yandex.ru/admin/orgs) и скопируйте значение поля **идентификатор**.
5. Инициализируйте клиент в коде вашей программы:

В организации Яндекс 360 для бизнеса
В организации Yandex Cloud

```
from yandex_tracker_client import TrackerClient
client = TrackerClient(token='<OAuth-токен>', org_id='<идентификатор_организации>')
```

```
from yandex_tracker_client import TrackerClient
client = TrackerClient(token='<OAuth-токен>', cloud_org_id='<идентификатор_организации>')
```

Здесь `<OAuth-токен>` — ваш OAuth-токен, а `<идентификатор_организации>` — идентификатор организации.

В клиенте используйте такой же формат данных, как в API Яндекс Трекера.

Подробнее о работе клиента и условиях использования читайте на его странице в GitHub: [https://github.com/yandex/yandex_tracker_client](https://github.com/yandex/yandex_tracker_client).

---

# Общий формат запросов

- [Методы](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/common-format#methods)
- [Ресурс](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/common-format#resource)
- [Заголовки](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/common-format#headings)
- [Формат тела запроса](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/common-format#body)
  - [Редактирование параметров](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/common-format#edit-fields)
  - [Формат текста и переменные](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/common-format#text-format)
  - [Использование специальных символов](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/common-format#str-escape)
- [Постраничное отображение результатов](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/common-format#displaying-results)
- [Примеры запросов](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/common-format#examples)

Общий вид запросов к API Яндекс Трекера:

```
<метод> https://api.tracker.yandex.net/v3/<тип_ресурса>/<идентификатор_ресурса>/?<параметр>=<значение>
```

Структура запроса

```
<метод> /v3/<тип_ресурса>/<идентификатор_ресурса>/?<параметр>=<значение>
Host: api.tracker.yandex.net
Content-Type: application/json
Authorization: OAuth <OAuth-токен>
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>

{
   Тело запроса в формате JSON
}
```

Python

```
import requests;

def my_function():
    session = requests.Session()
    url = "https://api.tracker.yandex.net/v3/<resources>/<resource_id>/?<param>=<value>"
    json = {
        # Тело запроса в формате JSON
    }
    head =  {
        "Authorization": "OAuth <OAuth-токен>",
        "X-Org-ID": <идентификатор_организации>
    }
    session.headers.update(head)
    response = session.post(url, json=json) # session.* - get, post, path, delete
    data = response.json()
    print(response)
    print(data)

my_function()
```

API Яндекс Трекера передает и получает параметры даты и времени в часовом поясе UTC±00:00. Поэтому полученные время и дата могут отличаться от часового пояса клиента, с которого выполняется запрос.

## Методы

Запросы к API Трекера используют один из HTTP-методов:

`GET` — получить информацию об объекте или списке объектов;

`POST` — создать объект;

`PATCH` — изменить параметры существующего объекта. Запросы, выполненные с помощью метода PATCH изменяют только те параметры, которые явно указаны в теле запроса;

`DELETE` — удалить объект.

## Ресурс

Адрес ресурса в запросе содержит версию API Яндекс Трекера:

- `v3` — текущая версия, в которой доступны все обновления методов API. Рекомендуется использовать эту версию для всех запросов к API.
- `v2` — предыдущая версия. В запросах можно использовать версию `v2`, при этом могут быть недоступны новые методы API и параметры объектов Трекера.

## Заголовки

В запросах к API Трекера указывайте заголовки:

- `Host: api.tracker.yandex.net`
- `Authorization: OAuth <OAuth-токен>` — при доступе по протоколу OAuth 2.0. Подробнее в разделе [Получить доступ к API по протоколу OAuth 2.0](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/access#about_OAuth).

`Authorization: Bearer <IAM-токен>` — при доступе при помощи IAM-токена. Подробнее в разделе [Получить доступ к API по IAM-токену](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/access#iam-token).

Например: `Authorization: Bearer t1.ab123cd45*****************`.

- `X-Org-ID` или `X-Cloud-Org-ID`: идентификатор организации.

  - если к Трекеру привязана организация Яндекс 360 для бизнеса, используйте заголовок `X-Org-ID`,
  - если к Трекеру привязана организация Yandex Cloud Organization, используйте заголовок `X-Cloud-Org-ID`.

Чтобы узнать идентификатор организации, перейдите на страницу **Администрирование** → [**Организации**](https://tracker.yandex.ru/admin/orgs) и скопируйте значение поля **идентификатор**.

Например: `X-Org-ID: 1234***`.

- `Content-Type`: формат тела запроса.

  - `application/json` — текст или данные;
  - `multipart/form-data` — файлы.
- `Accept-Language: <тег языка>` — язык локализации.

По умолчанию HTTP-запрос возвращает локализованные поля на русском языке. Чтобы получить значения локализованных полей на английском языке, укажите заголовок с тегом **en**.

## Формат тела запроса

В теле запроса передается JSON-объект с идентификаторами изменяемых параметров задач (или других объектов) и их значениями. [Что такое формат JSON](https://ru.wikipedia.org/wiki/JSON)

### Редактирование параметров

- Чтобы добавить или удалить значение из массива, используйте команды `add` и `remove`:

```
{
    "followers": { "add": ["<идентификатор_сотрудника_1>", "<идентификатор_сотрудника_2>"] }
}
```

- Чтобы перезаписать массив (удалить старые значения и добавить новые), используйте команду `set`. Чтобы обнулить массив, используйте пустой массив `[]`.
- Отдельные значения в массиве можно изменить с помощью команд `target` и `replacement`:

```
{
  "followers": {
    "replace": [
        {"target": "<идентификатор_1>", "replacement": "<идентификатор_2>"},
        {"target": "<идентификатор_3>", "replacement": "<идентификатор_4>"}]
  }
}
```

- Чтобы обнулить значение поля, укажите значение `null`.

```
{"followers": null}
```

- Для обращения к стандартным объектам Трекера, например, статусам или типам задач, можно использовать их идентификаторы, ключи или отображаемые названия. Например, чтобы изменить тип задачи на «Ошибка», используйте один из способов:

  - ```

{"type": 1}

```
  - ```
{"type": "bug"}
```

- ```

{
    "type": { "id": "1" }
}

```
  - ```
{
    "type": { "name": "Ошибка" }
}
```

- ```

{
    "type": {"set": "bug"}
}

```


### Формат текста и переменные



При работе с запросами на создание или редактирование описания [задачи](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/issues/create-issue), [комментариев](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/issues/add-comment), [макросов](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/post-macros), [триггеров](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/queues/create-trigger) и [автодействий](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/queues/create-autoaction) используйте специальный формат для текста сообщения:


- Чтобы отформатировать текст, используйте [разметку Yandex Flavored Markdown](https://yandex.ru/support/tracker/user/markup.html).
- Чтобы добавить перенос строки, используйте символ `\n`.
- Чтобы добавить значения из полей задачи, используйте переменные. Например:


  - `{{issue.<ключ_параметра>}}` — параметр задачи, значение которого будет подставлено вместо переменной. Полный список параметров задачи: [https://tracker.yandex.ru/admin/fields](https://tracker.yandex.ru/admin/fields).
  - `{{currentUser}}` — имя текущего пользователя, например при запуске макроса.
  - `{{currentDateTime.date}}` — текущая дата.
  - `{{currentDateTime}}` — текущие дата и время.


Подробнее читайте в разделе [Переменные](https://yandex.ru/support/tracker/user/vars.html).


### Использование специальных символов



При передаче параметров строкового типа учитывайте особенности работы со специальными символами:


- Символы `"`, `\`, `/` необходимо экранировать с помощью обратного слеша `\`.
- Для переноса строки используйте символы `\n` или `\r`.
- Символы в кодировке Unicode можно вставить в формате `\uFFFF`.


Например, в тексте описания задачи могут встречаться двойные кавычки или символы переноса строки:




```

{
  "description": "Внесите исправления:\n1. Используйте значение \"1\" вместо значения \"2\"."
}

```








## Постраничное отображение результатов



Если вы запрашиваете список объектов, и количество строк в ответе больше 50, в ответе возвращается страница с указанным количеством результатов. Вы можете выполнить несколько запросов для просмотра последующих страниц. Для этого используется механизм постраничного отображения результатов.


При постраничном отображении результаты запроса рассчитываются каждый раз при отображении новой страницы. Если за время просмотра одной страницы в результатах запроса произошли изменения, это может повлиять на отображение следующих страниц. Например, по запросу найдено 11 задач, из которых отображено 10. В процессе просмотра результатов первой страницы одна из задач была изменена и перестала отвечать требованиям поискового запроса. В этом случае, при запросе второй страницы результатов будет возвращен пустой массив, так как оставшиеся 10 задач будут находиться на первой странице.


В новом API проектов, портфелей и целей ([Проекты, портфели и цели](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/entities/about-entities)) доступно постраничное отображение результатов запроса для событий и комментариев с более гибкими настройками:


- [Получить историю событий сущности](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/entities/get-events-relative)
- [Получить комментарии к сущности](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/entities/comments/get-all-comments)


Для постраничного отображения результатов используйте в запросе следующие параметры:


- **perPage (необязательный)**


Количество объектов (задач, очередей и пр.) на странице. Значение по умолчанию — 50.
- **page (необязательный)**


Номер страницы ответа. Значение по умолчанию — 1.


В ответе будут содержаться следующие заголовки:


- **X-Total-Pages**


Общее количество страниц с записями.
- **X-Total-Count**


Общее число записей в ответе.


## Примеры запросов


Пример 1: Изменить название, описание, тип и приоритет задачи.
- Используется HTTP-метод PATCH.
- Редактируется задача TEST-1.
- Новый тип задачи: «Ошибка».
- Новый приоритет задачи: «Низкий».



PATCH


```

https://api.tracker.yandex.net/v3/issues/TEST-1

```





Формат запроса
Python





```

PATCH /v3/issues/TEST-1
Host: api.tracker.yandex.net
Content-Type: application/json
Authorization: OAuth <OAuth-токен>
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>
{
  "summary": "<новое_название_задачи>",
  "description": "<новое_описание_задачи>",
  "type": {
      "id": "1",
      "key": "bug"
      },
  "priority": {
      "id": "2",
      "key": "minor"
      }
}

```












```

import requests;

def my_function():
    session = requests.Session()
    url = "https://api.tracker.yandex.net/v3/issues/TEST-1"
    json = {
        "summary": "<новое_название_задачи>",
        "description": "<новое_описание_задачи>",
        "type": {
            "id": "1",
            "key": "bug"
            },
        "priority": {
            "id": "2",
            "key": "minor"
            }
        }
    head =  {
        "Authorization": "OAuth <OAuth-токен>",
        "X-Org-ID": <идентификатор_организации>
    }
    session.headers.update(head)
    response = session.patch(url, json=json)
    data = response.json()
    print(response)
    print(data)

my_function()

```









Пример 2: Запрос одной задачи с указанием необходимых полей.
- Используется HTTP-метод GET.
- В ответе включено отображение приложений.



GET


```

https://api.tracker.yandex.net/v3/issues/JUNE-3?expand=attachments

```





Формат запроса
Python





```

GET /v3/issues/JUNE-3?expand=attachments
Host: api.tracker.yandex.net
Authorization: OAuth <OAuth-токен>
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>

```












```

import requests;

def my_function():
    session = requests.Session()
    url = "https://api.tracker.yandex.net/v3/issues/JUNE-3?expand=attachments"
    head =  {
        "Authorization": "OAuth <токен>",
        "X-Org-ID": <идентификатор_организации>
    }
    session.headers.update(head)
    response = session.get(url)
    data = response.json()
    print(response)
    print(data)

my_function()

```









Пример 3: Создать задачу.
- Используется HTTP-метод POST.
- Создается задача с названием «Test Issue» в очереди с *ключом* «TREK».
- Новая задача — подзадача «JUNE-2».
- Тип создаваемой задачи – «Ошибка».
- Исполнитель задачи – <логин_пользователя>



POST


```

https://api.tracker.yandex.net/v3/issues/

```





Формат запроса
Python





```

POST /v3/issues/
Host: api.tracker.yandex.net
Content-Type: application/json
Authorization: OAuth <OAuth-токен>
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>
{
  "queue": "TREK",
  "summary": "Test Issue",
  "parent":"JUNE-2",
  "type": "bug",
  "assignee": "<user_login>",
  "attachmentIds": [55, 56]
}

```












```

import requests;

def my_function():
    session = requests.Session()
    url = "https://api.tracker.yandex.net/v3/issues/"
    json = {
        "queue": "TREK",
        "summary": "Test Issue",
        "parent":"JUNE-2",
        "type": "bug",
        "assignee": "<user_login>",
        "attachmentIds": [55, 56]
        }
    head =  {
        "Authorization": "OAuth <токен>",
        "X-Org-ID": <идентификатор_организации>
    }
    session.headers.update(head)
    response = session.post(url, json=json)
    data = response.json()
    print(response)
    print(data)

my_function()

```









Пример 4: Найти задачи очереди, которые назначены на заданного сотрудника. Результаты отобразить постранично.
- Используется HTTP-метод POST.
- Ключ очереди – «TREK».
- Исполнитель задачи – <логин_пользователя>.



POST


```

https://api.tracker.yandex.net/v3/issues/_search?perPage=15

```





Формат запроса
Python





```

POST /v3/issues/_search?perPage=15
Host: api.tracker.yandex.net
Content-Type: application/json
Authorization: OAuth <OAuth-токен>
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>
{
  "filter": {
    "queue": "TREK",
    "assignee": "<user_login>"
  }
}

```












```

import requests;

def my_function():
    session = requests.Session()
    url = "https://api.tracker.yandex.net/v3/issues/_search?perPage=15"
    json = {
        "filter": {
            "queue": "TREK",
            "assignee": "<user_login>"
            }
        }
    head =  {
        "Authorization": "OAuth <токен>",
        "X-Org-ID": <идентификатор_организации>
    }
    session.headers.update(head)
    response = session.post(url, json=json)
    data = response.json()
    print(response)
    print(data)

my_function()

```










Ключ очереди — это уникальный код из латинских букв, по которому можно идентифицировать очередь, например: `TEST`. С помощью ключа можно перейти к очереди по ссылке: `https://tracker.yandex.ru/TEST`.

---

# Параметры задач в запросах к API и ответах


При работе с задачами через API вы можете использовать различные параметры для создания, редактирования и получения информации о задачах.


В этой документации описаны стандартные параметры задачи, которые доступны в Трекере по умолчанию, а также стандартные объекты, которые могут содержаться в задаче:


- [Параметры задачи в запросах к API](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/request-fields)
- [Параметры задачи в ответах на запросы](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/response-fields)


Помимо стандартных параметров, задачи могут содержать:


- Пользовательские глобальные поля, созданные в организации.
- Локальные поля, специфичные для конкретной очереди.


### Глобальные поля



Глобальные поля можно использовать в задачах во всех очередях Трекера. По умолчанию в Трекере доступны самые популярные поля задач.


Дополнительные глобальные поля  может создать администратор организации. [Как добавить в Трекер глобальное поле](https://yandex.ru/support/tracker/user/create-param.html#global-field).


Список всех глобальных полей можно посмотреть на странице [Настройки Трекера](https://tracker.yandex.ru/admin/fields).


### Локальные поля



Локальное поле можно использовать только в задачах той очереди, к которой оно привязано. Преимущество локальных полей в том, что владелец очереди может управлять такими полями без риска повлиять на процессы работы в других очередях. Пользователи, которые работают в других очередях, не будут видеть это поле в своих задачах.


Как использовать локальные поля, читайте в разделе [Локальные поля задач](https://yandex.ru/support/tracker/local-fields.html).


При работе с локальными полями через API обратите внимание, что идентификатор локального поля включает шестнадцатеричный префикс и ключ поля: `603fb94c38bbe658********--myfield`.


Например, чтобы изменить значение локального поля задачи через API, в теле HTTP-запроса на редактирование задачи укажите идентификатор поля: `603fb94c38bbe658********--<ключ_поля>: "<новое_значение_локального_поля>"`. [Как редактировать задачу с помощью API](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/patch-issue)


Чтобы узнать идентификатор локального поля, используйте запрос [Получить список локальных полей очереди](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/queues/get-local-fields).

---

# Возможные коды ответа


200
Запрос выполнен успешно.
201
В результате выполнения запроса с методом `POST` успешно создан новый объект.
204
Запрос с методом DELETE успешно выполнен, объект удален.


400
Один или несколько параметров запроса имеют недопустимое значение.


401
Пользователь не авторизован. Проверьте, были ли выполнены действия, описанные в разделе [Доступ к API](https://yandex.ru/support/tracker/ru/api-ref/ru/api-ref/access).


403
У вас не хватает прав на выполнение этого действия. Наличие прав можно перепроверить в интерфейсе Трекера — для выполнения действия при помощи API и через интерфейс требуются одинаковые права.


404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.


409
При редактировании объекта возник конфликт. Возможно, ошибка возникла из-за неправильно указанной версии изменений.


412
При редактировании объекта возник конфликт. Возможно, ошибка возникла из-за неправильно указанной версии изменений.


422
Ошибка валидации JSON, запрос отклонен.


423
Редактирование объекта заблокировано. Возможно, превышено допустимое значение параметра `version` — количество обновлений объекта. Максимальное значение версии составляет `10100` для роботов и `11100` для пользователей.


428
Доступ к ресурсу отклонен. Проверьте, указаны ли все обязательные условия выполнения запроса.


429
Превышено допустимое количество запросов к хосту в единицу времени. Попробуйте повторить запрос позже.

---
