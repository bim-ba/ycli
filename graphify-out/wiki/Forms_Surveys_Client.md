# Forms Surveys Client

> 10 nodes · cohesion 0.22

## Key Concepts

- **SurveysClient** (7 connections) — `src/ycli/yandex/forms/surveys/client.py`
- **.list()** (5 connections) — `src/ycli/yandex/forms/surveys/client.py`
- **._list_page()** (4 connections) — `src/ycli/yandex/forms/surveys/client.py`
- **SurveyList** (2 connections) — `src/ycli/yandex/forms/surveys/client.py`
- **client.py** (2 connections) — `src/ycli/yandex/forms/surveys/client.py`
- **SurveysResponse** (2 connections) — `src/ycli/yandex/forms/surveys/client.py`
- **Declarative Forms /surveys client (uplink) — transport ONLY.  NOTE: no ``from __** (1 connections) — `src/ycli/yandex/forms/surveys/client.py`
- **Declarative HTTP for ``/surveys`` (list envelope + single get).** (1 connections) — `src/ycli/yandex/forms/surveys/client.py`
- **``GET /surveys`` → raw ``SurveysResponse`` envelope (internal).** (1 connections) — `src/ycli/yandex/forms/surveys/client.py`
- **``GET /surveys`` → flat :class:`SurveyList`.          Example:             >>> c** (1 connections) — `src/ycli/yandex/forms/surveys/client.py`

## Relationships

- [[Forms Questions Client]] (4 shared connections)
- [[Forms Answers Client]] (1 shared connections)
- [[Pagination and Clients]] (1 shared connections)

## Source Files

- `src/ycli/yandex/forms/surveys/client.py`

## Audit Trail

- EXTRACTED: 21 (81%)
- INFERRED: 5 (19%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*