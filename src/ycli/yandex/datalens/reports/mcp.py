"""DataLens reports FastMCP tools (read + write) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    OverBudget,
    PermissionsInfo,
    datalens_client,
)
from ycli.yandex.datalens.models import SaveMode
from ycli.yandex.datalens.reports.models import (
    EntryAnnotation,
    Report,
    ReportCreated,
    ReportData,
    ReportMeta,
    ReportSaved,
)
from ycli.yandex.models import Ack

mcp = FastMCP("datalens-reports")

ReportID = Annotated[str, Field(description="Report id.")]
Data = Annotated[
    ReportData,
    OverBudget(
        "ycli.yandex.datalens.reports.models:ReportData",
        "What the report holds: its slides and its settings; it replaces the whole of it.",
    ),
]
Meta = Annotated[
    ReportMeta | None, Field(description="Metadata of the entry; null for none. Required.")
]
Note = Annotated[EntryAnnotation | None, Field(description="A description of the report.")]


@mcp.tool(name="reports_get", annotations={**RO, "title": "Get DataLens report"})
def get(
    entry_id: ReportID,
    rev_id: Annotated[
        str | None,
        Field(description="The revision of the report to read; the current when left out."),
    ] = None,
    include_permissions: PermissionsInfo = None,
    include_favorite: Annotated[
        bool | None, Field(description="Also say whether the report is a favourite.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> Report:
    """One report: its slides and the charts and texts on them.

    ``entry.data`` and ``entry.meta`` are what ``reports_update`` takes back.
    ``entries_list`` with the scope ``report`` finds reports.
    """
    return client.reports.get(
        entry_id,
        rev_id=rev_id,
        include_permissions=include_permissions,
        include_favorite=include_favorite,
    )


@mcp.tool(name="reports_create", annotations={**WRITE, "title": "Create DataLens report"})
def create(
    data: Data,
    meta: Meta,
    annotation: Note = None,
    include_permissions: Annotated[
        bool | None, Field(description="Also say what the caller may do with the new report.")
    ] = None,
    key: Annotated[str | None, Field(description="The report's key, in a folder.")] = None,
    workbook_id: Annotated[
        str | None, Field(description="The workbook to create the report in.")
    ] = None,
    name: Annotated[str | None, Field(description="The report's name.")] = None,
    client: DataLensClient = Depends(datalens_client),
) -> ReportCreated:
    """Create a report in a workbook; the API keeps no ``layout`` of slide elements.

    Measured (2026-10-06): a report made through the API loses the ``layout`` of the
    elements of its slides and part of its ``settings``, so a copy of a report read with
    ``reports_get`` loses where its elements stood. Say so before making one. DataLens
    refuses a report with no slide: ``data.slides`` holds at least one.
    """
    return client.reports.create(
        data=data,
        meta=meta,
        annotation=annotation,
        include_permissions=include_permissions,
        key=key,
        workbook_id=workbook_id,
        name=name,
    )


@mcp.tool(
    name="reports_update", annotations={**WRITE_IDEMPOTENT, "title": "Update DataLens report"}
)
def update(
    entry_id: ReportID,
    data: Data,
    mode: Annotated[
        SaveMode,
        Field(description="`save` keeps the report as a draft; `publish` shows it to all."),
    ],
    meta: Meta,
    rev_id: Annotated[
        str | None, Field(description="The revision of the report the change is made on.")
    ] = None,
    annotation: Note = None,
    client: DataLensClient = Depends(datalens_client),
) -> ReportSaved:
    """Save a report; it LOSES the ``layout`` of its slide elements and some ``settings``.

    Measured (2026-10-06): DataLens drops them on a save through the API, without a word,
    though every value is sent. Ask the person before saving an existing report. Otherwise:
    read it, change ``data``, send it back whole.
    """
    return client.reports.update(
        entry_id, data=data, mode=mode, meta=meta, rev_id=rev_id, annotation=annotation
    )


@mcp.tool(name="reports_delete", annotations={**DESTRUCTIVE, "title": "Delete DataLens report"})
def delete(entry_id: ReportID, client: DataLensClient = Depends(datalens_client)) -> Ack:
    """Delete a report."""
    client.reports.delete(entry_id)
    return Ack.deleted("report", entry_id)
