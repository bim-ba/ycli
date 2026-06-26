# Yandex Tracker — Reference

Normalized 1:1 mirror of the Yandex Tracker API + product documentation (HTML→MD), relocated from the
`yandex-360-tracker` skill in sub-project G/M2. Leaf files keep their vendor filenames (URL-traceable);
navigate via [`index/docs.md`](index/docs.md) or `rg` over this tree.

## Layout

- `01-overview/` … `18-api/` — the vendor docs by topic section (18 directories; `18-api/` is the
  canonical REST reference).
- [`index/docs.md`](index/docs.md) — curated navigation guide to the sections + endpoint map
  (`index/endpoints/`).
- [`service-map.md`](service-map.md) — workflow/status reference for our Tracker usage.

> The `uv run ycli tracker …` CLI cheatsheet stays in the skill
> (`.claude/skills/yandex-360-tracker/references/taskfile-quick-ref.md`) — it is agent-operational, not
> vendor documentation.
