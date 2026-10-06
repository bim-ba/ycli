"""`forms keysets` commands (reads + writes; download is a binary payload — CLI/SDK only)."""

from typing import Annotated

import typer

from ycli.cli.output import BinaryResult
from ycli.cli.typedefs import OutputOption
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.keysets.models import Keyset, KeysetCreate, KeysetUpdate
from ycli.yandex.forms.typedefs import (
    SurveyIDArg,
)
from ycli.yandex.models import Ack, ItemList

app = typer.Typer(name="keysets", help="Forms personal-link key sets.", no_args_is_help=True)

KeysetIDArg = Annotated[int, typer.Argument(metavar="KEYSET_ID", help="Key set id (integer).")]


@app.command("list")
def list_(survey_id: SurveyIDArg, *, forms: FormsClient) -> ItemList[Keyset]:
    """List key sets on form SURVEY_ID (GET /surveys/{id}/keysets)."""
    return forms.keysets.list(survey_id)


@app.command()
def get(survey_id: SurveyIDArg, keyset_id: KeysetIDArg, *, forms: FormsClient) -> Keyset:
    """Print one key set (SURVEY_ID KEYSET_ID)."""
    return forms.keysets.get(survey_id, keyset_id)


@app.command()
def create(
    survey_id: SurveyIDArg,
    name: Annotated[str, typer.Option(help="Key set name.")],
    total: Annotated[int, typer.Option(help="Number of keys to generate.")],
    enabled: Annotated[
        bool,
        typer.Option(
            "--enabled/--disabled",
            help="Create the set active (required — the API rejects a create without it).",
        ),
    ],
    *,
    forms: FormsClient,
) -> Keyset:
    """Create a key set on form SURVEY_ID; --enabled/--disabled is required.

    ``POST /surveys/{id}/keysets``: the API requires is_enabled, so it is always sent in the body.
    """
    body = KeysetCreate(name=name, total=total, is_enabled=enabled)
    return forms.keysets.create(survey_id, body=body)


@app.command()
def update(
    survey_id: SurveyIDArg,
    keyset_id: KeysetIDArg,
    name: Annotated[str, typer.Option(help="Key set name (required — replaces the record).")],
    total: Annotated[
        int,
        typer.Option(
            help="Number of keys (required — replaces the record); the API refuses a number "
            "smaller than the set has now."
        ),
    ],
    enabled: Annotated[bool, typer.Option("--enabled/--disabled", help="Active flag (required).")],
    *,
    forms: FormsClient,
) -> Keyset:
    """Replace key set KEYSET_ID on SURVEY_ID; every field is required.

    ``PATCH``: the API replaces the whole record, so name, total and enabled are sent together.
    """
    body = KeysetUpdate(name=name, total=total, is_enabled=enabled)
    return forms.keysets.update(survey_id, keyset_id, body=body)


@app.command()
def delete(survey_id: SurveyIDArg, keyset_id: KeysetIDArg, *, forms: FormsClient) -> Ack:
    """Delete key set KEYSET_ID on SURVEY_ID (DELETE /surveys/{id}/keysets/{keyset_id})."""
    forms.keysets.delete(survey_id, keyset_id)
    return Ack.deleted("keyset", keyset_id, from_=f"survey {survey_id}")


@app.command()
def download(
    survey_id: SurveyIDArg,
    keyset_id: KeysetIDArg,
    output: OutputOption = None,
    *,
    forms: FormsClient,
) -> BinaryResult:
    """Download key set KEYSET_ID to --output (or stdout) as raw bytes."""
    return BinaryResult(forms.keysets.download(survey_id, keyset_id), output)
