---
description: Review the current diff against the ARCHITECTURE.md invariants before merge.
---

Review the working diff (`git diff main...HEAD`) strictly against `ARCHITECTURE.md`. For each
invariant, state **PASS/FAIL** with `file:line` evidence:

- **ARCH-1 — Four-surface symmetry.** Every new `yandex/<domain>/<resource>/` dir has all five
  canonical files (`__init__.py`, `client.py`, `cli.py`, `mcp.py`, `models.py`). (Carve-out:
  `yandex/status/` and the `ycli/mcp/` server package are cross-cutting, not resource dirs.)
- **ARCH-2 — HTTP confinement.** No `requests` / `uplink` import in `cli.py` / `mcp.py` / `models.py`;
  all HTTP lives in `client.py` / `base.py` / `transport.py`.
- **ARCH-3 — MCP read-only.** `fastmcp` only in `mcp.py` (and the `ycli.mcp` server package). Every
  new tool's verb is in the read-verb allow-list, carries `readOnlyHint` (via `RO`), and no `mcp.py`
  calls a client write method (`.create/.update/.add/.execute/…`).
- **ARCH-4 — Serialization confinement.** `model_dump_json` / `yaml.safe_dump` / `json.dumps` appear
  only in `src/ycli/cli/output.py`; CLI command bodies render model output via
  `output.Serializer.serialize` (carve-outs: a scalar `count` `print`, and binary downloads via
  `ycli.cli.binary.write_output`).
- **ARCH-5 — Single sources of truth.** No hardcoded version literal, `YANDEX_ID_*` token, or
  org-header string in `src/` outside `transport.py` (headers) and `__init__.py` (version).
- **ARCH-6 — Public-surface stability.** If the CLI tree or MCP tool list changed, `tests/snapshots/`
  was regenerated (`uv run python -m tests.snapshots --update`) AND the change is intentional.
- **ARCH-7 — Composition-root DI.** Clients take dependencies as constructor args and never read the
  environment; credentials enter only as `oauth_token` / `organization_id`. No `from_env`.
- **ARCH-8 — Single configuration source.** No direct `os.environ` access and no `BaseSettings`
  subclass outside `src/ycli/settings.py`.
- **ARCH-9 — Typed boundary errors.** Non-2xx raises a typed `YandexError` subclass from the transport
  hook; no surface parses an error body or branches on status outside `transport.py`.
- **ARCH-10 — No shadowing of configurable values.** No hardcoded literal overriding a configured
  value (no `@uplink.timeout`); SDK constructor defaults stay equal to `AppConfig`'s defaults.
- **ARCH-11 — Doc-drift guard.** No purged idiom (`.from_env(`, `session_from_env(`) appears in the
  live user-facing docs; any invariant change edits `ARCHITECTURE.md` in the SAME diff.

Also flag **semantic drift** the linters can't see: business logic in `cli.py` that belongs in
`client.py`; a client method bypassing `transport`; a new ad-hoc output path; an asymmetric resource.
If any invariant changed, confirm `ARCHITECTURE.md` was edited in the same diff — if not, that is a
FAIL (silent invariant change). End with: **APPROVE** or **REQUEST CHANGES** + the specific fixes.
