# Forms Me Client

> 7 nodes · cohesion 0.29

## Key Concepts

- **MeClient** (4 connections) — `src/ycli/yandex/forms/me/client.py`
- **.get()** (3 connections) — `src/ycli/yandex/forms/me/client.py`
- **client.py** (2 connections) — `src/ycli/yandex/forms/me/client.py`
- **User** (2 connections) — `src/ycli/yandex/forms/me/client.py`
- **Declarative HTTP for ``/users/me``.** (1 connections) — `src/ycli/yandex/forms/me/client.py`
- **``GET /users/me`` → the authenticated ``User`` (a safe auth probe).          Exa** (1 connections) — `src/ycli/yandex/forms/me/client.py`
- **Declarative Forms /users/me client (uplink) — transport ONLY.  NOTE: do NOT add** (1 connections) — `src/ycli/yandex/forms/me/client.py`

## Relationships

- [[Forms Questions Client]] (2 shared connections)

## Source Files

- `src/ycli/yandex/forms/me/client.py`

## Audit Trail

- EXTRACTED: 12 (86%)
- INFERRED: 2 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*