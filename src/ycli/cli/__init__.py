"""The ``ycli`` CLI surface — the Typer root app, its composition root, and output rendering.

Grouped as a package (mirroring ``ycli.mcp``) so the CLI-only modules live together: ``root``
(the Typer command tree + console entry point), ``context`` (``AppContext``, the CLI
composition root), and ``output`` (the ``--format`` serializer).

``__init__`` stays import-light: domain ``cli.py`` modules import ``ycli.cli.context`` /
``ycli.cli.output``, which would trigger this package init, so eagerly importing ``root`` here
(it imports every domain app) would be circular. ``app`` and ``main`` resolve lazily on
attribute access instead, preserving ``ycli.cli:main`` (the console script) and
``from ycli.cli import app`` for every call site.
"""

from __future__ import annotations

from typing import Any

__all__ = ["app", "main"]


def __getattr__(name: str) -> Any:
    if name in {"app", "main"}:
        from ycli.cli import root

        return getattr(root, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
