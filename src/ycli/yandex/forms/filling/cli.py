"""`forms filling` commands (get-settings read + submit write + suggest read).

All three also reach MCP (``filling_get`` / ``filling_submit`` / ``filling_suggest``).
"""

from typing import Annotated

import typer

from ycli.cli.body_fields import CallerFields
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.filling.models import FillableForm, SubmitBody, SubmitResult, Suggestion
from ycli.yandex.forms.typedefs import (
    SurveyIDArg,
)
from ycli.yandex.models import ItemList

app = typer.Typer(name="filling", help="Forms form filling.", no_args_is_help=True)

_KEY = typer.Option("--key", help="Personal-link fill key, when the form uses one.")


@app.command()
def get(
    survey_id: SurveyIDArg, key: Annotated[str | None, _KEY] = None, *, forms: FormsClient
) -> FillableForm:
    """Print the fillable-form settings for SURVEY (GET …/form) — pages, conditions, values."""
    return forms.filling.get(survey_id, key=key)


@app.command()
def submit(
    survey_id: SurveyIDArg,
    validate_only: Annotated[
        bool | None,
        typer.Option(
            "--validate-only/--no-validate-only",
            help="Validate only — save nothing, fire no integrations.",
        ),
    ] = None,
    key: Annotated[str | None, _KEY] = None,
    *,
    caller: CallerFields,
    forms: FormsClient,
) -> SubmitResult:
    """Submit a form response from --body-file and -F (POST …/form).

    The answers are a map keyed by question slug (see ``filling get``); --validate-only saves
    nothing.
    """
    if not caller.given:
        # violation(arch-9): the answers have no flags of their own, so with neither option
        # there is no body to send
        raise typer.BadParameter(
            "give the answers with --body-file or -F", param_hint="--body-file / -F"
        )
    payload = SubmitBody.model_validate(caller.over({}))
    return forms.filling.submit(survey_id, payload, validate_only=validate_only, key=key)


@app.command()
def suggest(
    survey_id: SurveyIDArg,
    question: Annotated[
        str | None, typer.Option(help="Question slug the suggestion is for.")
    ] = None,
    text: Annotated[str | None, typer.Option(help="Text to search suggestions for.")] = None,
    suggest_id: Annotated[
        str | None,
        typer.Option("--suggest-id", help="Comma-separated suggestion-object ids to resolve."),
    ] = None,
    parent_id: Annotated[
        str | None, typer.Option("--parent-id", help="Parent ids for a Master/Detail lookup.")
    ] = None,
    *,
    forms: FormsClient,
) -> ItemList[Suggestion]:
    """Get fill suggestions for a question (GET …/suggest)."""
    return forms.filling.suggest(
        survey_id,
        question=question,
        text=text,
        suggest_id=suggest_id,
        parent_id=parent_id,
    )
