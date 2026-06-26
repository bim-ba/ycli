# 40 — External / Vendor References

Normalized, offline copies of **external** vendor documentation that the platform integrates with —
kept here (not inside `.claude/skills/`) so the team can browse and `rg` them directly. Skills link
here rather than holding the canonical copy (see
[`../20-conventions/08-documentation-governance.md`](../20-conventions/08-documentation-governance.md)).

## Contents

- [`yandex/`](yandex/) — Yandex 360 service docs (Tracker, Forms, Wiki) — API + product reference,
  normalized from the raw HTML→MD scrape. Populated by sub-project G/M2 from the `yandex-360-*` skill
  references.

> Files here follow the `NN-<slug>.md` numbering rule. For a large vendor corpus the prefixes are a
> stable ordering for convention-compliance, not a semantic sequence.
