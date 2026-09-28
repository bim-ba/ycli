---
name: page-structure
description: Conventions for creating and naming Yandex Wiki pages — slug rules, title/H1 matching, and the page preamble standard
type: rule
---

# Rule: Page Structure

## Slug Conventions

- Format: `kebab-case`, hierarchy expressed through `/` (e.g. `team/guides/how-to-use-api`, `team/incidents/2026-05-db-outage`).
- Do **not** use: spaces, underscores, or Cyrillic characters in slugs.
- A slug is a **permanent URL** — never change it after publication. Changing a slug breaks every inbound link and Tracker magic-link reference.
- Decide the full slug (including parent path) before publishing the page.

## Page Title and H1

- The page's `# H1` heading should match the title shown in navigation (the `--title` you pass to the CLI).
- Use the reader's natural language for prose; keep technical identifiers (slugs, code, table names) in their canonical form.

## Page Preamble Standard

Open each page with a short, scannable preamble:

1. A **status note block** indicating page state, e.g.
   `{% note info "Status: Production" %}{% endnote %}` for stable content, or
   `{% note warning "Status: Draft" %}{% endnote %}` for in-progress content.
2. A **Tracker magic link** to the driving issue, if applicable — just type the bare issue key (e.g. `QUEUE-42`); it auto-renders as a card.
3. An **"Updated"** date.

Example:

```text
{% note info "Status: Production" %}{% endnote %}

QUEUE-42

_Updated: 2026-05-15_
```

## Do Not Duplicate Content

- Link to source code, dbt docs, or configuration in its repository instead of copying it into a page.
- A link that may need updating is better than a copy that silently goes stale.
