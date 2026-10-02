"""`forms keysets` commands (reads + writes; download is a binary payload — CLI/SDK only)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.aliases import deprecated_alias
from ycli.cli.output import BinaryResult
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.keysets.models import Keyset, KeysetCreate, KeysetList, KeysetUpdate
from ycli.yandex.forms.typedefs import (
    SurveyIdArg,
)
from ycli.yandex.models import Ack

app = typer.Typer(name="keysets", help="Forms personal-link key sets.", no_args_is_help=True)

KeysetIdArg = Annotated[int, typer.Argument(metavar="KEYSET_ID", help="Key set id (integer).")]
OutputOption = Annotated[
    str | None,
    typer.Option("--output", help="Write bytes to this path; omit / '-' streams to stdout."),
]


@app.command("list")
def list_(survey_id: SurveyIdArg, *, forms: FormsClient) -> KeysetList:
    """List key sets on form SURVEY_ID (GET /surveys/{id}/keysets)."""
    return forms.keysets.list(survey_id)


@app.command()
def get(survey_id: SurveyIdArg, keyset_id: KeysetIdArg, *, forms: FormsClient) -> Keyset:
    """Print one key set (SURVEY_ID KEYSET_ID)."""
    return forms.keysets.get(survey_id, keyset_id)


@app.command()
def create(
    survey_id: SurveyIdArg,
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
    """Create a key set on form SURVEY_ID (POST /surveys/{id}/keysets) — the API requires
    is_enabled, so --enabled/--disabled is required and always sent in the body."""
    body = KeysetCreate(name=name, total=total, is_enabled=enabled).model_dump()
    return forms.keysets.create(survey_id, body=body)


@deprecated_alias(app, "modify")
@app.command()
def update(
    survey_id: SurveyIdArg,
    keyset_id: KeysetIdArg,
    name: Annotated[str, typer.Option(help="Key set name (required — replaces the record).")],
    total: Annotated[int, typer.Option(help="Number of keys (required — replaces the record).")],
    enabled: Annotated[bool, typer.Option("--enabled/--disabled", help="Active flag (required).")],
    *,
    forms: FormsClient,
) -> Keyset:
    """Modify key set KEYSET_ID on SURVEY_ID (PATCH) — the API replaces the whole record, so
    every field (name, total, enabled) is required and sent together."""
    body = KeysetUpdate(name=name, total=total, is_enabled=enabled).model_dump()
    return forms.keysets.modify(survey_id, keyset_id, body=body)


@app.command()
def delete(survey_id: SurveyIdArg, keyset_id: KeysetIdArg, *, forms: FormsClient) -> Ack:
    """Delete key set KEYSET_ID on SURVEY_ID (DELETE /surveys/{id}/keysets/{keyset_id})."""
    forms.keysets.delete(survey_id, keyset_id)
    return Ack.deleted("keyset", keyset_id, from_=f"survey {survey_id}")


@app.command()
def download(
    survey_id: SurveyIdArg,
    keyset_id: KeysetIdArg,
    output: OutputOption = None,
    *,
    forms: FormsClient,
) -> BinaryResult:
    """Download key set KEYSET_ID to --output (or stdout) as raw bytes."""
    return BinaryResult(forms.keysets.download(survey_id, keyset_id), output)
