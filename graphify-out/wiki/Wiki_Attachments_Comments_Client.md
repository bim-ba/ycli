# Wiki Attachments Comments Client

> 42 nodes · cohesion 0.05

## Key Concepts

- **AttachmentsClient** (6 connections) — `src/ycli/yandex/wiki/attachments/client.py`
- **._list_page()** (6 connections) — `src/ycli/yandex/wiki/attachments/client.py`
- **._list_page()** (6 connections) — `src/ycli/yandex/wiki/comments/client.py`
- **WikiResource** (6 connections) — `src/ycli/yandex/wiki/_base.py`
- **BaseYandex** (6 connections) — `src/ycli/yandex/base.py`
- **.list()** (5 connections) — `src/ycli/yandex/wiki/attachments/client.py`
- **CommentsClient** (5 connections) — `src/ycli/yandex/wiki/comments/client.py`
- **.list()** (5 connections) — `src/ycli/yandex/wiki/comments/client.py`
- **MeClient** (4 connections) — `src/ycli/yandex/wiki/me/client.py`
- **.__init__()** (4 connections) — `src/ycli/yandex/wiki/client.py`
- **.get()** (3 connections) — `src/ycli/yandex/wiki/me/client.py`
- **client.py** (2 connections) — `src/ycli/yandex/wiki/attachments/client.py`
- **Session** (2 connections) — `src/ycli/yandex/wiki/client.py`
- **client.py** (2 connections) — `src/ycli/yandex/wiki/comments/client.py`
- **client.py** (2 connections) — `src/ycli/yandex/wiki/me/client.py`
- **_base.py** (2 connections) — `src/ycli/yandex/wiki/_base.py`
- **base.py** (2 connections) — `src/ycli/yandex/base.py`
- **.__init__()** (2 connections) — `src/ycli/yandex/base.py`
- **Declarative Yandex Wiki /pages/{id}/attachments client (uplink) — transport ONLY** (1 connections) — `src/ycli/yandex/wiki/attachments/client.py`
- **Declarative HTTP for ``/pages/{id}/attachments``.** (1 connections) — `src/ycli/yandex/wiki/attachments/client.py`
- **``GET /pages/{id}/attachments`` → raw ``AttachmentsResponse`` envelope (internal** (1 connections) — `src/ycli/yandex/wiki/attachments/client.py`
- **``GET /pages/{id}/attachments`` → flat :class:`AttachmentList`.          Example** (1 connections) — `src/ycli/yandex/wiki/attachments/client.py`
- **AttachmentsResponse** (1 connections) — `src/ycli/yandex/wiki/attachments/client.py`
- **Declarative HTTP for ``/pages/{id}/comments``.** (1 connections) — `src/ycli/yandex/wiki/comments/client.py`
- **``GET /pages/{id}/comments`` → raw ``CommentsResponse`` envelope (internal).** (1 connections) — `src/ycli/yandex/wiki/comments/client.py`
- *... and 17 more nodes in this community*

## Relationships

- [[Pagination and Clients]] (2 shared connections)
- [[Wiki Pages Client]] (2 shared connections)
- [[Architecture and Docs]] (1 shared connections)
- [[Composition Roots Deps]] (1 shared connections)
- [[Forms Questions Client]] (1 shared connections)
- [[Tracker Me Client]] (1 shared connections)

## Source Files

- `src/ycli/yandex/base.py`
- `src/ycli/yandex/wiki/_base.py`
- `src/ycli/yandex/wiki/attachments/client.py`
- `src/ycli/yandex/wiki/client.py`
- `src/ycli/yandex/wiki/comments/client.py`
- `src/ycli/yandex/wiki/me/client.py`

## Audit Trail

- EXTRACTED: 84 (89%)
- INFERRED: 10 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*