---
type: how-to
---

# Вызов необёрнутого эндпоинта

`ycli api PATH --service tracker|wiki|forms` вызывает любой эндпоинт сервиса — так же, как это делает
[`gh api`](https://cli.github.com/manual/gh_api): с той же аутентификацией, повторами, выводом и
кодами возврата, что и у остальных команд.

```bash
ycli api issues/TRACKER-1 --service tracker --jq .summary                # GET по умолчанию
ycli api issues/TRACKER-1/comments --service tracker -F text=@note.md    # поле превращает запрос в POST
ycli api pages/descendants --service wiki -f slug=docs --paginate        # все страницы одним JSON-массивом
```

- `PATH` задаётся относительно базового URL сервиса. Полному URL сервиса `--service` не нужен;
  любой другой хост отклоняется, поэтому токен не уходит за пределы Яндекса.
- `-f key=value` отправляет строку; `-F` — типизированное значение: `true`, `null`, числа, JSON,
  `@file` — текст файла, `key[sub]=v` — вложенное поле, `key[]=v` — элемент массива.
- Поля запроса GET или DELETE уходят в строку запроса, во всех остальных случаях — в JSON-тело.
  `--input FILE` отправляет вместо этого тело как есть.
- `-H 'Name: value'` добавляет заголовок, а `-X` задаёт метод. `--dry-run`, `--yes` и `--jq`
  работают так же, как везде.
- `--paginate` идёт по `Link: rel="next"` в Трекере и по `next_cursor` в Вики. Формы разбивают списки
  на страницы несколькими способами, поэтому параметры постраничной выдачи передавайте сами через `-f`.

Полный список опций — в [справочнике по `ycli api`](https://bim-ba.github.io/ycli/reference/cli/api/).
