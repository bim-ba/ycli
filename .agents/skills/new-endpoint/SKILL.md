---
name: new-endpoint
description: >-
  Use when scaffolding a new Yandex resource (client/cli/mcp/models) that
  satisfies the architecture by construction; takes a <domain> and <resource>.
---
# New endpoint

Codex has no project-scoped slash commands; this is the skill form of the repo's
`/new-endpoint <domain> <resource>` command, kept in sync with
`.rulesync/commands/new-endpoint.md`.

Given a `<domain>` and `<resource>` from the request:

1. `uv run python scripts/new_endpoint.py <domain> <resource>`
2. Replace every `FILL` marker in the generated `client.py` / `models.py` with the real endpoint
   path and fields. Consult the vendored API docs under `references/yandex-360/<domain>/` (they are
   git-ignored/local-only — regenerate with `uv run python scripts/fetch_docs.py <domain>` if the
   tree is empty).
3. Mount the new sub-app into the domain `cli.py` (`app.add_typer(...)`) and the new subserver into
   the domain `mcp.py` (`mcp.mount(...)`), mirroring a sibling resource.
4. Add tests under `tests/yandex/<domain>/<resource>/` (client + cli + mcp) — every operation
   ships across SDK + CLI + MCP (writes included, honestly annotated); keep the 100% coverage
   gate green.
5. Run `uv run pytest` and `uv run lint-imports`, then regenerate the public-surface snapshots on
   purpose — the new commands/tools change the CLI tree and MCP tool list (ARCH-6):
   `uv run python -m tests.snapshots --update`.

Architecture rules (see `ARCHITECTURE.md`, ARCH-1..11): HTTP only in `client.py`; a CLI command
returns its result and never prints (`output.render` does); `fastmcp` only in `mcp.py`, and every new MCP tool carries
honest annotations (reads `RO`; writes the `WRITE` / `WRITE_IDEMPOTENT` / `DESTRUCTIVE` sets plus
the `write` tag — the tool's verb must classify into the ARCH-3 maps); clients receive credentials
as constructor arguments and never read the environment (no `from_env`).
