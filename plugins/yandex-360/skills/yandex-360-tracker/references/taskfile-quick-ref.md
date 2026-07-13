# Tracker CLI Quick Reference

All commands run via `uv run ycli tracker …`. Run `uv run ycli tracker --help` to
list resources. Reads **and writes** are also exposed as MCP tools named
`tracker_<resource>_<action>` (e.g. `tracker_issues_get`, `tracker_issues_create`);
write tools carry `readOnlyHint=False` and explicit destructive hints, and
`ycli mcp start --read-only` hides them. Binary downloads are CLI/SDK-only.

Replace placeholders (`MYQUEUE`, `MYQUEUE-123`, `EPIC-1`, `<your-login>`) with your
own queue keys, issue keys, and logins.

```bash
# ----- READ -----

# Single issue (works for any queue you can access)
uv run ycli tracker issues get MYQUEUE-123       # compact view (incl. epic + parent)
uv run ycli tracker issues get MYQUEUE-123 -o json  # raw API dict, every field
uv run ycli tracker comments list MYQUEUE-123
uv run ycli tracker links list MYQUEUE-123
uv run ycli tracker changelog list MYQUEUE-123
uv run ycli tracker worklog list MYQUEUE-123

# Filtered listing — combine any subset of --queue / --status / --assignee / --epic / --type
uv run ycli tracker issues list                                   # all queues you can read
uv run ycli tracker issues list --queue MYQUEUE --status inProgress
uv run ycli tracker issues list --assignee <your-login>
uv run ycli tracker issues list --epic EPIC-1

# Full-text search via Tracker Query Language (TQL)
uv run ycli tracker issues search '"search phrase"'
uv run ycli tracker issues search 'Queue: MYQUEUE AND "search phrase"'

# Count (TQL or filters — no JSON file needed)
uv run ycli tracker issues count --queue MYQUEUE --status inProgress
uv run ycli tracker issues count --query 'Assignee: <your-login>'

# Discover valid enum values (BEFORE building payloads)
uv run ycli tracker priorities list
uv run ycli tracker linktypes list
uv run ycli tracker issuetypes list
uv run ycli tracker transitions list MYQUEUE-123

# ----- WRITE -----

# Create (supply --summary and --description explicitly)
uv run ycli tracker issues create --queue MYQUEUE --summary 'Title' \
  --type improvement --priority normal --parent EPIC-1 \
  --description "$(cat /tmp/desc.md)"

# Arbitrary fields via -F (JSON-coerced, repeatable) — for anything without a named flag
uv run ycli tracker issues update MYQUEUE-123 -F 'epic={"key":"EPIC-1"}'
uv run ycli tracker issues update MYQUEUE-123 --priority critical -F storyPoints=5

# Comment / link / transition
uv run ycli tracker comments add MYQUEUE-123 --text "$(cat comment.md)"
uv run ycli tracker links add MYQUEUE-130 'depends on' MYQUEUE-129
uv run ycli tracker transitions execute MYQUEUE-123 <id> -F 'resolution={"key":"fixed"}'
```

For endpoints the CLI does not cover, consult the live Tracker API reference at
<https://yandex.ru/dev/tracker/> before hand-rolling raw `http`. Prefer the CLI/MCP
tools over raw `http` wherever they cover the operation.
