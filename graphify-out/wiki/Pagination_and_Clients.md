# Pagination and Clients

> 22 nodes · cohesion 0.14

## Key Concepts

- **NextUrlStrategy** (10 connections) — `src/ycli/yandex/pagination.py`
- **SinglePageStrategy** (9 connections) — `src/ycli/yandex/pagination.py`
- **Any** (8 connections) — `src/ycli/yandex/pagination.py`
- **collect_single_page()** (8 connections) — `src/ycli/yandex/pagination.py`
- **pagination.py** (7 connections) — `src/ycli/yandex/pagination.py`
- **PaginationStrategy** (6 connections) — `src/ycli/yandex/pagination.py`
- **ABC** (4 connections)
- **PaginationStrategy ABC** (3 connections) — `src/ycli/yandex/pagination.py`
- **.collect()** (3 connections) — `src/ycli/yandex/pagination.py`
- **.collect()** (3 connections) — `src/ycli/yandex/pagination.py`
- **.collect()** (2 connections) — `src/ycli/yandex/pagination.py`
- **.__init__()** (2 connections) — `src/ycli/yandex/pagination.py`
- **.__init__()** (2 connections) — `src/ycli/yandex/pagination.py`
- **.collect()** (2 connections) — `src/ycli/yandex/pagination.py`
- **.__init__()** (2 connections) — `src/ycli/yandex/pagination.py`
- **forms surveys client** (1 connections) — `src/ycli/yandex/forms/surveys/client.py`
- **wiki attachments client** (1 connections) — `src/ycli/yandex/wiki/attachments/client.py`
- **wiki comments client** (1 connections) — `src/ycli/yandex/wiki/comments/client.py`
- **Pagination strategies — drain an API's page mechanics into a bounded flat list.** (1 connections) — `src/ycli/yandex/pagination.py`
- **Accumulate items by driving ``fetch_page`` until exhausted or ``limit`` reached.** (1 connections) — `src/ycli/yandex/pagination.py`
- **HATEOAS: the first page comes from ``fetch_page``; subsequent ones from ``fetch_** (1 connections) — `src/ycli/yandex/pagination.py`
- **Single-page envelope -> bounded, wrapped flat collection (the wiki/forms list sh** (1 connections) — `src/ycli/yandex/pagination.py`

## Relationships

- [[Wiki Pages Client]] (5 shared connections)
- [[Forms Answers MCP]] (3 shared connections)
- [[CLI Command Groups]] (2 shared connections)
- [[Wiki Attachments Comments Client]] (2 shared connections)
- [[Forms Surveys Client]] (1 shared connections)
- [[Forms Answers Client]] (1 shared connections)

## Source Files

- `src/ycli/yandex/forms/surveys/client.py`
- `src/ycli/yandex/pagination.py`
- `src/ycli/yandex/wiki/attachments/client.py`
- `src/ycli/yandex/wiki/comments/client.py`

## Audit Trail

- EXTRACTED: 72 (92%)
- INFERRED: 6 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*