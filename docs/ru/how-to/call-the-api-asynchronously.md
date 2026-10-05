---
description: "Вызов Яндекс Трекера, Вики и Форм из кода на asyncio: асинхронная сессия и эндпоинты любого ресурса ycli."
type: how-to
---

# Асинхронный вызов API

Клиенты ресурсов (`tracker.issues.get(...)`) синхронные. Для кода на `asyncio` используйте слой,
на котором они построены: у каждого ресурса есть модуль `endpoints`, который описывает его
запросы и ничего не отправляет, а асинхронная сессия отправляет любой из них.

```python
import asyncio

from pydantic import SecretStr

from ycli.yandex import tracker
from ycli.yandex.core.auth import OAuthTokenAuth
from ycli.yandex.core.session import connect_async
from ycli.yandex.tracker.boards import endpoints as boards
from ycli.yandex.tracker.issues import endpoints as issues
from ycli.yandex.tracker.issues.models import IssueSearch


async def main() -> None:
    session = connect_async(
        tracker.SERVICE.profile,
        auth=OAuthTokenAuth(SecretStr("…")),
        organization_id="…",
    )
    try:
        board = await session.send(boards.get(31))                      # один запрос
        search = issues.search(IssueSearch(filter={"queue": "DE"}), expand=None)
        async for issue in session.iterate(search, limit=500):         # все страницы
            print(issue.key, issue.summary)
    finally:
        await session.aclose()


asyncio.run(main())
```

## Что вызывать

| Нужно | Вызов | Что возвращает |
|---|---|---|
| сессия сервиса | `connect_async(<service>.SERVICE.profile, auth=…, organization_id=…)` | `AsyncSession` |
| один запрос | `await session.send(endpoints.<operation>(…))` | разобранную модель, как метод клиента |
| листание | `async for item in session.iterate(endpoints.<operation>(…), limit=N)` | элементы, страница за страницей; `limit=None` читает все |
| завершить | `await session.aclose()` | закрывает соединения |

- Сервис — `ycli.yandex.tracker`, `ycli.yandex.wiki` или `ycli.yandex.forms`; в его
  `SERVICE.profile` лежат базовый адрес и имя заголовка организации.
- Функция в `endpoints` называется так же, как метод клиента, который её отправляет:
  `tracker.boards.update(...)` отправляет `boards.endpoints.update(...)`. Имя, совпадающее со
  встроенным в Python, получает подчёркивание: `endpoints.list_`. Методы перечислены в
  [справочнике SDK](https://ycli.savaznatnov.dev/reference/sdk/tracker/); функция принимает те же значения, но может
  требовать аргумент, у которого в методе есть значение по умолчанию (`expand=None` выше).
- Эндпоинт, который возвращает листание (`Paged`), передаётся в `iterate`, любой другой — в
  `send`.
- `auth` — `OAuthTokenAuth` для OAuth-токена или `IAMTokenAuth` для IAM-токена, оба из
  `ycli.yandex.core.auth`.

Ошибки, повторы и журнал — те же, что у синхронных клиентов: неудачный вызов поднимает
типизированную ошибку из `ycli.yandex.errors`, а запрос, который безопасно повторить,
повторяется.

## Много вызовов сразу

Одна сессия обслуживает параллельные вызовы:

```python
from ycli.yandex.wiki.pages import endpoints as pages

found = await asyncio.gather(
    *(
        session.send(pages.get(slug, fields=None, revision_id=None, raise_on_redirect=False))
        for slug in ("team/a", "team/b", "team/c")
    )
)
```

## Чего это не даёт

У метода клиента, который делает больше одного запроса, асинхронной пары нет: ожидание конца
долгой операции, загрузка файла частями, сборка тела запроса из нескольких аргументов. В
асинхронном коде эти шаги вы делаете сами из тех же эндпоинтов. Асинхронный клиент с полным
набором методов отслеживается в [#321](https://github.com/bim-ba/ycli/issues/321).
