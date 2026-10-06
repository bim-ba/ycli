"""DataLens report operations, declared once (sans-IO).

Examples:
    >>> delete("r1").body
    {'entryId': 'r1'}
"""

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
from ycli.yandex.datalens.reports.models import (
    EntryAnnotation,
    Report,
    ReportCreated,
    ReportData,
    ReportMeta,
    ReportSaved,
)
from ycli.yandex.datalens.schemas.reports import (
    CreateReportV2Args,
    DeleteReportArgs,
    GetReportV2Args,
    UpdateReportV2Args,
)


def get(
    entry_id: str,
    *,
    rev_id: str | None,
    include_permissions: bool | None,
    include_favorite: bool | None,
) -> Endpoint[Report]:
    body = GetReportV2Args(
        entryId=entry_id,
        revId=rev_id,
        includePermissions=include_permissions,
        includeFavorite=include_favorite,
    )
    return RPC("getReport", Report, json=body, effect=Effect.READ)


def create(
    *,
    data: ReportData,
    meta: ReportMeta | None,
    annotation: EntryAnnotation | None,
    include_permissions: bool | None,
    key: str | None,
    workbook_id: str | None,
    name: str | None,
) -> Endpoint[ReportCreated]:
    body = CreateReportV2Args(
        data=data,
        meta=meta,
        annotation=annotation,
        includePermissions=include_permissions,
        key=key,
        workbookId=workbook_id,
        name=name,
    )
    return RPC("createReport", ReportCreated, json=body, effect=Effect.WRITE)


def update(
    entry_id: str,
    *,
    data: ReportData,
    mode: str,
    meta: ReportMeta | None,
    rev_id: str | None,
    annotation: EntryAnnotation | None,
) -> Endpoint[ReportSaved]:
    body = UpdateReportV2Args(
        entryId=entry_id, data=data, mode=mode, meta=meta, revId=rev_id, annotation=annotation
    )
    return RPC("updateReport", ReportSaved, json=body, effect=Effect.IDEMPOTENT_WRITE)


def delete(entry_id: str) -> Endpoint[None]:
    # The document describes an empty object; as with a chart, nothing in it is read.
    body = DeleteReportArgs(entryId=entry_id)
    return RPC("deleteReport", json=body, effect=Effect.DESTRUCTIVE)
