"""Shared forms CLI argument type aliases."""

from __future__ import annotations

from typing import Annotated

import typer

SurveyIdArg = Annotated[
    str, typer.Argument(metavar="SURVEY_ID", help="Form id, e.g. 6818ceffe010db4f59d11329.")
]
