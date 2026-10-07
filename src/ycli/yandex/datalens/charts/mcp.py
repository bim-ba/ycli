"""DataLens charts FastMCP tools (read-only) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.datalens.charts.models import (
    ChartData,
    EditorChart,
    EditorChartCreate,
    EditorChartCreated,
    EditorChartSaved,
    EditorChartUpdate,
    EntryAnnotation,
    QLChart,
    QLChartChange,
    QLChartCreated,
    QLChartData,
    QLChartSaved,
    WizardChart,
    WizardChartCreated,
    WizardChartData,
    WizardChartSaved,
)
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    OverBudget,
    PermissionsInfo,
    datalens_client,
    new_server,
)
from ycli.yandex.datalens.models import RevisionBranch, SaveMode
from ycli.yandex.models import Ack

mcp = new_server("datalens-charts")

ChartID = Annotated[str, Field(description="Chart id.")]
ChartWorkbook = Annotated[str | None, Field(description="The workbook the chart lies in.")]
Revision = Annotated[
    str | None, Field(description="One revision to read, as it is; give it or `branch`, not both.")
]
WithLinks = Annotated[bool | None, Field(description="Also say what it is linked to.")]
WithFavorite = Annotated[
    bool | None, Field(description="Also say whether it is a favourite of the caller.")
]
Branch = Annotated[
    RevisionBranch | None,
    Field(
        description="The version to read when no revision is named: `saved` or `published`. A "
        "save writes the saved one: read `saved` before changing a chart."
    ),
]
Mode = Annotated[
    SaveMode, Field(description="`save` keeps a draft; `publish` makes it the version shown.")
]
Annotation = Annotated[EntryAnnotation | None, Field(description="A description of the chart.")]
WIZARD_DATA = "ycli.yandex.datalens.charts.models:WizardChartData"
Template = Annotated[
    str, Field(description="The template of the chart; the API takes only `ql` today.")
]


@mcp.tool(name="charts_data_get", annotations={**RO, "title": "Read the data of a DataLens chart"})
def data_get(
    chart_id: ChartID,
    params: Annotated[
        dict[str, str | list[str]] | None,
        Field(description="Values for the chart's parameters, by name: one value or several."),
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> ChartData:
    """The data a saved chart shows, as tables of columns and rows.

    The chart runs with its saved settings. ``chartType`` says how it is built (``wizard``,
    ``ql``, ``editor``). A pivot table is not supported, and a chart whose source cannot be
    reached answers with an error.
    ``entries_list`` with the scope ``widget`` finds charts.
    """
    return client.charts.data_get(chart_id, params=params)


@mcp.tool(name="charts_wizard_get", annotations={**RO, "title": "Get DataLens wizard chart"})
def wizard_get(
    chart_id: ChartID,
    workbook_id: ChartWorkbook = None,
    rev_id: Revision = None,
    include_permissions: PermissionsInfo = None,
    include_links: WithLinks = None,
    include_favorite: WithFavorite = None,
    branch: Branch = None,
    client: DataLensClient = Depends(datalens_client),
) -> WizardChart:
    """One chart built in the wizard: the datasets it reads and what it shows.

    ``entry.data`` is what ``charts_wizard_update`` takes back; ``isFavorite`` and
    ``permissions`` come only when asked for. ``entries_list`` with the scope
    ``widget`` finds charts; its ``type`` says how a chart is built.
    """
    return client.charts.wizard_get(
        chart_id,
        workbook_id=workbook_id,
        rev_id=rev_id,
        include_permissions=include_permissions,
        include_links=include_links,
        include_favorite=include_favorite,
        branch=branch,
    )


@mcp.tool(
    name="charts_wizard_create", annotations={**WRITE, "title": "Create DataLens wizard chart"}
)
def wizard_create(
    data: Annotated[
        WizardChartData,
        OverBudget(WIZARD_DATA, "What the chart holds: `sources` and `visualization`."),
    ],
    annotation: Annotation = None,
    key: Annotated[str | None, Field(description="The entry's key, in a folder.")] = None,
    workbook_id: Annotated[str | None, Field(description="The workbook to create it in.")] = None,
    name: Annotated[str | None, Field(description="The chart's name.")] = None,
    client: DataLensClient = Depends(datalens_client),
) -> WizardChartCreated:
    """Create a chart of the wizard in a workbook and return it with its id.

    The ``entry.data`` of a chart read with ``charts_wizard_get`` is a valid ``data``.
    """
    return client.charts.wizard_create(
        data, annotation=annotation, key=key, workbook_id=workbook_id, name=name
    )


@mcp.tool(
    name="charts_wizard_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update DataLens wizard chart"},
)
def wizard_update(
    chart_id: ChartID,
    mode: Mode,
    data: Annotated[
        WizardChartData,
        OverBudget(WIZARD_DATA, "What the chart holds; it replaces the whole of it."),
    ],
    annotation: Annotation = None,
    rev_id: Annotated[
        str | None,
        Field(
            description="The revision the change is made on; DataLens does not check it (measured)."
        ),
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> WizardChartSaved:
    """Save a chart of the wizard as given: read it, change it, send it back whole.

    DataLens does not check a revision here: a save overwrites what was saved since you read it
    (measured).
    """
    return client.charts.wizard_update(
        chart_id, mode=mode, data=data, annotation=annotation, rev_id=rev_id
    )


@mcp.tool(
    name="charts_wizard_delete",
    annotations={**DESTRUCTIVE, "title": "Delete DataLens wizard chart"},
)
def wizard_delete(chart_id: ChartID, client: DataLensClient = Depends(datalens_client)) -> Ack:
    """Delete a chart; the dashboards that show it lose it.

    The API has no way to bring it back, and a dashboard that shows it keeps naming its id
    (measured).
    """
    client.charts.wizard_delete(chart_id)
    return Ack.deleted("chart", chart_id)


@mcp.tool(name="charts_ql_get", annotations={**RO, "title": "Get DataLens QL chart"})
def ql_get(
    chart_id: ChartID,
    workbook_id: ChartWorkbook = None,
    rev_id: Revision = None,
    include_permissions: PermissionsInfo = None,
    include_links: WithLinks = None,
    include_favorite: WithFavorite = None,
    branch: Branch = None,
    client: DataLensClient = Depends(datalens_client),
) -> QLChart:
    """One QL chart. Unlike a chart of the wizard it comes flat, with no ``entry`` around it."""
    return client.charts.ql_get(
        chart_id,
        workbook_id=workbook_id,
        rev_id=rev_id,
        include_permissions=include_permissions,
        include_links=include_links,
        include_favorite=include_favorite,
        branch=branch,
    )


@mcp.tool(name="charts_ql_create", annotations={**WRITE, "title": "Create DataLens QL chart"})
def ql_create(
    template: Template,
    data: Annotated[
        QLChartData, Field(description="What the chart holds: its query and how it is shown.")
    ],
    annotation: Annotation = None,
    key: Annotated[str | None, Field(description="The entry's key, in a folder.")] = None,
    workbook_id: Annotated[str | None, Field(description="The workbook to create it in.")] = None,
    name: Annotated[str | None, Field(description="The chart's name.")] = None,
    client: DataLensClient = Depends(datalens_client),
) -> QLChartCreated:
    """Create a QL chart; the reply is what DataLens answers, as it came.

    The specification describes neither the content of a QL chart nor the reply.
    """
    return client.charts.ql_create(
        template=template,
        data=data,
        annotation=annotation,
        key=key,
        workbook_id=workbook_id,
        name=name,
    )


@mcp.tool(
    name="charts_ql_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update DataLens QL chart"},
)
def ql_update(
    entry_id: Annotated[str, Field(description="Chart id.")],
    template: Template,
    mode: Mode,
    data: Annotated[
        QLChartChange, Field(description="What the chart holds; it replaces the whole of it.")
    ],
    annotation: Annotation = None,
    client: DataLensClient = Depends(datalens_client),
) -> QLChartSaved:
    """Save a QL chart as given; the reply is what DataLens answers, as it came.

    DataLens does not check a revision here: a save overwrites what was saved since you read it
    (measured).
    """
    return client.charts.ql_update(
        entry_id, template=template, mode=mode, data=data, annotation=annotation
    )


@mcp.tool(
    name="charts_ql_delete",
    annotations={**DESTRUCTIVE, "title": "Delete DataLens QL chart"},
)
def ql_delete(chart_id: ChartID, client: DataLensClient = Depends(datalens_client)) -> Ack:
    """Delete a chart; the dashboards that show it lose it."""
    client.charts.ql_delete(chart_id)
    return Ack.deleted("chart", chart_id)


@mcp.tool(name="charts_editor_get", annotations={**RO, "title": "Get DataLens editor chart"})
def editor_get(
    chart_id: ChartID,
    workbook_id: ChartWorkbook = None,
    rev_id: Revision = None,
    include_permissions: PermissionsInfo = None,
    include_links: WithLinks = None,
    include_favorite: WithFavorite = None,
    branch: Branch = None,
    client: DataLensClient = Depends(datalens_client),
) -> EditorChart:
    """One chart written in the editor: its kind (``entry.type``) and its tabs of code."""
    return client.charts.editor_get(
        chart_id,
        workbook_id=workbook_id,
        rev_id=rev_id,
        include_permissions=include_permissions,
        include_links=include_links,
        include_favorite=include_favorite,
        branch=branch,
    )


@mcp.tool(
    name="charts_editor_create", annotations={**WRITE, "title": "Create DataLens editor chart"}
)
def editor_create(
    entry: Annotated[
        EditorChartCreate,
        Field(description="The new chart: where it lies, its kind (`type`) and its code."),
    ],
    client: DataLensClient = Depends(datalens_client),
) -> EditorChartCreated:
    """Create a chart of the editor and return it with its id."""
    return client.charts.editor_create(entry)


@mcp.tool(
    name="charts_editor_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update DataLens editor chart"},
)
def editor_update(
    entry: Annotated[
        EditorChartUpdate,
        Field(description="The chart to save: its `entryId`, its kind (`type`) and its code."),
    ],
    mode: Mode,
    client: DataLensClient = Depends(datalens_client),
) -> EditorChartSaved:
    """Save a chart of the editor as given.

    DataLens does not check a revision here: a save overwrites what was saved since you read it
    (measured).
    """
    return client.charts.editor_update(entry, mode=mode)


@mcp.tool(
    name="charts_editor_delete",
    annotations={**DESTRUCTIVE, "title": "Delete DataLens editor chart"},
)
def editor_delete(chart_id: ChartID, client: DataLensClient = Depends(datalens_client)) -> Ack:
    """Delete a chart; the dashboards that show it lose it."""
    client.charts.editor_delete(chart_id)
    return Ack.deleted("chart", chart_id)
