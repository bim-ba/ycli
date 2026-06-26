---
name: tracker-queues-index
description: Reference for all Yandex Tracker queues in the organization — data team queues with full conventions, others as lookup
type: index
---

# Tracker Queues — Organization Reference

## Data Team Queues (full skill coverage)

| Queue | Key | Purpose | Primary board | Workflow |
|-------|-----|---------|--------------|---------|
| Data Engineering | `DATAENGINEERING` | Core data platform: pipelines, models, infra, quality | Board 34 | Full 9-status workflow |
| Ad-hoc | `ADHOC` | One-off data requests from business | Board 37 | Simplified |
| BI | `BI` | BI reports and dashboards | Board 10 | Standard |
| BI Reports | `BIREPORTS` | Formal report delivery queue | — | Standard |
| Data Product | `DATAPRODUCT` | Cross-team data product initiatives | Board 32 | Full workflow |

**For all data team queues:** issue naming conventions, SP estimation, and lifecycle rules from `rules/` apply.

## Other Organization Queues (lookup only)

| Queue | Key | Owner | Board | Notes |
|-------|-----|-------|-------|-------|
| UNI Fast Track | `UFT` | Product team | — | Fast-track feature delivery |
| CS Unilog | `CSUNILOG` | Customer Service | 44 | CS operations |
| UT-UNI | `UTUNI` | UT-UNI team | 64 | UT-UNI specific work |
| Test | `TEST` | Internal | — | Testing only, ignore |

## How to Find Any Queue

```bash
http --print=b GET 'https://api.tracker.yandex.net/v3/queues?perPage=50' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID" | \
  jq '[.[] | {key: .key, name: .name}]'
```
