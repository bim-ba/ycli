# Attachments and Upload Sessions — Wiki API

← Back to [docs.md](../docs.md)

Upload a file to a page in three steps:

```bash
# Step 1 — start session; body: {"filename": "arch.png", "mimeType": "image/png"}
SESSION=$(http --print=b POST "https://api.wiki.yandex.net/v1/pages/{id}/attachments/upload-session" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" \
  @start.json | uv run python -c "import sys,json; d=json.load(sys.stdin); print(d['sessionId'], d['uploadUrl'])")

# Step 2 — PUT binary to uploadUrl (use http or curl for binary upload)
# Step 3 — commit
http POST "https://api.wiki.yandex.net/v1/pages/{id}/attachments/upload-session/{sessionId}/commit" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID"
```

After committing, the file appears in the page's attachment list. Reference it in YFM content using a standard markdown link where the URL part has the `attachment:` prefix followed by the filename — e.g., a link to `invoice.pdf` uses the URL `attachment:invoice.pdf`.
