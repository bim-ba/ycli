# Forms Answers Client

> 10 nodes · cohesion 0.24

## Key Concepts

- **AnswersClient** (10 connections) — `src/ycli/yandex/forms/answers/client.py`
- **FormsClient** (9 connections) — `src/ycli/yandex/forms/client.py`
- **.__init__()** (5 connections) — `src/ycli/yandex/forms/client.py`
- **Session** (3 connections) — `src/ycli/yandex/forms/client.py`
- **client.py** (2 connections) — `src/ycli/yandex/forms/answers/client.py`
- **client.py** (2 connections) — `src/ycli/yandex/forms/client.py`
- **Declarative Forms answers client (uplink) — transport ONLY.  NOTE: no ``from __f** (1 connections) — `src/ycli/yandex/forms/answers/client.py`
- **Declarative HTTP for ``/surveys/{id}/answers``.** (1 connections) — `src/ycli/yandex/forms/answers/client.py`
- **FormsClient — composition root over the forms resource clients (one shared sessi** (1 connections) — `src/ycli/yandex/forms/client.py`
- **Holds the per-resource forms clients, all sharing one authed ``requests.Session`** (1 connections) — `src/ycli/yandex/forms/client.py`

## Relationships

- [[Forms Answers MCP]] (3 shared connections)
- [[Forms Questions Client]] (2 shared connections)
- [[CLI Commands and Auth]] (2 shared connections)
- [[Architecture and Docs]] (2 shared connections)
- [[Pagination and Clients]] (1 shared connections)
- [[App Config and Server]] (1 shared connections)
- [[Composition Roots Deps]] (1 shared connections)
- [[Forms Surveys Client]] (1 shared connections)

## Source Files

- `src/ycli/yandex/forms/answers/client.py`
- `src/ycli/yandex/forms/client.py`

## Audit Trail

- EXTRACTED: 22 (63%)
- INFERRED: 13 (37%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*