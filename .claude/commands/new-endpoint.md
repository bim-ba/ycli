---
description: >-
  Scaffold a new Yandex resource (client/cli/mcp/models) that satisfies the
  architecture by construction.
argument-hint: <domain> <resource>
---
Run the generator, then finish wiring the new resource:

1. `uv run python scripts/new_endpoint.py $ARGUMENTS`
2. Replace every `FILL` marker in the generated `endpoints.py` / `client.py` / `models.py` with
   the real paths, operations and fields: each operation is declared once in `endpoints.py`
   (`Endpoint`, or `Paged` for a listing) and the `Resource` client sends it —
   `tracker/issues/` is the worked example. Consult the vendored API docs under
   `references/yandex-360/<domain>/` (they are git-ignored/local-only — regenerate with
   `uv run python scripts/fetch_docs.py <domain>` if the tree is empty).
3. Register the resource in the domain client's `_wire(self, session)`
   (`self.<resource> = <Resource>Client(session=session)`: the domain's one core session is
   handed to it), then mount the
   new sub-app into the domain `cli.py` (`app.add_typer(...)`) and the new subserver into the
   domain `mcp.py` (`mcp.mount(...)`), mirroring a sibling resource.
4. Add `tests/unit/yandex/<domain>/<resource>/cases.py`: one contract `Case` per way of reaching
   each operation through the SDK, CLI and MCP, with distinct literal values
   (`docs/conventions/testing.md`). Hand-write tests only for what a case cannot reach (errors,
   multi-step flows, guards); keep the 100% coverage gate green.
5. Run `uv run pytest` and `uv run lint-imports`, then regenerate the public-surface snapshots on
   purpose — the new commands/tools change the CLI tree and MCP tool list (ARCH-6):
   `uv run python -m tests.snapshots --update`.

The rules the result must meet are in `ARCHITECTURE.md` (ARCH-1..9) and
`docs/conventions/resources.md`; the scaffold already meets them, and `uv run pytest` names the
one a change breaks.
