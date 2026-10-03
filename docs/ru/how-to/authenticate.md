---
description: "Как получить OAuth-токен Яндекса и идентификатор организации Яндекс 360 для ycli: одной командой или вручную."
type: how-to
---

# Аутентификация

ycli нужны два значения. Он читает их из окружения или из файла `.env` в рабочем каталоге:

```bash
YANDEX_ID_OAUTH_TOKEN=...        # OAuth-токен Яндекса с доступом к Трекеру, Вики и Формам
YANDEX_ID_ORGANIZATION_ID=...    # идентификатор вашей организации в Яндекс 360
```

ycli передаёт идентификатор организации в заголовке `X-Org-Id` каждому сервису.

## Получите токен командой `ycli auth login`

Яндекс выдаёт OAuth-токены только через зарегистрированное приложение.

1. Зарегистрируйте приложение на [oauth.yandex.ru](https://oauth.yandex.ru/client/new) и выдайте ему
   права на **Трекер**, **Вики** и **Формы** — чтение и запись. Одних прав на чтение хватает только
   для `ycli mcp start --read-only`.
2. Положите в `.env` его ClientID, а если нужен сценарий без браузера, то и Client secret:

    ```bash
    YANDEX_OAUTH_CLIENT_ID=...
    YANDEX_OAUTH_CLIENT_SECRET=...    # необязательно: включает device flow
    ```

3. Выполните `ycli auth login`. Команда получит токен, определит вашу организацию и запишет оба
   значения в `.env`:
    - если заданы client id и secret, используется **device flow**: ycli печатает код и ссылку
      `https://ya.ru/device`, вы подтверждаете вход там, и ycli получает токен. Это работает и по SSH;
    - если задан только client id или передан `--implicit`, используется **browser flow**: ycli
      открывает страницу авторизации Яндекса, вы подтверждаете вход и вставляете показанный токен
      обратно.

## Проверьте учётные данные

```bash
ycli auth status            # чей это токен, какая организация, какие сервисы его принимают
ycli tracker auth status    # только один сервис (также wiki, forms)
ycli doctor                 # все проверки по порядку и что исправить в каждой, которая не прошла
```

`ycli doctor` ещё показывает, где задано каждое значение (в окружении или в файле `.env`, само значение — никогда) и какие extras установлены; для агента добавьте `-o json`. Все три команды завершаются с ненулевым кодом, если сервис отклонил токен. Для названия организации нужен
необязательный доступ `directory:read_organization`; без него вы получите идентификатор и пояснение.

## Вручную

Device flow:

```bash
# 1. запустить процесс: вернёт user_code и verification_url
curl -s -X POST https://oauth.yandex.ru/device/code -d "client_id=$YANDEX_OAUTH_CLIENT_ID"
# 2. открыть https://ya.ru/device, ввести user_code, подтвердить
# 3. обменять device_code на токен
curl -s -X POST https://oauth.yandex.ru/token \
  -d grant_type=device_code -d "code=<device_code>" \
  -d "client_id=$YANDEX_OAUTH_CLIENT_ID" -d "client_secret=$YANDEX_OAUTH_CLIENT_SECRET"
```

Browser flow: откройте `https://oauth.yandex.ru/authorize?response_type=token&client_id=<ClientID>`
в браузере, где вы вошли в аккаунт, подтвердите доступ и скопируйте токен со страницы.

Идентификатор организации: [tracker.yandex.ru/admin/orgs](https://tracker.yandex.ru/admin/orgs), ваша
организация, поле с идентификатором.

## Документация Яндекса

| Шаг | Документация Яндекса |
|---|---|
| Регистрация OAuth-приложения | [Регистрация приложения](https://yandex.ru/dev/id/doc/ru/register-client) |
| Device flow | [Ввод кода на странице авторизации](https://yandex.ru/dev/id/doc/ru/codes/screen-code-oauth) |
| Browser flow | [Получение токена вручную](https://yandex.ru/dev/id/doc/ru/tokens/debug-token) |
| Токен и заголовок организации для каждого сервиса | Доступ к API: [Трекер](https://yandex.ru/support/tracker/ru/api/access) · [Вики](https://yandex.ru/support/wiki/ru/api-ref/access) · [Формы](https://yandex.ru/support/forms/ru/api-ref/access) |
