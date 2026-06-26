---
name: wiki-include-usage
description: Rules for using the YFM include element to avoid content duplication
type: rule
---

# Rule: Include Usage

## What Include Is

The `include` element in Yandex Wiki allows embedding the content of one page into another. Use it to maintain DRY (Don't Repeat Yourself) content across multiple pages.

Syntax:

```text
{{include page="your-space/shared/team-contacts"}}
```

## When to Use Include

Use Include when:

- The same content block appears on 3 or more pages (team contacts, standard disclaimers, common procedures)
- Content needs to stay in sync across pages (ownership tables, SLA definitions)
- A page serves as a shared library of definitions or terms

Do NOT use Include when:

- The content is similar but contextually different on each page — write it per-page instead
- The included page would need different rendering in different contexts
- The page is only referenced from one or two places — copy-paste is fine at that scale

## How to Structure Shared Content Pages

Keep shared content under a dedicated parent slug (e.g. `your-space/shared/`):

- `your-space/shared/team-contacts` — team member contacts and roles
- `your-space/shared/glossary` — terminology definitions
- `your-space/shared/sla-definitions` — SLA tiers and what they mean

Naming convention: `your-space/shared/{topic-name}` — keep shared pages flat, no deep nesting.

## Include Syntax Reference

**Basic include** (embeds the entire page):

```text
{{include page="your-space/shared/team-contacts"}}
```

**Include with heading override:**

```text
{{include page="your-space/shared/team-contacts" title="Team"}}
```

Note: The included page content is rendered at the include point. The included page itself is a valid wiki page and will also appear in navigation on its own.

## DRY Principle Applied to Wiki

Before writing the same content a second time, ask:

1. Will this content need to stay in sync across pages? → use Include
2. Is this content a stable reference (team roster, glossary, SLA tiers)? → candidate for a shared page
3. Is this content only slightly similar, not identical? → do not force DRY, write per-page

A wiki that is too DRY becomes hard to navigate — too many includes cause readers to lose context when they land on a page mid-task. Balance DRY with readability. A page should be useful on its own even when an include fails to render.
