# Yandex Wiki — Reference

Normalized 1:1 mirror of the Yandex Wiki API + product documentation (HTML→MD), including YFM syntax,
relocated from the `yandex-360-wiki` skill in sub-project G/M2. Leaf files keep their vendor filenames
(URL-traceable); navigate via [`index/docs.md`](index/docs.md) or `rg` over this tree.

## Layout

- `01-overview/` … `07-api/` — the vendor docs by topic section (7 directories; `05-edit-page/` = the
  full YFM syntax + Include element, `07-api/` = API auth/errors/base-URLs).
- [`index/docs.md`](index/docs.md) — curated navigation guide + endpoint map (`index/endpoints/`).
- [`yfm-quick-ref.md`](yfm-quick-ref.md) — inline YFM quick reference.

> Maps of OUR `data/` wiki space (`service-map.md`, `index/wiki-structure.md`) stay in the
> `yandex-360-wiki` skill — they are agent-private, not vendor documentation.
