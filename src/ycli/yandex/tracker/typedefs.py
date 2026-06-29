"""Shared tracker CLI argument type aliases."""

from __future__ import annotations

from typing import Annotated

import typer

KeyArg = Annotated[str, typer.Argument(metavar="KEY", help="Issue key, e.g. DATAENGINEERING-1.")]
