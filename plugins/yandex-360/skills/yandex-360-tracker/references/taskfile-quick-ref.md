# Tracker CLI Quick Reference

All commands run via `uv run ycli tracker …`. Run `uv run ycli tracker --help` to
list resources. Reads **and writes** are also exposed as MCP tools named
`tracker_<resource>_<action>` (e.g. `tracker_issues_get`, `tracker_issues_create`);
write tools carry `readOnlyHint=False` and explicit destructive hints, and
`ycli mcp start --read-only` hides them. Binary downloads and `attachments import-for-comment` are CLI/SDK-only.

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

# Comments, links, attachments, structure
uv run ycli tracker comments get MYQUEUE-123 <comment-id> --expand all
uv run ycli tracker links list-filtered MYQUEUE-123 --type relates
uv run ycli tracker attachments get MYQUEUE-123 <file-id>
uv run ycli tracker components list-for-queue MYQUEUE
uv run ycli tracker queues user-permissions-get MYQUEUE <login>
uv run ycli tracker queues group-permissions-get MYQUEUE <group-id>
uv run ycli tracker triggers list MYQUEUE
uv run ycli tracker workflows list
uv run ycli tracker workflows list-for-queue MYQUEUE
uv run ycli tracker entities permissions-get-direct project <id>

# ----- WRITE -----

# Create (supply --summary and --description explicitly)
uv run ycli tracker issues create --queue MYQUEUE --summary 'Title' \
  --type improvement --priority normal --parent EPIC-1 \
  --description "$(cat /tmp/desc.md)"

# Arbitrary fields via -F (JSON-coerced, repeatable) — for anything without a named flag
uv run ycli tracker issues update MYQUEUE-123 -F 'epic={"key":"EPIC-1"}'
uv run ycli tracker issues update MYQUEUE-123 --priority critical -F storyPoints=5

# Comment / link / transition
uv run ycli tracker comments create MYQUEUE-123 --text "$(cat comment.md)"
uv run ycli tracker links create MYQUEUE-130 'depends on' MYQUEUE-129
uv run ycli tracker transitions execute MYQUEUE-123 <id> -F 'resolution={"key":"fixed"}'

# Files: attach to an issue, or upload a temp file (id works once, for attachmentIds)
uv run ycli tracker attachments upload MYQUEUE-123 ./report.pdf
uv run ycli tracker attachments upload-temp ./report.pdf
uv run ycli tracker attachments delete MYQUEUE-123 <file-id>

# Org-wide / admin writes — confirm first (workflows and projects need the current --version)
uv run ycli tracker workflows update <id> --version 3 --name "New name"
uv run ycli tracker components delete <id>
uv run ycli tracker queues versions-update <id> --due-date 2026-12-31
uv run ycli tracker filters delete <id>
uv run ycli tracker gaps create --user <login> --workflow vacation --from 2026-07-01T00:00Z --to 2026-07-15T00:00Z
uv run ycli tracker entities permissions-update-direct project <id> --grant '{"READ":{"users":["<login>"]}}'
```

For endpoints the CLI does not cover, consult the live Tracker API reference at
<https://yandex.ru/dev/tracker/> before hand-rolling raw `http`. Prefer the CLI/MCP
tools over raw `http` wherever they cover the operation.
