# yandex-360/ — local-only service docs

Vendored Yandex 360 + dev-hub service documentation (Tracker, Wiki, Forms and the wider dev hub).
**The docs themselves are not committed** — they are served from `yandex.ru`, covered by the Yandex
User Agreement (not an open licence), so redistributing them here isn't permitted. The tree is
**gitignored (local-only)** and regenerated on demand from a committed, reproducible source:
[`scripts/fetch_docs.py`](../../scripts/fetch_docs.py).

## Regenerate locally

```bash
uv run python scripts/fetch_docs.py --all       # every diplodoc-served service
uv run python scripts/fetch_docs.py tracker     # a single service
uv run python scripts/fetch_docs.py wiki --dry-run
```

Output mirrors each service's URL path 1:1 under this directory. Run the script with `--help` for the
full service list and `--lang {ru,en,all}`.

> The CC-BY Yandex Cloud docs live next door in [`../yandex-cloud/`](../yandex-cloud) as a git
> submodule — see [`../README.md`](../README.md).
