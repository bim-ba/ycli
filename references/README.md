# references/ — external Yandex documentation

Vendored, offline copies of **external** Yandex documentation the platform references. Kept out of
[`docs/`](../docs/) — which holds *this repo's own* docs — so external material can be browsed and
`rg`-ed without polluting the project's documentation tree.

## Layout

- **[`yandex-360/`](yandex-360/)** — Yandex 360 + dev-hub service docs (Tracker, Wiki, Forms, Disk,
  Telemost, ID, Metrika, Direct, …). Served from `yandex.ru` under the Yandex User Agreement (**not**
  an open licence), so they are **not committed** — the tree is gitignored and regenerated locally
  from a reproducible source: [`scripts/fetch_docs.py`](../scripts/fetch_docs.py).

- **`yandex-cloud/`** — the open-source Yandex Cloud documentation, vendored as a **git submodule** of
  [`github.com/yandex-cloud/docs`](https://github.com/yandex-cloud/docs) (© YANDEX LLC, licensed
  **CC BY 4.0**). Only a pinned pointer is committed; the ~1.4 GB of content is fetched on demand:

  ```bash
  git submodule update --init --depth 1 references/yandex-cloud
  ```

  Clones and CI do **not** pull it unless asked (no `--recursive`), so the repo stays lean.
