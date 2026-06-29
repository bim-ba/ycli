"""The ``ycli mcp`` surface — the read-only FastMCP server plus its CLI sub-app.

``__init__`` stays import-light so the base install (no ``mcp`` extra) can load
``ycli.mcp.cli`` without importing fastmcp; ``mcp`` and ``main`` resolve lazily on
attribute access, preserving ``from ycli.mcp import mcp, main`` for every call site.
"""

from __future__ import annotations

from typing import Any

__all__ = ["main", "mcp"]


def __getattr__(name: str) -> Any:
    if name in {"mcp", "main"}:
        from ycli.mcp import server

        return getattr(server, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
