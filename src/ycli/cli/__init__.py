"""The ``ycli`` CLI surface — the Typer root app (``app``), its composition root
(``context``), and output rendering (``output``), grouped as a package.

This ``__init__`` is intentionally empty. Domain ``cli.py`` modules import
``ycli.cli.context`` / ``ycli.cli.output``, which runs this package init; importing the
root ``app`` here would pull in every domain app and form an import cycle. Call sites
reference the modules explicitly instead — ``from ycli.cli.app import app`` and the
console entry point ``ycli.cli.app:main``.
"""
