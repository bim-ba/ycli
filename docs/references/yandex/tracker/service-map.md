---
name: tracker-service-map
description: Live map of DATAENGINEERING queue — statuses, transitions, issue types, naming conventions, SP scale, active state snapshot
type: reference
---

# Yandex Tracker — DATAENGINEERING Service Map

## Queue

| Field | Value |
|-------|-------|
| Key | `DATAENGINEERING` |
| ID | 6 |
| Lead | znatnov.s |
| Boards | 32 «Data: All», 34 «Data: Data Engineering» (primary) |
| Default type | Task |
| Default priority | Normal |

## Workflow

```text
Open → Backlog → In Progress → Testing → Review → Done
              ↕           ↕          ↕
          Need Info    Blocked  (Review → In Progress on reject)
          Cancelled  Cancelled   Cancelled
```

## Statuses

| Status | Type | Key | Purpose |
|--------|------|-----|---------|
| Open | new | `open` | Arrived from form, not triaged |
| Backlog | new | `backlog` | Triaged, waiting for pickup |
| In Progress | inProgress | `inProgress` | Active development |
| Testing | inProgress | `testing` | Internal QA / data validation |
| Review | paused | `review` | Stakeholder acceptance |
| Need Info | paused | `needInfo` | Waiting for requirements |
| Blocked | paused | `blocked` | External technical blocker |
| Done | done | `closed` | Accepted and closed |
| Cancelled | cancelled | `cancelled` | Cancelled |

## Transitions

| From | To | Required |
|------|----|----------|
| Open | Backlog | — |
| Open | Cancelled | Comment |
| Backlog | In Progress | Assignee, End Date |
| Backlog | Need Info | — |
| Backlog | Cancelled | Comment |
| In Progress | Testing | — |
| In Progress | Need Info | Comment |
| In Progress | Blocked | Comment |
| In Progress | Cancelled | Comment |
| Testing | In Progress | — |
| Testing | Review | Comment (test results) |
| Review | Done | Resolution |
| Review | In Progress | Comment |
| Need Info | Backlog | — |
| Need Info | In Progress | — |
| Need Info | Cancelled | Comment |
| Blocked | In Progress | — |
| Blocked | Cancelled | — |

> To find available transitions for an issue in an unknown status:
> `GET /v3/issues/{key}/transitions`

## Issue Types

| Type | Key | When to Use |
|------|-----|-------------|
| Task | `task` | Small discrete items without user story |
| Bug | `bug` | Broken pipeline, DQ issue, dbt model error |
| Incident | `incident` | Production incident affecting SLA |
| Story | `story` | User-facing feature: dashboard, report, pipeline |
| Epic | `epic` | Large theme grouping multiple Stories |
| Improvement | `improvement` | Enhancement to existing pipeline/model/process |
| Refactoring | `refactoring` | Technical debt, code quality, migrations |

## Naming Conventions

| Type | Format | Example |
|------|--------|---------|
| Bug | `[BUG] component: description` | `[BUG] parcels pipeline: null values in status_code` |
| Incident | `[INCIDENT] description` | `[INCIDENT] ClickHouse OOM — mart__parcels unavailable` |
| Story | verb + noun phrase | `Добавить дашборд оборачиваемости WB` |
| Epic | `[DOMAIN] theme` | `[PARCELS] Tracking pipeline refactor` |
| Task / Improvement / Refactoring | Imperative phrase | `Мигрировать stg__parcels в новые конвенции` |

## Story Points (Fibonacci)

| SP | Effort | ✅ Use For | ❌ Don't Use For |
|----|--------|-----------|-----------------|
| 1 | < 2h | Fix column name, add computed field | Tasks with exploration |
| 2 | Half day | Add filter to DataLens, update mart SQL | Unfamiliar area |
| 3 | 1 day | New staging model from existing source | Two independent components — split |
| 5 | 2–3 days | New mart with joins + DQ tests | Something done 10× — lower to 2–3 |
| 8 | 1 week | New CDC pipeline, domain dbt refactor | Org-level coordination baked in |
| 13 | 1–2 weeks | Full stg layer refactor, new service | Tasks without clear acceptance criteria |
| 21 | > 2 weeks | **STOP — decompose into subtasks** | Any SP=21 task |

**Rules**: Estimate complexity & uncertainty, not calendar time. SP=0 doesn't exist. SP≥13 without subtasks = red flag.

## Field Requirements

| Field | When Required | Notes |
|-------|--------------|-------|
| Priority | Always | Critical / High / Normal / Low |
| Assignee | Before In Progress | Set when picking up |
| Story Points | Mandatory for Story & Epic | Optional for others |
| End Date | On → In Progress | Expected completion date |
| Tags | As needed | See tags below |
| Epic | Story: mandatory; Task: optional | Link to parent |
| Resolution | On → Done | Successful / Fixed / Don't do / Can't reproduce |

## Tags

`clickhouse` `dbt` `kafka` `dagster` `api` `airflow`

## Resolution Values

| Resolution | When |
|-----------|------|
| `Successful` | Feature completed and accepted |
| `Fixed` | Bug fixed and verified |
| `Don't do` | Deprioritized or out of scope |
| `Can't reproduce` | Bug unconfirmable |
