# Yandex service reference docs — local-only

This directory mirrors vendored Yandex **service** documentation (Tracker, Wiki, Forms and
the wider dev hub) that the platform references. **The docs themselves are not committed.**

They are served from `yandex.ru`, which is covered by the Yandex User Agreement — not an open
licence — so redistributing them in this repository isn't permitted. We therefore keep them
**local-only (gitignored)** and regenerate them on demand from a committed, reproducible
source: [`scripts/fetch_docs.py`](../../../scripts/fetch_docs.py).

## Regenerate locally

```bash
uv run python scripts/fetch_docs.py --all       # every diplodoc-served service
uv run python scripts/fetch_docs.py tracker     # a single service
uv run python scripts/fetch_docs.py wiki --dry-run
```

Output mirrors each service's URL path 1:1 under this directory. Run the script with `--help`
for the full service list and `--lang {ru,en,all}`.

## Yandex Cloud docs (CC BY 4.0)

The open-source Yandex Cloud documentation (`github.com/yandex-cloud/docs`) *is* openly
licensed (CC BY 4.0) and may be redistributed with attribution — it is handled separately from
this local-only tree. Fetch it with `scripts/fetch_docs.py <service> --source cloud`.
