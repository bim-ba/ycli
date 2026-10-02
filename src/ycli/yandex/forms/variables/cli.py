"""`forms variables` command: the variable types a form's integrations can reference."""

from __future__ import annotations

import typer

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.typedefs import SurveyIdArg
from ycli.yandex.forms.variables.models import VariableInfoList

app = typer.Typer(
    name="variables", help="Variables available to a form's integrations.", no_args_is_help=True
)


@app.command("list")
def list_(survey_id: SurveyIdArg, *, forms: FormsClient) -> VariableInfoList:
    """List the variable types integrations of form SURVEY_ID can reference."""
    return forms.variables.list(survey_id)
