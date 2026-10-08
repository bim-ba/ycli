---
description: "Страницы Яндекс Вики и триггеры Трекера как файлы в git: ycli sync pull, diff и push, с ревью плана в пул-реквесте."
type: how-to
---

# Содержимое в git

`ycli sync` держит объекты Яндекс 360 как файлы git-репозитория: вы забираете их, правите как любой текст, проверяете изменение в пул-реквесте и отправляете обратно. Сейчас так хранятся два вида объектов, их перечисляет `ycli sync kinds`:

| Вид | Файл | Путь |
|---|---|---|
| `wiki/page` | Markdown под короткой шапкой | `wiki/team/onboarding.md` для страницы `team/onboarding` |
| `tracker/trigger` | YAML | `tracker/queues/DE/triggers/16.yaml` для триггера 16 очереди `DE` |

Все команды запускаются из корня репозитория. Учётные данные обычные (см. [Аутентификация](authenticate.md)).

Инструментов MCP для этого нет: `sync` работает в вашем рабочем каталоге, а у сервера MCP его нет. Агент пользуется теми же командами.

## Забрать

```console
$ ycli sync pull wiki/team
3 written, 0 unchanged, 1 skipped
$ ycli sync pull tracker/queues/DE
```

`pull wiki/team` пишет страницу `team` в `wiki/team.md`, а все страницы под ней — в `wiki/team/`. Объект, который вид не хранит, например таблица среди страниц, назван как пропущенный. Файл выглядит так:

```markdown
---
ycli: wiki/page
hash: 3954dedc1b058bc73e60e88d4436078e9689cc2e811ffb88e1e6cd48563c3a8d
id: 4821
revision: 9
title: Team
---
# Team
```

Первые четыре ключа — связь файла с объектом, их пишет ycli: не правьте их. `hash` — отпечаток содержимого, каким оно было прочитано; по нему все следующие команды понимают, что изменилось.

`pull` пишет поверх того, что есть. Закоммитьте свои правки перед `pull`: защищает их только git. `ycli --dry-run sync pull wiki/team` ничего не пишет и называет файлы с незакоммиченной работой, которые были бы перезаписаны.

## Посмотреть, что изменилось

```console
$ ycli sync status
$ ycli sync diff
```

`status` читает только файлы, поэтому работает без сети и годится для pre-commit. `diff` читает сервер и показывает для каждого файла разницу от объекта, каков он сейчас, к файлу. Обе команды говорят, что `push` сделал бы с файлом:

| Состояние | Что значит |
|---|---|
| `unchanged` | отправлять нечего |
| `update` | вы правили файл |
| `create` | файл ещё не называет объект: `push` его создаст |
| `untracked` | файл называет объект, но никогда с него не читался: сначала `pull` |
| `changed-on-server` | объект кто-то изменил после вашего `pull` (только `diff`) |
| `gone` | объекта больше нет (только `diff`) |
| `no-file` | в контейнере есть объект без файла: его запишет `pull` (`diff` по каталогу) |
| `unsupported` | API не умеет того, чего просит файл |
| `unreadable` | это не файл известного вида; названы строка и причина |

Неизменённые файлы скрыты; `--show-unchanged` их показывает. `--kind wiki/page` ограничивает запуск одним видом, путь — файлом или каталогом.

Если объект изменился на сервере, `diff` показывает ваш файл против сервера, каков он сейчас. Файл хранит только отпечаток того, что было прочитано, поэтому `diff` не может сказать, какие строки ваши, а какие чужие: сделайте `pull` в чистое дерево, и разницу покажет git.

## Отправить

```console
$ ycli --dry-run sync push
$ ycli sync push
0 created, 1 updated, 0 deleted, 14 unchanged, 0 stopped, 0 failed
$ git commit -am "Update the onboarding page"
```

`push` отправляет файл, только если его объект остался таким, каким вы его забрали. После каждой записи он читает объект заново и пишет новую связь в файл, поэтому за `push` следует коммит.

| Итог | Что произошло |
|---|---|
| `created`, `updated`, `deleted` | сделано и перечитано |
| `stopped` | файл и объект разошлись (`changed-on-server`, `untracked`, `gone`): ничего не отправлено; сначала `pull`, потом `push` |
| `failed` | API отказал, или сервис не сохранил отправленное значение: оно названо |

Новому файлу связь не нужна: напишите `ycli: wiki/page`, `title` и текст, положите файл туда, где должна жить страница, и `push` создаст её и допишет остальное. Новый файл триггера переименовывается по идентификатору триггера.

`--on-error abort` заканчивает запуск на первом сбойном файле; по умолчанию запуск идёт дальше.

### Удалить то, что вы удалили

Сам `push` ничего не удаляет. Чтобы удалить объекты, файлы которых вы убрали, назовите коммит для сравнения:

```console
$ ycli --dry-run sync push --prune main
$ ycli sync push --prune main
```

ycli берёт удалённые файлы из git и спрашивает перед каждым удалением; `--yes` отвечает за все. Объект, у которого никогда не было файла, не удаляется.

## Проверить файлы перед коммитом

`ycli sync validate` завершается с ошибкой, когда файл не читается как файл своего вида или лежит не там, где лежат файлы этого вида, и называет строку. Как хук [pre-commit](https://pre-commit.com/):

```yaml
repos:
  - repo: local
    hooks:
      - id: ycli-sync-validate
        name: ycli sync validate
        entry: ycli sync validate
        language: system
        pass_filenames: false
```

## Ревью плана в пул-реквесте

С `--exit-code` команды `status` и `diff` завершаются с кодом `7`, когда есть что отправлять, и с кодом `8`, когда файл и объект разошлись; без флага код всегда `0`. Эта задача пишет план комментарием к пул-реквесту и падает, когда сначала нужен `pull`:

```yaml
name: sync-plan
on: pull_request

jobs:
  plan:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    env:
      YANDEX_ID_OAUTH_TOKEN: ${{ secrets.YANDEX_ID_OAUTH_TOKEN }}
      YANDEX_ID_ORGANIZATION_ID: ${{ secrets.YANDEX_ID_ORGANIZATION_ID }}
      GH_TOKEN: ${{ github.token }}
    steps:
      - uses: actions/checkout@v5
      - uses: astral-sh/setup-uv@v10.2.0
      - name: Plan
        run: |
          uvx yandex-cli==0.130.1 sync diff --exit-code -o json > plan.json || code=$?
          jq -r '.[] | "### `\(.path)`: \(.state)\n\n```diff\n\(.diff // .detail // "")\n```\n"' plan.json > plan.md
          test -s plan.md || echo "Nothing to push." > plan.md
          gh pr comment "${{ github.event.pull_request.number }}" --body-file plan.md
          case "${code:-0}" in 0|7) ;; *) exit "$code" ;; esac
```

Секреты в разнице скрыты. Отправляйте с основной ветки после слияния — теми же двумя секретами и `ycli sync push`, — затем закоммитьте связи, которые записал `push`.

*Проверено 2026-10-08 на настоящей организации: pull, status, diff и push с `--prune` на страницах Вики; pull, diff и push правки на триггере очереди Трекера. Создание триггера из файла, хук pre-commit и задача GitHub Actions не запускались.*
