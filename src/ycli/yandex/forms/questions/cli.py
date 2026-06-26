"""`forms questions` commands."""
from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.forms._clideps import forms_client

app = typer.Typer(name="questions", help="Forms questions.", no_args_is_help=True)

SurveyIdArg = Annotated[
    str, typer.Argument(metavar="SURVEY_ID", help="Form id, e.g. 6818ceffe010db4f59d11329.")
]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context, survey_id: SurveyIdArg) -> None:
    """List a form's questions (the {pages} envelope)."""
    print(forms_client(ctx).questions.list(survey_id).model_dump_json(by_alias=True))
