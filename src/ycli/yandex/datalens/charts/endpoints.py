"""DataLens chart operations, declared once (sans-IO).

Examples:
    >>> data_get("ch1", params=None).body
    {'chartId': 'ch1'}
"""

from collections.abc import Mapping, Sequence

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
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
from ycli.yandex.datalens.schemas.data import GetChartDataArgs
from ycli.yandex.datalens.schemas.editor import (
    CreateEditorChartArgs,
    DeleteEditorChartArgs,
    GetEditorChartArgs,
    UpdateEditorChartArgs,
)
from ycli.yandex.datalens.schemas.ql import (
    CreateQLChartArgs,
    DeleteQLChartArgs,
    GetQLChartArgs,
    UpdateQLChartArgs,
)
from ycli.yandex.datalens.schemas.shared import EntryBranch, EntryUpdateMode
from ycli.yandex.datalens.schemas.wizard import (
    CreateWizardChartV1Args,
    DeleteWizardChartArgs,
    GetWizardChartV1Args,
    UpdateWizardV1Args,
)


def data_get(
    chart_id: str, *, params: Mapping[str, str | Sequence[str]] | None
) -> Endpoint[ChartData]:
    given = (
        None
        if params is None
        else {
            name: value if isinstance(value, str) else list(value) for name, value in params.items()
        }
    )
    body = GetChartDataArgs(chartId=chart_id, params=given)
    return RPC("getChartData", ChartData, json=body, effect=Effect.READ)


def wizard_get(
    chart_id: str,
    *,
    workbook_id: str | None,
    rev_id: str | None,
    include_permissions: bool | None,
    include_links: bool | None,
    include_favorite: bool | None,
    branch: str | None,
) -> Endpoint[WizardChart]:
    body = GetWizardChartV1Args(
        chartId=chart_id,
        workbookId=workbook_id,
        revId=rev_id,
        includePermissions=include_permissions,
        includeLinks=include_links,
        includeFavorite=include_favorite,
        branch=None if branch is None else EntryBranch(branch),
    )
    return RPC("getWizardChart", WizardChart, json=body, effect=Effect.READ)


def wizard_create(
    data: WizardChartData,
    *,
    annotation: EntryAnnotation | None,
    key: str | None,
    workbook_id: str | None,
    name: str | None,
) -> Endpoint[WizardChartCreated]:
    body = CreateWizardChartV1Args(
        data=data, annotation=annotation, key=key, workbookId=workbook_id, name=name
    )
    return RPC("createWizardChart", WizardChartCreated, json=body, effect=Effect.WRITE)


def wizard_update(
    chart_id: str,
    *,
    mode: str,
    data: WizardChartData,
    annotation: EntryAnnotation | None,
    rev_id: str | None,
) -> Endpoint[WizardChartSaved]:
    body = UpdateWizardV1Args(
        chartId=chart_id,
        mode=EntryUpdateMode(mode),
        data=data,
        annotation=annotation,
        revId=rev_id,
    )
    return RPC("updateWizardChart", WizardChartSaved, json=body, effect=Effect.IDEMPOTENT_WRITE)


def wizard_delete(chart_id: str) -> Endpoint[None]:
    # Measured: 200 with `{}`; nothing in it to read.
    body = DeleteWizardChartArgs(chartId=chart_id)
    return RPC("deleteWizardChart", json=body, effect=Effect.DESTRUCTIVE)


def ql_get(
    chart_id: str,
    *,
    workbook_id: str | None,
    rev_id: str | None,
    include_permissions: bool | None,
    include_links: bool | None,
    include_favorite: bool | None,
    branch: str | None,
) -> Endpoint[QLChart]:
    body = GetQLChartArgs(
        chartId=chart_id,
        workbookId=workbook_id,
        revId=rev_id,
        includePermissions=include_permissions,
        includeLinks=include_links,
        includeFavorite=include_favorite,
        branch=None if branch is None else EntryBranch(branch),
    )
    return RPC("getQLChart", QLChart, json=body, effect=Effect.READ)


def ql_create(
    *,
    template: str,
    data: QLChartData,
    annotation: EntryAnnotation | None,
    key: str | None,
    workbook_id: str | None,
    name: str | None,
) -> Endpoint[QLChartCreated]:
    # ``template`` has one value today; it is the caller's to give (#439), so it is validated.
    body = CreateQLChartArgs.model_validate(
        {
            "template": template,
            "data": data,
            "annotation": annotation,
            "key": key,
            "workbookId": workbook_id,
            "name": name,
        }
    )
    return RPC("createQLChart", QLChartCreated, json=body, effect=Effect.WRITE)


def ql_update(
    entry_id: str,
    *,
    template: str,
    mode: str,
    data: QLChartChange,
    annotation: EntryAnnotation | None,
) -> Endpoint[QLChartSaved]:
    body = UpdateQLChartArgs.model_validate(
        {
            "entryId": entry_id,
            "template": template,
            "mode": mode,
            "data": data,
            "annotation": annotation,
        }
    )
    return RPC("updateQLChart", QLChartSaved, json=body, effect=Effect.IDEMPOTENT_WRITE)


def ql_delete(chart_id: str) -> Endpoint[None]:
    body = DeleteQLChartArgs(chartId=chart_id)
    return RPC("deleteQLChart", json=body, effect=Effect.DESTRUCTIVE)


def editor_get(
    chart_id: str,
    *,
    workbook_id: str | None,
    rev_id: str | None,
    include_permissions: bool | None,
    include_links: bool | None,
    include_favorite: bool | None,
    branch: str | None,
) -> Endpoint[EditorChart]:
    body = GetEditorChartArgs(
        chartId=chart_id,
        workbookId=workbook_id,
        revId=rev_id,
        includePermissions=include_permissions,
        includeLinks=include_links,
        includeFavorite=include_favorite,
        branch=None if branch is None else EntryBranch(branch),
    )
    return RPC("getEditorChart", EditorChart, json=body, effect=Effect.READ)


def editor_delete(chart_id: str) -> Endpoint[None]:
    body = DeleteEditorChartArgs(chartId=chart_id)
    return RPC("deleteEditorChart", json=body, effect=Effect.DESTRUCTIVE)


def editor_create(entry: EditorChartCreate) -> Endpoint[EditorChartCreated]:
    body = CreateEditorChartArgs(entry=entry)
    return RPC("createEditorChart", EditorChartCreated, json=body, effect=Effect.WRITE)


def editor_update(entry: EditorChartUpdate, *, mode: str) -> Endpoint[EditorChartSaved]:
    body = UpdateEditorChartArgs(entry=entry, mode=mode)
    return RPC("updateEditorChart", EditorChartSaved, json=body, effect=Effect.IDEMPOTENT_WRITE)
