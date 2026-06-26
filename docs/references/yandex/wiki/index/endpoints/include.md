# Include / Transclude — Wiki API

← Back to [docs.md](../docs.md)

Include renders another wiki page inline at the point of insertion:

```text
{{include page="data/shared/team-contacts"}}
```

Rules:

- The referenced page must exist before the including page is published
- Includes are rendered server-side — the content appears live from the source page
- Do NOT include pages from outside `data/` without approval
- Do NOT create circular includes

Full Include conventions: `rules/03-include-usage.md`
