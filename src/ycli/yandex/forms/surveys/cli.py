"""`forms surveys` commands."""
from __future__ import annotations

from typing import Annotated

import typer

from ycli.cliformat import output_format
from ycli.output import render

from ycli.yandex.forms._clideps import forms_client

app = typer.Typer(name="surveys", help="Forms surveys.", no_args_is_help=True)

SurveyIdArg = Annotated[
    str, typer.Argument(metavar="SURVEY_ID", help="Form id, e.g. 6818ceffe010db4f59d11329.")
]


@app.command("list")
def list_(ctx: typer.Context) -> None:
    """List all forms (the {links, result} envelope)."""
    render(forms_client(ctx).surveys.list(), output_format=output_format(ctx))


@app.command()
def get(ctx: typer.Context, survey_id: SurveyIdArg) -> None:
    """Print one form's settings for SURVEY_ID."""
    render(forms_client(ctx).surveys.get(survey_id), output_format=output_format(ctx))
