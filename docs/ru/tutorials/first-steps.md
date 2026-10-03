---
description: "Установите ycli, войдите в Яндекс 360 и прочитайте задачу Яндекс Трекера из терминала, из Python и через ИИ-агента."
type: tutorial
---

# Первые шаги

За десять минут вы установите ycli, войдёте в Яндекс 360, прочитаете задачу Трекера из терминала и
из Python, а затем дадите сделать то же самое ИИ-агенту через MCP. Вам понадобятся
[uv](https://docs.astral.sh/uv/) и организация Яндекс 360 с Трекером.

## 1. Установка

```bash
uv tool install 'yandex-cli[mcp]'
ycli --version
```

Дополнение `mcp` добавляет MCP-сервер; CLI и SDK работают и без него.

## 2. Вход

Яндекс выдаёт токены только зарегистрированному приложению, поэтому сначала зарегистрируйте его:

1. Откройте [oauth.yandex.ru/client/new](https://oauth.yandex.ru/client/new), создайте приложение и
   выдайте ему права на Трекер, Вики и Формы (чтение и запись).
2. Скопируйте его **ClientID** и **Client secret** в файл `.env` в рабочем каталоге:

    ```bash
    YANDEX_OAUTH_CLIENT_ID=...
    YANDEX_OAUTH_CLIENT_SECRET=...
    ```

3. Запустите вход и перейдите по ссылке, которую он выведет:

    ```bash
    ycli auth login
    ```

    ycli покажет код и ссылку `https://ya.ru/device`; подтвердите вход там, и ycli запишет ваш
    токен и идентификатор организации в `.env`.

4. Проверьте, что каждый сервис принимает токен:

    ```bash
    ycli auth status
    ```

## 3. Чтение задачи из терминала

Возьмите ключ задачи, которую вы видите в Трекере, например `TEST-1`:

```bash
ycli tracker issues get TEST-1
ycli tracker issues get TEST-1 -o json | jq .summary
ycli --jq .summary tracker issues get TEST-1
```

В терминале первая команда печатает таблицу; если вывод передан по конвейеру, ycli печатает JSON.
`--jq` фильтрует JSON без отдельного `jq`.

## 4. Та же задача из Python

```python
from ycli.yandex.tracker.client import TrackerClient

with TrackerClient(oauth_token="...", organization_id="...") as tracker:
    issue = tracker.issues.get("TEST-1")
    print(issue.summary)
```

Подставьте два значения, которые `ycli auth login` записал в `.env`. Метод называется так же, как
команда: `ycli tracker issues get` — это `tracker.issues.get`.

## 5. Пусть это сделает агент

Добавьте сервер в MCP-клиент. Для Claude Code экспортируйте два значения, которые `ycli auth login`
записал в `.env` (`YANDEX_ID_OAUTH_TOKEN`, `YANDEX_ID_ORGANIZATION_ID`), и выполните:

```bash
claude mcp add yandex-360 --transport stdio \
  --env YANDEX_ID_OAUTH_TOKEN='${YANDEX_ID_OAUTH_TOKEN}' \
  --env YANDEX_ID_ORGANIZATION_ID='${YANDEX_ID_ORGANIZATION_ID}' \
  -- uvx --from 'yandex-cli[mcp]' ycli mcp start
```

Попросите агента прочитать `TEST-1`: он вызовет инструмент `tracker_issues_get` — так эта же
операция называется в MCP.

## Что дальше

- Другие ИИ-клиенты: [Установка в вашем ИИ-клиенте](../how-to/install-in-your-harness.md).
- Отдать агенту меньше инструментов или только чтение: [Запуск MCP-сервера](../how-to/serve-the-mcp-server.md).
- Все команды, инструменты и методы: [справочник](../reference/configuration.md).
