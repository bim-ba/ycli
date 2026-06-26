"""ycli — interact with Yandex 360 services (Wiki, Tracker, Forms, …).

One codebase, many surfaces: a Typer CLI (``ycli``), a FastMCP server (``ycli-mcp``),
and an importable Python SDK under ``ycli.yandex``.
"""

from __future__ import annotations

from importlib.metadata import version

# Single source of truth: the version declared in pyproject.toml (read from installed metadata).
__version__ = version("ycli")
