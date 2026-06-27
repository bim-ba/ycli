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
  tool wraps a read (no `create/update/add/execute/delete/set/remove`) and carries
  `readOnlyHint=True` (via the `RO` annotation).
- **ARCH-4 — Output discipline.** CLI results render through `ycli.output.render`;
  `model_dump_json` may appear only in `src/ycli/output.py`. (Raw passthroughs like
  `json.dumps(raw)`, `print(count)`, `.content` are intentional and allowed.)
- **ARCH-5 — Single sources of truth.** No hardcoded version literal, `YANDEX_ID_*` token, or
  org-header string in `src/` outside `transport.py` (headers) and `__init__.py` (version, read
  from `importlib.metadata`).
- **ARCH-6 — Public-surface stability.** The CLI command tree and MCP tool list change only by
  regenerating the snapshots in `tests/snapshots/` on purpose.

## Changing an invariant

These are deliberate, not incidental. To change one: edit this file **and** its enforcing check
(in `tests/test_architecture.py`, `pyproject.toml`, or the snapshots) **in the same PR**, and say
so in the PR body. A reviewer (human or `/arch-review`) should reject a surface/structure change
that isn't reflected here.
