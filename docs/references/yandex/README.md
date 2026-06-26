# Yandex 360 — Service References

Normalized offline reference for the Yandex 360 services the platform automates against. Source of
truth for "how does Tracker/Forms/Wiki work" — the `yandex-360-{tracker,forms,wiki}` skills link
here. Org-wide `rg` over these docs replaces the old in-skill `references/docs/` corpus.

(Distinct from `operational/yandex/wiki/` — that is the read-only mirror of other teams' wiki
*content*; this is the vendor *product/API* documentation.)

## Services

- [`tracker/`](tracker/) — Yandex Tracker API + product docs (385 files, 18 sections).
- [`forms/`](forms/) — Yandex Forms API + product docs (110 files, 9 sections).
- [`wiki/`](wiki/) — Yandex Wiki API + product docs incl. YFM (111 files, 7 sections).

> 1:1 mirrors relocated from the `yandex-360-*` skills in sub-project G/M2. Agent-private maps (our
> CLI cheatsheet, our `data/`-space maps) stayed in the skills.
