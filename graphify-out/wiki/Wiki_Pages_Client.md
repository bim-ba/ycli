# Wiki Pages Client

> 21 nodes · cohesion 0.15

## Key Concepts

- **CursorStrategy** (13 connections) — `src/ycli/yandex/pagination.py`
- **PagesClient** (10 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **.descendants()** (5 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **._descendants_page()** (5 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **.update()** (5 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **.create()** (4 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **.get()** (4 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **PageDetails** (4 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **Body** (3 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **Query** (3 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **DescendantsResponse** (2 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **client.py** (2 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **PageRefList** (2 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **Path** (2 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **Declarative Yandex Wiki /pages client (uplink) — transport ONLY.  NOTE: do NOT a** (1 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **Declarative HTTP for ``/pages`` (get, descendants, create, update).** (1 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **``GET /pages?slug=&fields=`` → a single page (raises on non-2xx).          Examp** (1 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **One raw page of ``{id, slug}`` refs + ``next_cursor``.          Internal; caller** (1 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **All descendant refs under ``slug``, draining ``next_cursor`` internally.** (1 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **``POST /pages`` — create. ``body`` carries ``content``/``title``/``slug``.** (1 connections) — `src/ycli/yandex/wiki/pages/client.py`
- **``POST /pages/{id}`` — update (POST not PATCH; PATCH returns 405).          Exam** (1 connections) — `src/ycli/yandex/wiki/pages/client.py`

## Relationships

- [[Pagination and Clients]] (5 shared connections)
- [[Wiki Attachments Comments Client]] (2 shared connections)

## Source Files

- `src/ycli/yandex/pagination.py`
- `src/ycli/yandex/wiki/pages/client.py`

## Audit Trail

- EXTRACTED: 54 (76%)
- INFERRED: 17 (24%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*