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

`ycli doctor` ещё показывает, где задано каждое значение (в окружении или в файле `.env`, само значение — никогда), какие extras установлены и не вышел ли новый релиз; для агента добавьте `-o json`. Все три команды завершаются с ненулевым кодом, если сервис отклонил токен. Для названия организации нужен
необязательный доступ `directory:read_organization`; без него вы получите идентификатор и пояснение.

## IAM-токен вместо OAuth-токена { #use-an-iam-token }

Учётная запись, которая не может получить OAuth-токен (например, федеративная), может использовать готовый IAM-токен:

```bash
export YANDEX_CLOUD_IAM_TOKEN="$(yc iam create-token)"   # вместо YANDEX_ID_OAUTH_TOKEN
export YANDEX_ID_ORGANIZATION_ID=...                      # тот же идентификатор организации
ycli doctor
```

Он передаётся как `Authorization: Bearer` и работает с Трекером, Вики и Формами. Живёт до 12 часов: когда вызовы начнут отвечать 401, выпустите новый. Задайте один токен, не оба: с двумя ycli останавливается с кодом возврата 2 и называет их. Для IAM-токена `ycli auth status` не может назвать владельца и организацию (Яндекс ID и API 360 принимают только OAuth-токен); проверки сервисов выполняются как обычно.

## Несколько организаций { #keep-several-organizations }

Профиль — это сохранённая под именем пара из токена и организации. Сохраните по профилю на организацию и называйте тот, от имени которого должна выполниться команда:

```bash
ycli auth login --profile work        # войти и сохранить результат как «work»
ycli auth login --profile client
ycli --profile client tracker me get  # одна команда от имени «client»
export YCLI_PROFILE=work              # все команды этой оболочки от имени «work»
ycli auth profiles                    # сохранённые профили, без токенов
```

Когда профиль назван, через `--profile` или `YCLI_PROFILE`, токен и организация берутся только из него: `YANDEX_ID_OAUTH_TOKEN`, `YANDEX_ID_ORGANIZATION_ID` и `.env` для них не читаются, поэтому экспортированный токен не отправит команду в другую организацию. Опция важнее переменной. Если профиль не назван, всё работает как раньше. «Текущий» профиль между командами не запоминается.

Профиль — это один файл `<имя>.env` с теми же переменными, что и в `.env`, в каталоге `profiles` вашей пользовательской конфигурации (путь печатает `ycli doctor`; в Linux это `~/.config/ycli/profiles`). `ycli auth login` создаёт файл доступным только вам. Чтобы завести профиль вручную, скопируйте туда готовый `.env`; чтобы удалить профиль, удалите файл. Имя состоит из строчных латинских букв, цифр, `-` и `_`. Неизвестное имя или файл без токена или организации останавливают команду с кодом возврата 2.

MCP-сервер принимает ту же опцию при работе через stdio: `ycli mcp start --profile work`.

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
