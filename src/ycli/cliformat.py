"""Resolve the root ``--format`` option from any (nested) command Context — DI, no global."""
from __future__ import annotations

import typer

from ycli.output import OutputFormat


def output_format(ctx: typer.Context) -> OutputFormat:
    """Return the ``--format`` chosen on the root app (defaults to ``auto``)."""
    chosen = ctx.find_root().params.get("output_format", OutputFormat.auto)
    return chosen if isinstance(chosen, OutputFormat) else OutputFormat(chosen)
