"""`forms variables` command: the variable types a form's integrations can reference."""

import typer

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.typedefs import SurveyIDArg
from ycli.yandex.forms.variables.models import VariableInfo
from ycli.yandex.models import ItemList

app = typer.Typer(
    name="variables", help="Variables available to a form's integrations.", no_args_is_help=True
)


@app.command("list")
def list_(survey_id: SurveyIDArg, *, forms: FormsClient) -> ItemList[VariableInfo]:
    """List the variable types integrations of form SURVEY_ID can reference."""
    return forms.variables.list(survey_id)
