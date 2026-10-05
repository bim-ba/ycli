---
description: "Call Yandex Tracker, Wiki and Forms from asyncio code: an async session plus the endpoints of any ycli resource."
type: how-to
---

# Call the API asynchronously

The resource clients (`tracker.issues.get(...)`) are synchronous. For `asyncio` code, use the
layer they are built on: every resource has an `endpoints` module that describes its requests
and sends nothing, and an asynchronous session sends any of them.

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
        board = await session.send(boards.get(31))                      # one request
        search = issues.search(IssueSearch(filter={"queue": "DE"}), expand=None)
        async for issue in session.iterate(search, limit=500):         # every page
            print(issue.key, issue.summary)
    finally:
        await session.aclose()


asyncio.run(main())
```

## What you call

| You need | Call | Returns |
|---|---|---|
| a session of a service | `connect_async(<service>.SERVICE.profile, auth=…, organization_id=…)` | an `AsyncSession` |
| one request | `await session.send(endpoints.<operation>(…))` | the parsed model, as the client method does |
| a listing | `async for item in session.iterate(endpoints.<operation>(…), limit=N)` | the items, page after page; `limit=None` reads all |
| to finish | `await session.aclose()` | closes the connections |

- The service is `ycli.yandex.tracker`, `ycli.yandex.wiki` or `ycli.yandex.forms`; its
  `SERVICE.profile` holds the base URL and the name of the organization header.
- A function in `endpoints` has the name of the client method that sends it:
  `tracker.boards.update(...)` sends `boards.endpoints.update(...)`. A name that is a Python
  builtin takes an underscore, `endpoints.list_`. The
  [SDK reference](../reference/sdk/tracker.md) lists the methods; the function takes the same
  values, but may require an argument the method gives a default (`expand=None` above).
- An endpoint that returns a listing (`Paged`) goes to `iterate`; any other goes to `send`.
- `auth` is `OAuthTokenAuth` for an OAuth token or `IAMTokenAuth` for an IAM token, both from
  `ycli.yandex.core.auth`.

Errors, retries and logging are the same as in the synchronous clients: a failed call raises a
typed error from `ycli.yandex.errors`, and a request that is safe to repeat is retried.

## Many calls at once

One session serves concurrent calls:

```python
from ycli.yandex.wiki.pages import endpoints as pages

found = await asyncio.gather(
    *(
        session.send(pages.get(slug, fields=None, revision_id=None, raise_on_redirect=False))
        for slug in ("team/a", "team/b", "team/c")
    )
)
```

## What this does not give

A client method that does more than send one request has no asynchronous twin: waiting for a
long operation to finish, uploading a file in parts, building a request body from several
arguments. In async code you make those steps yourself from the same endpoints. An asynchronous
client with the full set of methods is tracked in
[#321](https://github.com/bim-ba/ycli/issues/321).
