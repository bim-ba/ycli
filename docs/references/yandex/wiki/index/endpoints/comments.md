# Comments — Wiki API

← Back to [docs.md](../docs.md)

Comments appear in the page UI discussion panel. Use for annotating pages without changing content.

```bash
# List comments
http --print=b GET "https://api.wiki.yandex.net/v1/pages/{id}/comments" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" | \
  uv run python -c "import sys,json; [print(c['id'], c.get('text','')[:60]) for c in json.load(sys.stdin).get('results',[])]"

# Add a comment: body.json = {"text": "Reviewed by agent on 2026-05-17"}
http POST "https://api.wiki.yandex.net/v1/pages/{id}/comments" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" \
  @body.json
```
