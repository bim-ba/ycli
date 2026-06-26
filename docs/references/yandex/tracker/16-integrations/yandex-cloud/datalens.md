---
source: https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens
title: "Визуализация данных из Трекера"
word_count: 1272
token_estimate: 4339
extracted: "2026-05-13T11:23:53Z"
mode: quality
---

Визуализация данных из Трекера в DataLens позволяет построить более сложную аналитику, чем это возможно средствами самого Трекера.

Для визуализации данных из Трекера в DataLens необходимо:

- организовать регулярный экспорт данных во внешнее хранилище;
- визуализировать необходимые метрики и данные с помощью DataLens.

Для визуализации данных выполните следующие шаги:

1. [Подготовьте облако к работе](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#before-you-begin)
2. [Создайте БД для хранения данных Трекера](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#database-create)
3. [Получите OAuth-токен для доступа к Трекеру](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#oauth-token)
4. [Создайте функцию Cloud Functions для импорта данных](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#function-import)
5. [Создайте подключение к DataLens](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#connection-create)
6. [Создайте датасет](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#dataset-create)
7. [Создайте чарт](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#chart-create)
8. [Создайте дашборд в DataLens и добавьте на него чарты](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#dashboard-create)

# Перед началом работы

Для получения данных необходимо [авторизоваться в Трекере](https://yandex.ru/support/tracker/ru/user/login) с учетной записью пользователя, который имеет полный доступ к сервису.

Зарегистрируйтесь в Yandex Cloud и создайте платежный аккаунт:

1. Перейдите в [консоль управления](https://console.cloud.yandex.ru/), затем войдите в Yandex Cloud или зарегистрируйтесь.
2. На странице **[Биллинг](https://billing.cloud.yandex.ru/)** убедитесь, что у вас подключен [платежный аккаунт](https://yandex.cloud/ru/docs/billing/concepts/billing-account), и он находится в статусе `ACTIVE` или `TRIAL_ACTIVE`. Если платежного аккаунта нет, [создайте его](https://yandex.cloud/ru/docs/billing/quickstart).

Если у вас есть активный платежный аккаунт, вы можете создать или выбрать каталог, в котором будет работать ваша инфраструктура, на [странице облака](https://console.yandex.cloud/cloud).

[Подробнее об облаках и каталогах](https://yandex.cloud/ru/docs/resource-manager/concepts/resources-hierarchy).

## Необходимые платные ресурсы

- Оплаченный [тариф](https://yandex.ru/support/tracker/ru/enable-tracker) для полного доступа к Трекеру.
- Постоянно запущенный кластер Managed Service for ClickHouse® (см. [тарифы Managed Service for ClickHouse®](https://yandex.cloud/ru/docs/managed-clickhouse/pricing.md));
- Использование функции Cloud Functions (см. [тарифы Cloud Functions](https://yandex.cloud/ru/docs/functions/pricing)).

Если созданные ресурсы вам больше не нужны, [удалите их](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#clear-out).

# Создайте БД для хранения данных Трекера

1. Перейдите в [консоль управления](https://console.cloud.yandex.ru/).
2. В левом верхнем углу нажмите кнопку  **Все сервисы**.
3. Выберите **Платформа данных** → **Managed Service for ClickHouse**.
4. Нажмите кнопку **Создать кластер ClickHouse**.
5. Укажите параметры кластера:
    - Базовые параметры:
        - **Окружение** — `PRODUCTION`;
        - **Версия** — `24.8 LTS`;
    - Ресурсы:
        - **Платформа** — `Intel Ice Lake`;
        - **Тип** — `standart`;
        - **Класс хоста** — `s3-c2-m8 (2 vCPU, 8 ГБ)`;
    - Размер хранилища — `30 ГБ`;
    - Хосты:
        - **Публичный доступ** — `Включено`;
    - Настройки СУБД:
        - **Управление пользователями через SQL** — `Выключено`;
        - **Управление базами данных через SQL** — `Выключено`;
        - **Имя пользователя** — `tracker_data`;
        - **Имя БД** — `db1`;
    - Сервисные настройки:
        - **Доступ из DataLens** — `Включено`;
        - **Доступ из Serverless** — `Включено`.
            Полный список настроек см. в разделе [Настройки Managed Service for ClickHouse®](https://yandex.cloud/ru/docs/managed-clickhouse/concepts/settings-list).
6. Нажмите кнопку **Создать кластер**. Дождитесь, когда статус созданного кластера сменится на `Alive`.
7. Скопируйте и сохраните имя хоста для дальнейшей настройки Cloud Functions.

![Вкладка Хосты](https://yandex.ru/support/tracker/docs-assets/support-tracker/rev/r19613496/ru/_assets/dl-tracker-host-name.png)

# Получите OAuth-токен для доступа к Трекеру

Если вы используете федеративный или сервисный аккаунт, авторизуйтесь с помощью [IAM-токена](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#iam-token).

Чтобы получить токен:

1. Перейдите по ссылке [https://oauth.yandex.ru](https://oauth.yandex.ru/).

2. На странице **Ваши приложения** нажмите  **Создать**.

3. В открывшемся окне выберите вариант **Для доступа к API или отладки** и нажмите **Перейти к созданию**.

4. Укажите название приложения и почту для связи.

5. Добавьте разрешения для доступа к данным пользователя. Чтобы выбрать разрешение, начните вводить его название в поле **Название доступа**:

    - **Запись в трекер (tracker:write)** — все операции с данными: создание, удаление, редактирование.
    - **Чтение из трекера (tracker:read)** — только чтение данных.
6. Нажмите **Создать приложение**.

7. В личном кабинете [Яндекс OAuth](https://oauth.yandex.ru/) выберите созданное ранее приложение и скопируйте его идентификатор из поля **ClientID**.

8. Сформируйте ссылку для запроса токена:

    ```
    https://oauth.yandex.ru/authorize?response_type=token&client_id=<идентификатор_приложения>
    ```

9. Войдите в аккаунт, от имени которого вы будете работать с API, и перейдите по сформированной ссылке.

    На странице появится последовательность символов — это OAuth-токен. Скопируйте его и сохраните.

Чтобы проверить наличие доступа к API, выполните [запрос информации о текущем пользователе](https://yandex.ru/support/tracker/ru/api-ref/users/get-user-info). Если доступ не был получен, запрос вернет ответ с кодом `401 Unauthorized`.

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

# Создайте функцию Cloud Functions для импорта данных

1. Перейдите в [консоль управления](https://console.cloud.yandex.ru/).
2. В левом верхнем углу нажмите кнопку  **Все сервисы**.
3. Выберите **Бессерверные вычисления** → **Cloud Functions**.
4. Нажмите кнопку **Создать функцию**.
5. Укажите название функции и нажмите кнопку **Создать**.
6. В открывшемся окне **Редактор** выберите среду выполнения `Python / 3.9`.
7. Нажмите кнопку **Продолжить**.
8. В поле **Способ** нажмите кнопку **ZIP-архив**.
9. Прикрепите [тестовый архив](https://github.com/yandex-cloud-examples/yc-tracker-data-import/blob/main/build/tracker-data-import.zip).
10. В поле **Точка входа** укажите `tracker_import.handler`.
11. В разделе **Параметры** укажите:
     - **Таймаут, c** — `60`;
     - **Память** — `1024`;
     - **Переменные окружения**:
         - `TRACKER_ORG_ID` — ID организации Яндекс 360 для бизнеса.

             Чтобы узнать идентификатор организации, перейдите на страницу **Администрирование** → [**Организации**](https://tracker.yandex.ru/admin/orgs) и скопируйте значение поля **идентификатор**.

         - `TRACKER_OAUTH_TOKEN` — [OAuth токен](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#oauth-token) учетной записи Трекера.

         - `CH_HOST` — имя [хоста](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#database-create).

         - `CH_DB` — название [базы данных](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#database-create).

         - `CH_USER` — [имя пользователя](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#database-create).

         - `CH_PASSWORD` — [пароль](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#database-create).

         - `CH_ISSUES_TABLE` — `tracker_issues`.

         - `CH_CHANGELOG_TABLE` — `tracker_changelog`.

         - `TRACKER_INITIAL_HISTORY_DEPTH` — `1d`.

         - `CH_STATUSES_VIEW` — `v_tracker_statuses`.

12. Нажмите кнопку **Сохранить изменения**.
13. На вкладке **Тестирование** нажмите кнопку **Запустить тест**.
14. Результат теста — лог импорта данных:

     ```
     {
         "statusCode": 200,
         "headers": {
         "Content-Type": "text/plain"
         },
         "isBase64Encoded": false,
         "body": "OK"
     }
     ```

15. Создайте [триггер](https://yandex.cloud/ru/docs/functions/concepts/trigger) для регулярного экспорта новых данных в БД:
     1. Откройте раздел **Cloud Functions**.
     2. Нажмите → **Создать триггер**.
     3. Укажите тип триггера — **Таймер**.
     4. В поле **Cron-выражение** выберите `Каждый день`.
     5. В разделе **Настройки функции** нажмите кнопку **Создать новый**.
     6. Укажите имя аккаунта. По умолчанию аккаунту присвоена роль `functions.functionInvoker` для работы с триггером.
     7. Нажмите кнопку **Создать**.
     8. Нажмите кнопку **Создать триггер**.

# Создайте подключение в DataLens

1. Откройте [кластер](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#database-create) **Managed Service for ClickHouse®**.

2. В левой части окна выберите раздел  **DataLens**.

3. Нажмите кнопку **Создать подключение**.

4. Укажите настройки подключения:

    - **Подключение** — `Выбрать в каталоге`;

    - **Кластер** — кластер, указанный при [создании базы данных](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#database-create);

    - **Имя хост** — хост, указанный при [создании базы данных](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#database-create);

    - **Порт HTTP-интерфейса** — `8443`;

    - **Имя пользователя** — имя пользователя, указанное при [создании базы данных](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#database-create);

    - **Пароль** — пароль, указанный при [создании базы данных](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#database-create);

    - **Время жизни кeша в секундах** — `По умолчанию`;

    - **Уровень доступа SQL запросов** — `Запретить`;

    - **HTTPS** — `Включено`.

        ![Настройки подключения](https://yandex.ru/support/tracker/docs-assets/support-tracker/rev/r19613496/ru/_assets/datalens-connection-settings.png)
5. Нажмите кнопку **Создать подключение**.

# Создайте датасет

1. Перейдите на [страницу подключений](https://datalens.yandex.cloud//connections).
2. Выберите [подключение](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#connection-create).
3. В правом верхнем углу нажмите кнопку **Создать датасет**.
4. Перенесите на рабочую область одну или несколько таблиц:
    - `db1.v_tracker_issues` — текущий (последний) срез задач;
    - `db1.v_tracker_changelog` — история изменения параметров задач;
    - `Db1.v_tracker_statuses` – время переходов между статусами на основе истории изменения задач.
5. Нажмите кнопку **Сохранить**.

# Создайте чарт

1. Перейдите на главную страницу [DataLens](https://datalens.yandex.cloud/).
2. Нажмите кнопку **Создать чарт**.
3. В левом верхнем углу нажмите  **Выберите датасет**.
4. В выпадающем списке **Датасеты** выберите [датасет](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#dataset-create), созданный на предыдущем шаге.
5. На верхней панели выберите [тип визуализации](https://yandex.cloud/ru/docs/datalens/visualization-ref). По умолчанию выбран тип **Столбчатая диаграмма**.

# Создайте дашборд и добавьте на него чарты

1. На главной странице [DataLens](https://datalens.yandex.cloud/) нажмите **Создать дашборд**.

2. В верхней части страницы [дашборда](https://yandex.ru/support/tracker/ru/tutorials/visualisation-in-datalens#dashboard-create) нажмите кнопку **Добавить** → **Чарт**.

3. Заполните параметры виджета. Обратите внимание на следующие поля:

    - **Название**. Задает имя виджета. Отображается на верхней части виджета.
    - **Чарт**. Задает добавляемый виджет.
    - **Описание**. Задает описание виджета. Отображается на нижней части виджета.
    - **Автовысота**. Задает автоматическую высоту для виджетов типа **Таблица** и **Markdown**. Если параметр отключен, то высоту виджета на странице можно установить с помощью мыши.
4. Нажмите кнопку **Добавить**. Виджет отобразится на дашборде.

5. Сохраните дашборд:

    1. В правом верхнем углу дашборда нажмите кнопку **Сохранить**.
    2. Введите название дашборда и нажмите **Создать**.

    Подробнее о настройке дашбордов см. в разделе [Дашборд DataLens](https://yandex.cloud/ru/docs/datalens/concepts/dashboard).

Пример дашборда на основе данных из таблицы `v_tracker_issues`

![Пример дашборда на основе данных по таблице v_tracker_issues](https://yandex.ru/support/tracker/docs-assets/support-tracker/rev/r19613496/ru/_assets/dashboard-from-table-issues.png)
Пример дашборда на основе данных по таблице `db1.v_tracker_statuses`

![Пример дашборда на основе данных по таблице db1.v_tracker_statuses](https://yandex.ru/support/tracker/docs-assets/support-tracker/rev/r19613496/ru/_assets/dashboard-from-table-statuses.png)

# Как удалить созданные ресурсы

Чтобы перестать платить за созданные ресурсы:

- [Удалите ClickHouse®-кластер](https://yandex.cloud/ru/docs/managed-clickhouse/operations/cluster-delete);
- [Удалите функцию Cloud Functions](https://yandex.cloud/ru/docs/functions/operations/function/function-delete).

*ClickHouse® является зарегистрированным товарным знаком [ClickHouse, Inc](https://clickhouse.com/).*
