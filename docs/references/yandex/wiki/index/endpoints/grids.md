# Grids — Full API Workflow — Wiki API

← Back to [docs.md](../docs.md)

1. Create the grid, capture the `id`:

   ```bash
   http POST https://api.wiki.yandex.net/v1/grids \
     "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
     "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" \
     @grid-create.json | uv run python -c "import sys,json; print(json.load(sys.stdin).get('id'))"
   ```

2. Add rows one at a time:

   ```bash
   # body: {"cells": {"task": "Fix pipeline", "status": "Open", "owner": "ivanov"}}
   http POST "https://api.wiki.yandex.net/v1/grids/{gridId}/rows" \
     "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
     "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" \
     @row.json
   ```

3. Embed in a page by putting `{% wgrid id="{gridId}" %}` in the page content.

4. Update a single cell:

   ```bash
   # body: {"value": "In Progress"}
   http PATCH "https://api.wiki.yandex.net/v1/grids/{gridId}/rows/{rowId}/cells/{columnId}" \
     "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
     "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" \
     @cell.json
   ```
