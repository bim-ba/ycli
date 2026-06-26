---
source: https://yandex.ru/support/tracker/ru/user/API
title: "Инструменты разработчика |"
word_count: 284
token_estimate: 811
extracted: "2026-05-13T11:26:03Z"
mode: quality
---

# API Яндекс Трекера

Управляйте вашими задачами в Трекере с помощью HTTP-запросов к [REST API Яндекс Трекера](https://yandex.ru/support/tracker/ru/api-ref/about-api).

API Яндекс Трекера предназначено для веб-сервисов и приложений, которые работают с задачами вашей организации от имени пользователя. При этом возможности API зависят от прав доступа пользователя, от имени которого выполняются запросы.

С помощью API Яндекс Трекера вы можете:

- интегрировать Трекер с другими сервисами — например, управлять задачами с помощью чат-бота или связать Трекер с CRM-системой;
- автоматизировать процессы, связанные с созданием, массовым изменением и поиском задач по параметрам;
- задавать специфические правила обработки определенных действий — например, обновлять статус задачи по таймеру;
- создавать браузерные расширения для работы с Трекером.

Подробнее о работе с API Яндекс Трекера читайте в [Справочнике](https://yandex.ru/support/tracker/ru/api-ref/about-api).

Попробуйте наш [Python-клиент](https://yandex.ru/support/tracker/ru/user/API#python) для работы с API Яндекс Трекера. Так вам будет проще начать использовать API в своих приложениях.

# Python-клиент

Чтобы вам было проще начать пользоваться [API Яндекс Трекера](https://yandex.ru/support/tracker/ru/api-ref/about-api), мы подготовили [yandex\_tracker\_client](https://github.com/yandex/yandex_tracker_client) — пакет, позволяющий легко добавлять вызовы API в программы, написанные на языке Python.

Чтобы начать пользоваться клиентом:

1. Скачайте и установите на свой компьютер актуальную версию Python с сайта [https://www.python.org/downloads/](https://www.python.org/downloads/).

2. В командной строке вашей ОС выполните команду:

    ```
    pip install yandex_tracker_client
    ```

3. Получите OAuth-токен и идентификатор организации для доступа к API. Как это сделать, читайте в [Справочнике API](https://yandex.ru/support/tracker/ru/api-ref/access).

4. Инициализируйте клиент в коде вашей программы:

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

В клиенте используйте такой же формат данных, как в [API Яндекс Трекера](https://yandex.ru/support/tracker/ru/api-ref/common-format).

Подробнее о работе клиента и условиях использования читайте на его странице в GitHub: [https://github.com/yandex/yandex\_tracker\_client](https://github.com/yandex/yandex_tracker_client).
