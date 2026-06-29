# Forms Questions Client

> 16 nodes · cohesion 0.15

## Key Concepts

- **FormsResource** (16 connections) — `src/ycli/yandex/forms/_base.py`
- **QuestionsClient** (5 connections) — `src/ycli/yandex/forms/questions/client.py`
- **.list()** (4 connections) — `src/ycli/yandex/forms/questions/client.py`
- **.get()** (4 connections) — `src/ycli/yandex/forms/surveys/client.py`
- **_base.py** (2 connections) — `src/ycli/yandex/forms/_base.py`
- **client.py** (2 connections) — `src/ycli/yandex/forms/questions/client.py`
- **Path** (2 connections) — `src/ycli/yandex/forms/questions/client.py`
- **QuestionsResponse** (2 connections) — `src/ycli/yandex/forms/questions/client.py`
- **Path** (2 connections) — `src/ycli/yandex/forms/surveys/client.py`
- **Survey** (2 connections) — `src/ycli/yandex/forms/surveys/client.py`
- **Per-domain base — carries the Forms API base_url; resource clients inherit it.** (1 connections) — `src/ycli/yandex/forms/_base.py`
- **Base for every Forms resource client (inherits session DI via constructor).** (1 connections) — `src/ycli/yandex/forms/_base.py`
- **Declarative Forms questions client (uplink) — transport ONLY.  NOTE: no ``from _** (1 connections) — `src/ycli/yandex/forms/questions/client.py`
- **Declarative HTTP for ``/surveys/{id}/questions``.** (1 connections) — `src/ycli/yandex/forms/questions/client.py`
- **``GET /surveys/{id}/questions`` → the ``{pages}`` envelope (verbatim).** (1 connections) — `src/ycli/yandex/forms/questions/client.py`
- **``GET /surveys/{id}`` → a single ``Survey`` (settings).          Example:** (1 connections) — `src/ycli/yandex/forms/surveys/client.py`

## Relationships

- [[Forms Surveys Client]] (4 shared connections)
- [[Forms Answers Client]] (2 shared connections)
- [[Forms Answers MCP]] (2 shared connections)
- [[Forms Me Client]] (2 shared connections)
- [[Wiki Attachments Comments Client]] (1 shared connections)

## Source Files

- `src/ycli/yandex/forms/_base.py`
- `src/ycli/yandex/forms/questions/client.py`
- `src/ycli/yandex/forms/surveys/client.py`

## Audit Trail

- EXTRACTED: 27 (57%)
- INFERRED: 20 (43%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*