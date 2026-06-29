---
date: 2026-06-29
status: APPLIED
disposition: applied
applied_date: 2026-06-29
applied_in: docs/conventions/resources.md (§3), ARCHITECTURE.md
priority: MEDIUM
trigger: 4
session_context: round-3 arch-tooling refactor — MCP server wiring research
affected_source:
  - ARCHITECTURE.md
  - docs/conventions/resources.md
---

## What diverged

During round-3, research into fastmcp's mount API revealed that `mount()` does not propagate
lifespan context (and therefore non-serializable objects like HTTP client sessions) to mounted
subservers. The practical consequence is that the canonical way to share one client instance
across all tools in a mounted MCP domain server is a module-level `@functools.cache` factory:
a `<domain>_client` function in `_deps.py` decorated with `@functools.cache`, accepting
credential arguments, returning the domain client. MCP tool functions consume it via FastMCP's
`Depends(...)` mechanism.

The older `import_server` API is deprecated in fastmcp and was ruled out. The `@cache`
factory is the correct, forward-compatible pattern — but it was arrived at by live research,
not prescribed anywhere in `ARCHITECTURE.md` or `docs/conventions/resources.md`. A future
contributor adding a new domain's MCP server has no documented guide and will have to
rediscover the same non-obvious constraint.

## Why it seemed better

Deferring documentation until the pattern is proven in code is prudent — it avoids
enshrining an approach that might change as fastmcp evolves. The research session confirmed
the pattern works, but it felt premature to update architecture docs mid-implementation.
In hindsight the pattern is stable enough to document immediately.

## Proposed change

Add a subsection to `docs/conventions/resources.md` (under a "MCP wiring" or "Client
factories" heading) and a note in `ARCHITECTURE.md`'s layout prose:

```
### MCP client factories (`_deps.py`)

fastmcp's `mount()` does not propagate lifespan context across server boundaries.
To share one client instance across tools in a mounted domain server, define a
`@functools.cache` factory in `<domain>/_deps.py`:

    @functools.cache
    def tracker_client(oauth_token: str, organization_id: str) -> TrackerClient:
        return TrackerClient(oauth_token=oauth_token, organization_id=organization_id)

MCP tool functions receive the client via `Depends(tracker_client)`. This is the
only approved pattern; `import_server` is deprecated and must not be used.
```

## Resolution

Documented in `docs/conventions/resources.md` §3 ("Why `<domain>_client` is a cached provider")
and in the `ARCHITECTURE.md` layout prose (the `_mcp.py` line). The codified docs reflect the
pattern as it actually shipped: each `_deps` calls `make_cached_client(ClientCls)` from
`ycli.yandex._mcp` — a helper that wraps a `functools.cache`d zero-arg factory and reads
`Credentials()` from the env once — rather than the raw per-module `@functools.cache def`
sketched in the proposal above. The rationale (fastmcp `mount()` not propagating lifespan
context; `import_server` deprecated) and the `Depends(...)` consumption are unchanged.
