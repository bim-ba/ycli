# Descendants Navigation — Wiki API

← Back to [docs.md](../docs.md)

`/v1/pages/descendants` returns the entire subtree recursively. For large trees, use `depth` to limit:

```bash
# Top 2 levels only
http --print=b GET "https://api.wiki.yandex.net/v1/pages/descendants?slug=data&depth=2" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" | \
  uv run python -c "
import sys, json
d = json.load(sys.stdin)
for p in d.get('results', []):
    print(p['slug'], '—', p.get('title', '?'))
"
```

`children-by-slug` returns only direct children (depth=1), which is faster for large trees when you only need the next level.
