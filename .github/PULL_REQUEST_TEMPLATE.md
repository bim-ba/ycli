## What

Brief description of the change.

## Checklist

- [ ] `uv run pytest` passes (coverage stays at 100%)
- [ ] Reads ship across SDK + CLI + MCP; writes across SDK + CLI only
- [ ] No MCP write tool added (server is read-only by design)
- [ ] No secrets / real org data committed
- [ ] Docs updated if behavior or coverage changed
