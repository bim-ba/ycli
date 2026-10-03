"""`forms filling` commands (get-settings read + submit write + suggest read).

All three also reach MCP (``filling_get`` / ``filling_submit`` / ``filling_suggest``).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.filling.models import FillableForm, SubmitBody, SubmitResult, Suggestion
from ycli.yandex.forms.typedefs import (
    SurveyIdArg,
)
from ycli.yandex.models import ItemList

app = typer.Typer(name="filling", help="Forms form filling.", no_args_is_help=True)

_KEY = typer.Option("--key", help="Personal-link fill key, when the form uses one.")
# Module-level Annotated alias so ``Path`` is referenced at runtime (typer resolves annotations
# via get_type_hints), keeping the import out of a TYPE_CHECKING block.
BodyFileArg = Annotated[
    Path,
    typer.Option(
        "--body-file",
        help="JSON file: an answer map keyed by question slug (see `filling get` values).",
    ),
]


@app.command()
def get(survey: SurveyIdArg, key: Annotated[str, _KEY] = "", *, forms: FormsClient) -> FillableForm:
    """Print the fillable-form settings for SURVEY (GET …/form) — pages, conditions, values."""
    return forms.filling.get(survey, key=key or None)


@app.command()
def submit(
    survey: SurveyIdArg,
    body_file: BodyFileArg,
    validate_only: Annotated[
        bool,
        typer.Option("--validate-only", help="Validate only — save nothing, fire no integrations."),
    ] = False,
    key: Annotated[str, _KEY] = "",
    *,
    forms: FormsClient,
) -> SubmitResult:
    """Submit a form response from --body-file (POST …/form); --validate-only validates only."""
    payload = SubmitBody.model_validate(json.loads(body_file.read_text(encoding="utf-8")))
    return forms.filling.submit(survey, payload, dry_run=validate_only, key=key or None)


@app.command()
def suggest(
    survey: SurveyIdArg,
    question: Annotated[str, typer.Option(help="Question slug the suggestion is for.")] = "",
    text: Annotated[str, typer.Option(help="Text to search suggestions for.")] = "",
    suggest_id: Annotated[
        str, typer.Option("--id", help="Comma-separated suggestion-object ids to resolve.")
    ] = "",
    parent_id: Annotated[
        str, typer.Option("--parent-id", help="Parent ids for a Master/Detail lookup.")
    ] = "",
    *,
    forms: FormsClient,
) -> ItemList[Suggestion]:
    """Get fill suggestions for a question (GET …/suggest)."""
    return forms.filling.suggest(
        survey,
        question=question or None,
        text=text or None,
        suggest_id=suggest_id or None,
        parent_id=parent_id or None,
    )
