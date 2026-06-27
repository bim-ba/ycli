---
description: Scaffold a new Yandex resource (client/cli/mcp/models) that satisfies the architecture by construction.
argument-hint: <domain> <resource>
---

Run the generator, then finish wiring:

1. `uv run python scripts/new_endpoint.py $ARGUMENTS`
2. Replace every `FILL` marker in the generated `client.py`/`models.py` with the real
   endpoint path and fields (see `docs/references/yandex/` for the API).
3. Mount the new sub-app into the domain `cli.py` (`app.add_typer(...)`) and the new subserver
   into the domain `mcp.py` (`mcp.mount(...)`), mirroring a sibling resource.
4. Add tests under `tests/yandex/<domain>/<resource>/` (client + cli + mcp) — reads ship across
   SDK+CLI+MCP; keep 100% coverage.
5. Run `uv run pytest`, `uv run lint-imports`, and `uv run python -m tests.snapshots --update`
   (the new commands/tools change the public surface — accept it intentionally).

Architecture rules: see ARCHITECTURE.md. HTTP only in `client.py`; CLI output via
`ycli.output.render`; MCP tools read-only.
