---
description: Review the current diff against the ARCHITECTURE.md invariants before merge.
---

Review the working diff (`git diff main...HEAD`) strictly against `ARCHITECTURE.md`. For each
invariant, state PASS/FAIL with file:line evidence:

- ARCH-1 every new resource dir has all five canonical files.
- ARCH-2 no `requests`/`uplink` import in `cli.py`/`mcp.py`/`models.py`.
- ARCH-3 `fastmcp` only in `mcp.py`; new MCP tools are read-only + `readOnlyHint`.
- ARCH-4 no `model_dump_json` outside `output.py`; CLI output via `render`.
- ARCH-5 no hardcoded version/token/org-header outside the sanctioned files.
- ARCH-6 if the CLI tree or MCP tool list changed, `tests/snapshots/` was regenerated AND the
  change is intentional.

Also flag SEMANTIC drift the linters can't see: business logic in `cli.py` that belongs in
`client.py`; a client method bypassing `transport`; a new ad-hoc output path; an asymmetric
resource. If any invariant changed, confirm `ARCHITECTURE.md` was edited in the SAME diff —
if not, that is a FAIL (silent invariant change). End with: APPROVE or REQUEST CHANGES + the
specific fixes.
