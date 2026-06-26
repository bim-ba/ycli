# Async Clone Operations — Wiki API

← Back to [docs.md](../docs.md)

Cloning a subtree is async — never block waiting inline. Always poll:

```bash
# Start clone
OP=$(http --print=b POST "https://api.wiki.yandex.net/v1/pages/{id}/clone" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" \
  @clone.json | uv run python -c "import sys,json; print(json.load(sys.stdin).get('operationId'))")

# Poll — run this in a loop until status != PENDING/IN_PROGRESS
http --print=b GET "https://api.wiki.yandex.net/v1/operations/$OP" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" | \
  uv run python -c "import sys,json; d=json.load(sys.stdin); print(d.get('status'), d.get('error',''))"
```
