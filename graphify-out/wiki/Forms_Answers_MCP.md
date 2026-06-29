# Forms Answers MCP

> 15 nodes · cohesion 0.16

## Key Concepts

- **AnswersResponse** (9 connections) — `src/ycli/yandex/forms/answers/models.py`
- **list_()** (5 connections) — `src/ycli/yandex/forms/answers/mcp.py`
- **AnswersResponse** (5 connections) — `src/ycli/yandex/forms/answers/client.py`
- **.list()** (4 connections) — `src/ycli/yandex/forms/answers/client.py`
- **.list_all()** (4 connections) — `src/ycli/yandex/forms/answers/client.py`
- **Path** (4 connections) — `src/ycli/yandex/forms/answers/client.py`
- **mcp.py** (3 connections) — `src/ycli/yandex/forms/answers/mcp.py`
- **AnswersResponse** (3 connections) — `src/ycli/yandex/forms/answers/mcp.py`
- **AppConfig** (3 connections) — `src/ycli/yandex/forms/answers/mcp.py`
- **FormsClient** (3 connections) — `src/ycli/yandex/forms/answers/mcp.py`
- **``GET /surveys/{id}/answers`` → the ``{columns, answers, next}`` envelope (verba** (1 connections) — `src/ycli/yandex/forms/answers/client.py`
- **Drain responses across pages (HATEOAS ``next.next_url``), capped at ``limit``.** (1 connections) — `src/ycli/yandex/forms/answers/client.py`
- **Forms answers FastMCP tool (reads-only).** (1 connections) — `src/ycli/yandex/forms/answers/mcp.py`
- **A form's responses, capped at cfg.max_items (drains pages via the next cursor).** (1 connections) — `src/ycli/yandex/forms/answers/mcp.py`
- **Envelope for ``GET …/answers`` — ``{columns, answers, next}``.      ``next`` is** (1 connections) — `src/ycli/yandex/forms/answers/models.py`

## Relationships

- [[Forms Answers Client]] (3 shared connections)
- [[Pagination and Clients]] (3 shared connections)
- [[App Config and Server]] (3 shared connections)
- [[Forms Questions Client]] (2 shared connections)
- [[CLI Command Groups]] (1 shared connections)
- [[Forms Answers Models]] (1 shared connections)
- [[Wiki User Page Models]] (1 shared connections)

## Source Files

- `src/ycli/yandex/forms/answers/client.py`
- `src/ycli/yandex/forms/answers/mcp.py`
- `src/ycli/yandex/forms/answers/models.py`

## Audit Trail

- EXTRACTED: 29 (60%)
- INFERRED: 19 (40%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*