# Pages CRUD — Wiki API

← Back to [docs.md](../docs.md)

**Critical rule:** Content is NOT returned by default. Always append `&fields=content` when you need it.

**WRONG — content missing:**

```text
GET /v1/pages?slug=data/guides/my-page
```

**CORRECT — content returned:**

```text
GET /v1/pages?slug=data/guides/my-page&fields=content
```

**WRONG — endpoint does not exist:**

```text
GET /v1/pages/get-by-slug?slug=data/guides/my-page   ← returns 404
```

**WYSIWYG pages** contain control characters in their content field. Always parse with uv run python, never use jq on content.

**Page ID vs slug:** Most write operations (`PATCH`, `DELETE`, `copy`, `move`, `restore`, `clone`, comments, attachments) require the numeric or UUID page ID. Use a GET by slug to resolve it first.
