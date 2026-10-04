"""Shared wiki CLI argument type aliases."""

from __future__ import annotations

from typing import Annotated

import typer

PageIDArg = Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")]
