"""ycli — interact with Yandex 360 services (Wiki, Tracker, Forms, …).

One codebase, many surfaces: a Typer CLI (``ycli``), a FastMCP server (``ycli mcp``),
and an importable Python SDK under ``ycli.yandex``. Distributed on PyPI as ``yandex-cli``.
"""

from __future__ import annotations

import logging
from importlib.metadata import version

# A library never configures logging; it only emits. The CLI and MCP entry points attach a real
# handler (see ``ycli.log``), and a host application may attach its own.
logging.getLogger("ycli").addHandler(logging.NullHandler())

# Single source of truth: the version declared in pyproject.toml (read from installed
# metadata under the distribution name `yandex-cli`).
__version__ = version("yandex-cli")
