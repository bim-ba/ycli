"""ycli — interact with Yandex 360 services (Wiki, Tracker, Forms, …).

One codebase, many surfaces: a Typer CLI (``ycli``), a FastMCP server (``ycli mcp``),
and an importable Python SDK under ``ycli.yandex``. Distributed on PyPI as ``yandex-cli``.
"""

import logging

# A library never configures logging; it only emits. The CLI and MCP entry points attach a real
# handler (see ``ycli.log``), and a host application may attach its own.
logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> str:
    """``ycli.__version__``, read on first access: ``importlib.metadata`` is slow to import.

    Single source of truth: the version declared in pyproject.toml (installed metadata under
    the distribution name ``yandex-cli``).
    """
    if name == "__version__":
        from importlib.metadata import version

        return version("yandex-cli")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
