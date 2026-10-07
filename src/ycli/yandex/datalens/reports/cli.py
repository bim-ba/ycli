"""`datalens reports` commands."""

import json
from collections.abc import Mapping
from typing import Annotated

import typer
from pydantic import BaseModel

from ycli.cli.body_fields import CallerFields
from ycli.cli.typedefs import values_option
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.models import SaveMode
from ycli.yandex.datalens.reports.models import Report, ReportCreated, ReportSaved
from ycli.yandex.datalens.schemas.reports import CreateReportV2Args, UpdateReportV2Args
from ycli.yandex.models import Ack

app = typer.Typer(name="reports", help="DataLens reports.", no_args_is_help=True)

ReportIDArg = Annotated[str, typer.Argument(metavar="ENTRY_ID", help="Report id.")]
DataOption = Annotated[
    str | None,
    typer.Option(
        "--data",
        help="What the report holds, as a JSON object (the `entry.data` of a report read "
        "with `get`); --body-file gives it under `data`.",
    ),
]
MetaOption = Annotated[
    str | None,
    typer.Option(
        "--meta",
        help="Metadata of the entry, as a JSON object or `null`; the API requires it.",
    ),
]
NoteOption = Annotated[
    str | None,
    typer.Option(
        "--annotation", help='A description of the report, as JSON: {"description": "…"}.'
    ),
]


def _body[M: BaseModel](
    model: type[M], caller: CallerFields, flags: Mapping[str, str | bool | None]
) -> M:
    """The request as ``model``: the flags given, over -F, over --body-file.

    A flag is given under the API's name of its field; ``data``, ``meta`` and ``annotation``
    are JSON. The file and ``-F`` give the request itself, so ``workbookId`` in a file reaches
    it like ``--workbook-id``.
    """
    given = {
        name: json.loads(value) if isinstance(value, str) and name in _JSON else value
        for name, value in flags.items()
        if value is not None
    }
    return model.model_validate(caller.over(given))


_JSON = {"data", "meta", "annotation"}


@app.command()
def get(
    entry_id: ReportIDArg,
    rev_id: Annotated[
        str | None,
        typer.Option("--rev-id", help="The revision of the report to read; the current one."),
    ] = None,
    include_permissions: Annotated[
        bool | None,
        typer.Option(
            "--include-permissions/--no-include-permissions",
            help="Also say what you may do with the report.",
        ),
    ] = None,
    include_favorite: Annotated[
        bool | None,
        typer.Option(
            "--include-favorite/--no-include-favorite",
            help="Also say whether the report is a favourite.",
        ),
    ] = None,
    *,
    datalens: DataLensClient,
) -> Report:
    """Print one report: its slides and what stands on them.

    A report has no branch in the API: the read answers the saved version (measured).
    """
    return datalens.reports.get(
        entry_id,
        rev_id=rev_id,
        include_permissions=include_permissions,
        include_favorite=include_favorite,
    )


@app.command()
def create(
    data: DataOption = None,
    meta: MetaOption = None,
    annotation: NoteOption = None,
    include_permissions: Annotated[
        bool | None,
        typer.Option(
            "--include-permissions/--no-include-permissions",
            help="Also say what you may do with the new report.",
        ),
    ] = None,
    key: Annotated[str | None, typer.Option("--key", help="The report's key, in a folder.")] = None,
    workbook_id: Annotated[
        str | None, typer.Option("--workbook-id", help="The workbook to create the report in.")
    ] = None,
    name: Annotated[str | None, typer.Option("--name", help="The report's name.")] = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> ReportCreated:
    """Create a report; the API keeps no `layout` of slide elements and drops some `settings`.

    Measured: a copy made from a report read with `get` loses where its elements stood.
    `data` (with at least one slide) and `meta` are required.
    """
    flags = {
        "data": data,
        "meta": meta,
        "annotation": annotation,
        "includePermissions": include_permissions,
        "key": key,
        "workbookId": workbook_id,
        "name": name,
    }
    body = _body(CreateReportV2Args, caller, flags)
    return datalens.reports.create(
        data=body.data,
        meta=body.meta,
        annotation=body.annotation,
        include_permissions=body.include_permissions,
        key=body.key,
        workbook_id=body.workbook_id,
        name=body.name,
    )


@app.command()
def update(
    entry_id: ReportIDArg,
    mode: Annotated[
        str, values_option(SaveMode, "--mode", help="Keep the report as a draft, or publish it.")
    ],
    data: DataOption = None,
    meta: MetaOption = None,
    rev_id: Annotated[
        str | None,
        typer.Option(
            "--rev-id",
            help="The revision of the report to change; DataLens does not check it (measured).",
        ),
    ] = None,
    annotation: NoteOption = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> ReportSaved:
    """Save a report; it LOSES the `layout` of its slide elements and some `settings`.

    DataLens does not check a revision here: a save overwrites what was saved since you read it
    (measured).

    Measured: DataLens drops them on a save through the API, without a word. Do not save
    a report that exists unless that loss is fine. Otherwise: read it, change it, send it
    back whole.
    """
    flags = {
        "entryId": entry_id,
        "data": data,
        "mode": mode,
        "meta": meta,
        "revId": rev_id,
        "annotation": annotation,
    }
    body = _body(UpdateReportV2Args, caller, flags)
    return datalens.reports.update(
        body.entry_id,
        data=body.data,
        mode=body.mode,
        meta=body.meta,
        rev_id=body.rev_id,
        annotation=body.annotation,
    )


@app.command()
def delete(entry_id: ReportIDArg, *, datalens: DataLensClient) -> Ack:
    """Delete a report."""
    datalens.reports.delete(entry_id)
    return Ack.deleted("report", entry_id)
