# Append Content — Wiki API

← Back to [docs.md](../docs.md)

Prefer `append` over a full PATCH when adding a new section at the bottom — it avoids reading and rewriting the entire content:

```bash
# Create body.json first
# body.json: {"content": "\n## New Section\n\nAdded automatically."}
http POST "https://api.wiki.yandex.net/v1/pages/{id}/content/append" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" \
  @body.json
```

The appended content is added after the last character of the existing content. Include a leading `\n` to ensure separation.
