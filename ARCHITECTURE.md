# Architecture

`ycli` exposes one SDK four ways (CLI, MCP server, Python SDK, Claude Code plugin).
Its strength is a regular, symmetric layout — and that regularity is enforced, not hoped for.
These invariants are checked by `tests/test_architecture.py`, import-linter (`pyproject.toml`),
and `tests/test_snapshots.py`. A failing build names the violated invariant.

## Layout

```
src/ycli/
├── cli.py · mcp.py · output.py · log.py     # roots
└── yandex/
    ├── base.py · transport.py               # shared HTTP/session
    └── <domain>/                            # tracker · wiki · forms
        ├── _base.py · _deps.py · _clideps.py · client.py · cli.py · mcp.py
        └── <resource>/                      # issues · pages · surveys · …
            ├── client.py   # uplink SDK — the ONLY place HTTP happens
            ├── cli.py      # Typer — output via ycli.output.render
            ├── mcp.py      # FastMCP read-only tools
            ├── models.py   # pydantic
            └── __init__.py
```

## Invariants

- **ARCH-1 — Four-surface symmetry.** Every `yandex/<domain>/<resource>/` directory contains
  `__init__.py`, `client.py`, `cli.py`, `mcp.py`, `models.py`. Use `/new-endpoint` to scaffold.
- **ARCH-2 — HTTP confinement.** `cli.py`, `mcp.py`, and `models.py` never import `requests` or
  `uplink`. All HTTP lives in `client.py` / `base.py` / `transport.py`.
- **ARCH-3 — MCP is read-only.** `fastmcp` is imported only in modules named `mcp.py`. Every MCP
  tool's verb (last `_`-segment of its name) must be in a fail-closed read-verb **allow-list**
  (`get/list/count/full/search/descendants/meta` — a new read adds its verb deliberately), it
  carries `readOnlyHint=True` (via the `RO` annotation), and no `mcp.py` may call a client write
  method (`.create/.update/.add/.execute/…`).
- **ARCH-4 — Output discipline.** CLI results render through `ycli.output.render`;
  `model_dump_json` may appear only in `src/ycli/output.py`. (Raw passthroughs like
  `json.dumps(raw)`, `print(count)`, `.content` are intentional and allowed.)
- **ARCH-5 — Single sources of truth.** No hardcoded version literal, `YANDEX_ID_*` token, or
  org-header string in `src/` outside `transport.py` (headers) and `__init__.py` (version, read
  from `importlib.metadata`).
- **ARCH-6 — Public-surface stability.** The CLI command tree and MCP tool list change only by
  regenerating the snapshots in `tests/snapshots/` on purpose.

## Scope & limits of enforcement

The checks are guardrails, not a proof. Known boundaries (the `/arch-review` rubric and human
review cover the rest):

- **ARCH-2/ARCH-3 catch _direct_ imports** (`allow_indirect_imports=true`, since `cli.py`/`mcp.py`
  legitimately reach HTTP transitively through `client.py`). An HTTP call hidden behind a new
  helper module that `cli.py` imports is not caught by import-linter.
- **ARCH-5 is single-source-of-truth, not secret scanning.** It catches hardcoded `__version__`,
  `YANDEX_ID_*` assignments, and org-header strings — not an arbitrary raw token literal (that is
  the job of the token-leak guard, a separate piece of work).
- **ARCH-6 locks names, not signatures.** A tool/command keeping its name while changing its
  parameters, description, or return type does not trip the snapshot.

## Changing an invariant

These are deliberate, not incidental. To change one: edit this file **and** its enforcing check
(in `tests/test_architecture.py`, `pyproject.toml`, or the snapshots) **in the same PR**, and say
so in the PR body. A reviewer (human or `/arch-review`) should reject a surface/structure change
that isn't reflected here.
