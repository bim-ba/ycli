---
description: "CLI для Яндекс Трекера, Вики и Форм в shell-скриптах: вывод JSON, фильтры jq, пробный запуск, коды возврата, автодополнение."
type: how-to
---

# CLI в скриптах

## Получить JSON

В терминале ycli печатает таблицы, а при передаче по конвейеру — JSON. Формат можно задать явно глобальным флагом `--format` / `-o` (`auto`, `json`, `yaml`, `pretty`) до команды или после неё:

```bash
ycli tracker issues get TRACKER-1 | jq .        # JSON, потому что вывод передаётся по конвейеру
ycli -o yaml wiki pages get onboarding
ycli wiki pages get onboarding -o json
```

Ключи — это имена полей самого API (`createdAt` в Трекере, `created_at` в Вики), поэтому фильтры из документации Яндекса работают как есть.

## Фильтрация вывода

Своего фильтра у ycli нет: передайте JSON по конвейеру в [jq](https://jqlang.org).

```bash
ycli tracker issues get TRACKER-1 -o json | jq -r .summary
ycli tracker issues search 'Queue: TEST' -o json | jq -r '.[].key'
```

`-o json` задаёт формат явно; без него по конвейеру всё равно уходит JSON.

## Удаление без запроса подтверждения

Команда, которая уничтожает данные, в терминале просит подтверждения. В скрипте спросить некого, поэтому она завершается с кодом 2, пока вы не передадите `--yes` / `-y`:

```bash
ycli tracker boards delete 7 --yes
```

## Предпросмотр записи

`--dry-run` ничего не записывает, а печатает запрос (метод, URL, тело — но никогда не токен) в том же формате `-o`, и завершается с кодом 0. Чтения всё равно выполняются, поэтому команда, которая сначала читает, а потом пишет, покажет только свою первую запись.

```bash
ycli tracker boards delete 7 --dry-run
```

## Ветвление по коду возврата

У каждого вида ошибки свой код возврата; они перечислены в [справочнике по конфигурации](../reference/configuration.md#exit-codes).

```bash
ycli tracker issues get TRACKER-1 > issue.json
case $? in
  0) echo found ;;
  3) echo "no such issue" ;;
  6) echo "try again later" ;;
esac
```

## Автодополнение команд по Tab

В ycli несколько сотен команд; пусть их дополняет оболочка. Сначала установите ycli как инструмент (`uv tool install yandex-cli`), чтобы команда оставалась в `PATH`, затем выполните:

```bash
ycli --install-completion    # для текущей оболочки: bash, zsh, fish или PowerShell
```

Перезапустите терминал. Автодополнение устанавливается для того имени, которым вы запускали команду: если вы пользуетесь длинным именем, выполните `yandex-cli --install-completion` ещё раз. `ycli --show-completion` печатает скрипт, а не устанавливает его.

О запуске ycli в конвейере см. [Использование в CI](use-in-ci.md).
