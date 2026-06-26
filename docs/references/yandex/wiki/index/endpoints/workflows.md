# Common httpie Workflow Patterns — Wiki API

← Back to [docs.md](../docs.md)

## Pattern 1 — Get page ID from slug, then use it

```bash
PAGE_ID=$(http --print=b GET "https://api.wiki.yandex.net/v1/pages?slug=data/guides/my-page" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" | \
  uv run python -c "import sys,json; print(json.load(sys.stdin).get('id',''))")
echo "Page ID: $PAGE_ID"
```

## Pattern 2 — Get page content, edit, write back

```bash
# 1. Get content
http --print=b GET "https://api.wiki.yandex.net/v1/pages?slug=data/guides/my-page&fields=content" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" | \
  uv run python -c "import sys,json; print(json.load(sys.stdin).get('content',''))" > /tmp/page-content.txt

# 2. Edit /tmp/page-content.txt (agent writes new content)

# 3. Write back (body.json = {"content": "..."})
http PATCH "https://api.wiki.yandex.net/v1/pages/$PAGE_ID" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" \
  @body.json | uv run python -c "import sys,json; d=json.load(sys.stdin); print(d.get('slug',''), 'updated')"
```

## Pattern 3 — List all pages under data/, build slug map

```bash
http --print=b GET "https://api.wiki.yandex.net/v1/pages/descendants?slug=data" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" | \
  uv run python -c "
import sys, json
d = json.load(sys.stdin)
for p in d.get('results', []):
    print(f\"{p['id']}\\t{p['slug']}\\t{p.get('title','?')}\")
" > /tmp/wiki-map.tsv
```

## Pattern 4 — Create a page from a template file

```bash
# Prepare body.json:
# {"title": "New Domain Passport", "slug": "data/domains/parcels", "content": "...YFM..."}
http POST https://api.wiki.yandex.net/v1/pages \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" \
  @body.json | uv run python -c "import sys,json; d=json.load(sys.stdin); print('Created:', d.get('slug'), 'id:', d.get('id'))"
```

## Pattern 5 — Verify page exists before writing

```bash
STATUS=$(http --print=b GET "https://api.wiki.yandex.net/v1/pages?slug=data/guides/target" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" | \
  uv run python -c "import sys,json; d=json.load(sys.stdin); print('exists' if d.get('id') else 'missing')")
if [ "$STATUS" = "exists" ]; then
  echo "Page already exists — will PATCH"
else
  echo "Page missing — will POST"
fi
```
