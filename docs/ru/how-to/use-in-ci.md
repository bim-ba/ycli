---
description: "ycli в GitHub Actions и GitLab CI: комментарий в задаче Яндекс Трекера после выкладки, секреты и коды возврата."
type: how-to
---

# Использование в CI

Запускайте ycli в конвейере, чтобы прокомментировать задачу после деплоя, перевести её дальше по процессу или прочитать страницу. Конвейеру нужны три вещи: сам ycli, два учётных значения в виде секретов и команды, которые никогда не ждут человека.

## Учётные данные

Сохраните `YANDEX_ID_OAUTH_TOKEN` и `YANDEX_ID_ORGANIZATION_ID` как секреты конвейера и передайте их задаче как переменные окружения. Токен — это OAuth-токен человека (см. [Аутентификация](authenticate.md)). Рабочий путь для конвейера сегодня — учётная запись, заведённая под автоматику: добавьте для неё пользователя в организацию, дайте ему только то, что делает конвейер, и выпустите его OAuth-токен.

Сервисный аккаунт Yandex Cloud заменить такого пользователя не может. Для [Вики](https://yandex.ru/support/wiki/ru/api-ref/access) и [Форм](https://yandex.ru/support/forms/ru/api-ref/access) Яндекс его не допускает вовсе, а для [Трекера](https://yandex.ru/support/tracker/ru/api/access) — только в организации Yandex Cloud и после обращения в поддержку Яндекса. Готовый IAM-токен пользователя работает вместо OAuth-токена (`YANDEX_CLOUD_IAM_TOKEN`, см. [Аутентификация](authenticate.md#use-an-iam-token)), но живёт до 12 часов, поэтому подходит задаче, которая выпускает его в начале, а не хранимому секрету.

## GitHub Actions

```yaml
name: notify-tracker
on:
  workflow_dispatch:

jobs:
  comment:
    runs-on: ubuntu-latest
    env:
      YANDEX_ID_OAUTH_TOKEN: ${{ secrets.YANDEX_ID_OAUTH_TOKEN }}
      YANDEX_ID_ORGANIZATION_ID: ${{ secrets.YANDEX_ID_ORGANIZATION_ID }}
    steps:
      - uses: astral-sh/setup-uv@v10.2.0
      - run: uvx yandex-cli==0.107.0 tracker comments create TRACKER-1 --text "Deployed ${GITHUB_SHA::7}"
```

`uvx yandex-cli==<version>` запускает указанную версию, ничего больше не устанавливая. Фиксируйте версию: конвейер не должен менять поведение при выходе нового релиза.

Готовый GitHub Action запланирован: следите за [#210](https://github.com/bim-ba/ycli/issues/210).

## GitLab CI

Точка входа образа — `ycli`, поэтому сбросьте её, чтобы получить оболочку для `script`:

```yaml
comment:
  image:
    name: ghcr.io/bim-ba/ycli:0.107.0
    entrypoint: [""]
  script:
    - ycli tracker comments create TRACKER-1 --text "Deployed $CI_COMMIT_SHORT_SHA"
```

Задайте две переменные в **Settings → CI/CD → Variables** с признаком masked.

## Любой другой раннер

С Docker передавайте переменные по имени, чтобы их значения не попадали в командную строку:

```bash
docker run --rm -e YANDEX_ID_OAUTH_TOKEN -e YANDEX_ID_ORGANIZATION_ID \
  ghcr.io/bim-ba/ycli:0.107.0 tracker comments create TRACKER-1 --text "Deployed"
```

## Команды, которые не ждут

- **Для удаления нужен `--yes`.** Команда, которая уничтожает данные, просит подтверждения; без терминала она вместо этого завершается с кодом 2. Передайте `--yes`, если конвейер должен удалять.
- **Вывод — JSON.** Без терминала ycli печатает JSON, поэтому его читает `jq`: `ycli tracker issues get TRACKER-1 | jq .key`.
- **Сначала попробуйте.** `--dry-run` печатает запрос, который отправила бы запись, и ничего не отправляет.

## Завершайте задачу с верным кодом

У каждого вида ошибки свой [код возврата](../reference/configuration.md#exit-codes). Конвейер обычно повторяет запуск при временном сбое и останавливается при остальных:

```bash
ycli tracker comments create TRACKER-1 --text "Deployed" || status=$?
case "${status:-0}" in
  0) ;;
  5|6) echo "Tracker is busy or down, retry later"; exit 75 ;;
  4) echo "The token is missing or rejected"; exit 1 ;;
  *) exit "$status" ;;
esac
```

*Проверено на 2026-10-03: команды Docker и сброшенная точка входа работают с настоящей организацией; задания GitHub Actions и GitLab не запускались.*
