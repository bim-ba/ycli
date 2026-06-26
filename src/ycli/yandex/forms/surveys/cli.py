"""`forms surveys` commands."""
from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.forms._clideps import forms_client

app = typer.Typer(name="surveys", help="Forms surveys.", no_args_is_help=True)

SurveyIdArg = Annotated[
    str, typer.Argument(metavar="SURVEY_ID", help="Form id, e.g. 6818ceffe010db4f59d11329.")
]


@app.command("list")
def list_(ctx: typer.Context) -> None:
    """List all forms (the {links, result} envelope)."""
    print(forms_client(ctx).surveys.list().model_dump_json(by_alias=True))


@app.command()
def get(ctx: typer.Context, survey_id: SurveyIdArg) -> None:
    """Print one form's settings for SURVEY_ID."""
    print(forms_client(ctx).surveys.get(survey_id).model_dump_json(by_alias=True))
