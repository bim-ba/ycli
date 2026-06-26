# Recovery — Deleted Pages — Wiki API

← Back to [docs.md](../docs.md)

Pages are soft-deleted (moved to trash). Restore within the retention window:

```bash
# body.json: {} (empty body, or specify targetSlug to restore to a different location)
http POST "https://api.wiki.yandex.net/v1/pages/{id}/restore" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" \
  @body.json
```

If the original slug is taken by a new page, specify `targetSlug` in the body to restore to a different slug.
