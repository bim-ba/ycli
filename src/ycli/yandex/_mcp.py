"""Shared FastMCP tool annotations — de-dupes the per-domain _deps.py copies."""

from __future__ import annotations

RO: dict[str, bool] = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True}
