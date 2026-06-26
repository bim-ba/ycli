# Common Workflows — Tracker API

← Back to [docs.md](../docs.md)

## Common Workflows (Patterns)

### 1. Create Task + Add Links + Attach File

```bash
# Step 1: Create the issue
ISSUE=$(http --print=b POST 'https://api.tracker.yandex.net/v3/issues/' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID" \
  queue=DATAENGINEERING summary="New pipeline task" type:='{"key":"task"}' priority:='{"key":"normal"}' | \
  jq -r '.key')

# Step 2: Link to a parent epic
http POST "https://api.tracker.yandex.net/v3/issues/$ISSUE/links" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID" \
  relationship=parent object:='{"key":"DATAENGINEERING-10"}'

# Step 3: Attach a file
http POST "https://api.tracker.yandex.net/v3/issues/$ISSUE/attachments/" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID" \
  --form file@spec.md
```

### 2. Search + Bulk Update Priority

```bash
# Step 1: Search for issues matching criteria
KEYS=$(echo '{"filter": {"queue": "DATAENGINEERING", "status": ["open"], "type": "task"}}' | \
  http --print=b POST 'https://api.tracker.yandex.net/v3/issues/_search' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID" | \
  jq -r '[.[].key]')

# Step 2: Bulk update priority
echo "{\"issues\": $KEYS, \"values\": {\"priority\": {\"key\": \"high\"}}}" | \
  http --print=b POST 'https://api.tracker.yandex.net/v3/bulkchange/_update' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID"

# Step 3: Check operation status
# (use the operationId returned above)
http --print=b GET 'https://api.tracker.yandex.net/v3/bulkchange/_status/{operationId}' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID" | \
  jq '.status'
```

### 3. Create Sprint + Add Tasks + Start Sprint

```bash
# Step 1: Create sprint on board 34
SPRINT_ID=$(http --print=b POST 'https://api.tracker.yandex.net/v3/boards/34/sprints' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID" \
  name="Sprint 42" startDate="2026-05-20" endDate="2026-06-03" | jq -r '.id')

# Step 2: Add issues to sprint (via PATCH on each issue)
http PATCH 'https://api.tracker.yandex.net/v3/issues/DATAENGINEERING-100' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID" \
  sprint:="[{\"id\": $SPRINT_ID}]"

# Step 3: Start the sprint
http POST "https://api.tracker.yandex.net/v3/boards/34/sprints/$SPRINT_ID/start" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID"
```

### 4. Set Up Trigger for Auto-Status-Change

```bash
# Create a trigger: when assignee is set on an Open issue, move it to In Progress
echo '{
  "name": "Auto-start on assign",
  "conditions": [
    {"type": "FieldChangedCondition", "field": {"id": "assignee"}, "noMatchBefore": true}
  ],
  "actions": [
    {"type": "Transition", "status": {"key": "inProgress"}}
  ]
}' | http POST 'https://api.tracker.yandex.net/v3/queues/6/triggers/' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID"
```

### 5. Get Queue Trigger Execution Logs

```bash
# List all triggers for queue DATAENGINEERING (ID=6)
http --print=b GET 'https://api.tracker.yandex.net/v3/queues/6/triggers/' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID" | \
  jq '[.[] | {id, name}]'

# Get execution logs for a specific trigger
http --print=b GET 'https://api.tracker.yandex.net/v3/queues/6/triggers/{triggerId}/logs' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID" | \
  jq '.[] | {issueKey: .issue.key, status: .status, error: .error}'
```

### 6. Transition Issue to Done with Resolution

```bash
# Step 1: Get available transitions (NEVER skip)
http --print=b GET 'https://api.tracker.yandex.net/v3/issues/DATAENGINEERING-123/transitions' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID" | \
  jq '[.[] | {id, to: .to.key}]'

# Step 2: Execute the "done" transition
http POST 'https://api.tracker.yandex.net/v3/issues/DATAENGINEERING-123/transitions/{id}/_execute' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID" \
  resolution:='{"key":"successful"}' comment="Delivered and verified in production."
```
