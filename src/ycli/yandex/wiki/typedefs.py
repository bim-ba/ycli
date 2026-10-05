"""Shared wiki CLI argument type aliases."""

from typing import Annotated

import typer

PageIDArg = Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")]
