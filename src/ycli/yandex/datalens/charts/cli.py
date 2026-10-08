"""`datalens charts` commands."""

import json
from typing import Annotated

import typer
from pydantic import BaseModel

from ycli.cli.body_fields import CallerFields
from ycli.cli.typedefs import values_option
from ycli.yandex.datalens.charts.models import (
    ChartData,
    EditorChart,
    EditorChartCreated,
    EditorChartSaved,
    QLChart,
    QLChartCreated,
    QLChartSaved,
    WizardChart,
    WizardChartCreated,
    WizardChartSaved,
)
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.models import RevisionBranch, SaveMode
from ycli.yandex.datalens.schemas.editor import CreateEditorChartArgs, UpdateEditorChartArgs
from ycli.yandex.datalens.schemas.ql import CreateQLChartArgs, UpdateQLChartArgs
from ycli.yandex.datalens.schemas.wizard import CreateWizardChartV1Args, UpdateWizardV1Args
from ycli.yandex.models import Ack

app = typer.Typer(name="charts", help="DataLens charts.", no_args_is_help=True)
wizard_app = typer.Typer(name="wizard", help="Charts built in the wizard.", no_args_is_help=True)
ql_app = typer.Typer(name="ql", help="QL charts.", no_args_is_help=True)
editor_app = typer.Typer(name="editor", help="Charts written in the editor.", no_args_is_help=True)
app.add_typer(wizard_app)
app.add_typer(ql_app)
app.add_typer(editor_app)

ChartIDArg = Annotated[str, typer.Argument(metavar="CHART_ID", help="Chart id.")]
ChartWorkbookOption = Annotated[
    str | None, typer.Option("--workbook-id", help="The workbook the chart lies in.")
]
RevisionOption = Annotated[
    str | None,
    typer.Option("--rev-id", help="One revision to read, as it is; give it or --branch, not both."),
]
ChartPermissionsOption = Annotated[
    bool | None,
    typer.Option(
        "--include-permissions/--no-include-permissions", help="Also say what you may do with it."
    ),
]
LinksOption = Annotated[
    bool | None,
    typer.Option("--include-links/--no-include-links", help="Also say what it is linked to."),
]
FavoriteOption = Annotated[
    bool | None,
    typer.Option(
        "--include-favorite/--no-include-favorite", help="Also say whether it is a favourite."
    ),
]
BranchOption = Annotated[
    str | None,
    values_option(
        RevisionBranch,
        "--branch",
        help="The version to read when no revision is named: saved or published. A save writes "
        "the saved one: read `saved` before you change a chart.",
    ),
]
ModeOption = Annotated[
    str, values_option(SaveMode, "--mode", help="Keep the change as a draft, or publish it.")
]
TemplateOption = Annotated[
    str,
    typer.Option("--template", help="The template of the chart; the API takes only ql today."),
]
QL_DATA_HELP = (
    "What the chart holds, as a JSON object (its query and how it is shown); --body-file "
    "gives it under `data`."
)
ENTRY_HELP = (
    "The chart, as a JSON object; `type` says which kind it is. --body-file gives it under `entry`."
)


def _body[M: BaseModel](model: type[M], caller: CallerFields, flags: dict[str, str | None]) -> M:
    """The request as ``model``: the flags given, over -F, over --body-file.

    A flag is given under the API's name of its field; one that holds JSON (``data``,
    ``annotation``, ``entry``) is parsed. The file and ``-F`` give the request itself, so
    ``workbookId`` in a file reaches the request like ``--workbook-id``; a field the request
    needs and nobody gave is named in the error.
    """
    given = {
        name: json.loads(value) if name in {"data", "annotation", "entry"} else value
        for name, value in flags.items()
        if value is not None
    }
    return model.model_validate(caller.over(given))


@app.command("data-get")
def data_get(
    chart_id: ChartIDArg,
    params: Annotated[
        str | None,
        typer.Option(
            "--params",
            help='Values for the chart\'s parameters, as a JSON object: {"year": "2026", '
            '"city": ["Moscow", "Kazan"]}.',
        ),
    ] = None,
    *,
    datalens: DataLensClient,
) -> ChartData:
    """Print the data a saved chart shows, as tables; a pivot table is not supported.

    A chart of the editor with no source did not answer within the client's wait: the command
    ends with a timeout after about two minutes (measured, twice).
    """
    return datalens.charts.data_get(chart_id, params=None if params is None else json.loads(params))


@wizard_app.command("get")
def wizard_get(
    chart_id: ChartIDArg,
    workbook_id: ChartWorkbookOption = None,
    rev_id: RevisionOption = None,
    include_permissions: ChartPermissionsOption = None,
    include_links: LinksOption = None,
    include_favorite: FavoriteOption = None,
    branch: BranchOption = None,
    *,
    datalens: DataLensClient,
) -> WizardChart:
    """Print one chart of the wizard: its datasets and what it shows."""
    return datalens.charts.wizard_get(
        chart_id,
        workbook_id=workbook_id,
        rev_id=rev_id,
        include_permissions=include_permissions,
        include_links=include_links,
        include_favorite=include_favorite,
        branch=branch,
    )


@wizard_app.command("create")
def wizard_create(
    data: Annotated[
        str | None,
        typer.Option(
            "--data",
            help="What the chart holds, as a JSON object (the `entry.data` of a chart read "
            "with `get`); --body-file gives it under `data`.",
        ),
    ] = None,
    annotation: Annotated[
        str | None,
        typer.Option("--annotation", help='A description, as a JSON object: {"description": "…"}.'),
    ] = None,
    key: Annotated[str | None, typer.Option("--key", help="The entry's key, in a folder.")] = None,
    workbook_id: Annotated[
        str | None, typer.Option("--workbook-id", help="The workbook to create it in.")
    ] = None,
    name: Annotated[str | None, typer.Option("--name", help="The chart's name.")] = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> WizardChartCreated:
    """Create a chart of the wizard.

    --body-file (and -F) give the request itself: `data`, `workbookId`, `name`; a flag
    lies over them. `data` is required: the `entry.data` of a chart read with `get`.
    """
    body = _body(
        CreateWizardChartV1Args,
        caller,
        {
            "data": data,
            "annotation": annotation,
            "key": key,
            "workbookId": workbook_id,
            "name": name,
        },
    )
    return datalens.charts.wizard_create(
        body.data,
        annotation=body.annotation,
        key=body.key,
        workbook_id=body.workbook_id,
        name=body.name,
    )


@wizard_app.command("update")
def wizard_update(
    chart_id: ChartIDArg,
    mode: ModeOption,
    data: Annotated[
        str | None,
        typer.Option(
            "--data",
            help="What the chart holds, as a JSON object; --body-file gives it under `data`.",
        ),
    ] = None,
    annotation: Annotated[
        str | None,
        typer.Option("--annotation", help='A description, as a JSON object: {"description": "…"}.'),
    ] = None,
    rev_id: Annotated[
        str | None,
        typer.Option(
            "--rev-id",
            help="The revision the change is made on; DataLens does not check it (measured).",
        ),
    ] = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> WizardChartSaved:
    """Save a chart of the wizard as given: read it, change it, send it back whole.

    DataLens does not check a revision here: a save overwrites what was saved since you read it
    (measured).

    `data` is required, from --data or under `data` of --body-file.
    """
    body = _body(
        UpdateWizardV1Args,
        caller,
        {
            "chartId": chart_id,
            "mode": mode,
            "data": data,
            "annotation": annotation,
            "revId": rev_id,
        },
    )
    return datalens.charts.wizard_update(
        body.chart_id,
        mode=body.mode.root,
        data=body.data,
        annotation=body.annotation,
        rev_id=body.rev_id,
    )


@wizard_app.command("delete")
def wizard_delete(chart_id: ChartIDArg, *, datalens: DataLensClient) -> Ack:
    """Delete a chart of the wizard; dashboards that show it lose it.

    The API has no way to bring it back, and a dashboard that shows it keeps naming its
    id (measured).

    The interface lists what was deleted under Service settings, Deleted objects, with a
    Restore button (measured: the entry appears there; restoring was not tried).
    """
    datalens.charts.wizard_delete(chart_id)
    return Ack.deleted("chart", chart_id)


@ql_app.command("get")
def ql_get(
    chart_id: ChartIDArg,
    workbook_id: ChartWorkbookOption = None,
    rev_id: RevisionOption = None,
    include_permissions: ChartPermissionsOption = None,
    include_links: LinksOption = None,
    include_favorite: FavoriteOption = None,
    branch: BranchOption = None,
    *,
    datalens: DataLensClient,
) -> QLChart:
    """Print one QL chart: its keys come flat, with no `entry` around them."""
    return datalens.charts.ql_get(
        chart_id,
        workbook_id=workbook_id,
        rev_id=rev_id,
        include_permissions=include_permissions,
        include_links=include_links,
        include_favorite=include_favorite,
        branch=branch,
    )


@ql_app.command("create")
def ql_create(
    template: TemplateOption,
    data: Annotated[str | None, typer.Option("--data", help=QL_DATA_HELP)] = None,
    annotation: Annotated[
        str | None,
        typer.Option("--annotation", help='A description, as a JSON object: {"description": "…"}.'),
    ] = None,
    key: Annotated[str | None, typer.Option("--key", help="The entry's key, in a folder.")] = None,
    workbook_id: Annotated[
        str | None, typer.Option("--workbook-id", help="The workbook to create it in.")
    ] = None,
    name: Annotated[str | None, typer.Option("--name", help="The chart's name.")] = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> QLChartCreated:
    """Create a QL chart; --body-file and -F give the request itself, `data` is required."""
    body = _body(
        CreateQLChartArgs,
        caller,
        {
            "template": template,
            "data": data,
            "annotation": annotation,
            "key": key,
            "workbookId": workbook_id,
            "name": name,
        },
    )
    return datalens.charts.ql_create(
        template=body.template,
        data=body.data,
        annotation=body.annotation,
        key=body.key,
        workbook_id=body.workbook_id,
        name=body.name,
    )


@ql_app.command("update")
def ql_update(
    entry_id: Annotated[str, typer.Argument(metavar="ENTRY_ID", help="Chart id.")],
    template: TemplateOption,
    mode: ModeOption,
    data: Annotated[str | None, typer.Option("--data", help=QL_DATA_HELP)] = None,
    annotation: Annotated[
        str | None,
        typer.Option("--annotation", help='A description, as a JSON object: {"description": "…"}.'),
    ] = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> QLChartSaved:
    """Save a QL chart as given; `data` is required, from --data or --body-file.

    DataLens does not check a revision here: a save overwrites what was saved since you read it
    (measured).
    """
    body = _body(
        UpdateQLChartArgs,
        caller,
        {
            "entryId": entry_id,
            "template": template,
            "mode": mode,
            "data": data,
            "annotation": annotation,
        },
    )
    return datalens.charts.ql_update(
        body.entry_id,
        template=body.template,
        mode=body.mode.root,
        data=body.data,
        annotation=body.annotation,
    )


@ql_app.command("delete")
def ql_delete(chart_id: ChartIDArg, *, datalens: DataLensClient) -> Ack:
    """Delete a QL chart; dashboards that show it lose it."""
    datalens.charts.ql_delete(chart_id)
    return Ack.deleted("chart", chart_id)


@editor_app.command("get")
def editor_get(
    chart_id: ChartIDArg,
    workbook_id: ChartWorkbookOption = None,
    rev_id: RevisionOption = None,
    include_permissions: ChartPermissionsOption = None,
    include_links: LinksOption = None,
    include_favorite: FavoriteOption = None,
    branch: BranchOption = None,
    *,
    datalens: DataLensClient,
) -> EditorChart:
    """Print one chart of the editor: its kind and its code."""
    return datalens.charts.editor_get(
        chart_id,
        workbook_id=workbook_id,
        rev_id=rev_id,
        include_permissions=include_permissions,
        include_links=include_links,
        include_favorite=include_favorite,
        branch=branch,
    )


@editor_app.command("create")
def editor_create(
    entry: Annotated[str | None, typer.Option("--entry", help=ENTRY_HELP)] = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> EditorChartCreated:
    """Create a chart of the editor from --entry or --body-file."""
    return datalens.charts.editor_create(
        _body(CreateEditorChartArgs, caller, {"entry": entry}).entry
    )


@editor_app.command("update")
def editor_update(
    mode: ModeOption,
    entry: Annotated[str | None, typer.Option("--entry", help=ENTRY_HELP)] = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> EditorChartSaved:
    """Save a chart of the editor as given; `entryId` in the entry says which.

    DataLens does not check a revision here: a save overwrites what was saved since you read it
    (measured).
    """
    body = _body(UpdateEditorChartArgs, caller, {"entry": entry, "mode": mode})
    return datalens.charts.editor_update(body.entry, mode=body.mode)


@editor_app.command("delete")
def editor_delete(chart_id: ChartIDArg, *, datalens: DataLensClient) -> Ack:
    """Delete a chart of the editor; dashboards that show it lose it."""
    datalens.charts.editor_delete(chart_id)
    return Ack.deleted("chart", chart_id)
