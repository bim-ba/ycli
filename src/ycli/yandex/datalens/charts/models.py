"""DataLens chart models: the public names of the generated classes this resource uses."""

from typing import Annotated, Any

from pydantic import Field

from ycli.yandex.datalens.schemas.data import GetChartDataResult as ChartData
from ycli.yandex.datalens.schemas.editor import (
    CreateEditorChartArgsEntryVariant1,
    CreateEditorChartArgsEntryVariant2,
    CreateEditorChartArgsEntryVariant3,
    CreateEditorChartArgsEntryVariant4,
    CreateEditorChartArgsEntryVariant5,
    UpdateEditorAdvancedChartNodeEntry,
    UpdateEditorGravityChartsNodeEntry,
    UpdateEditorMarkdownNodeEntry,
    UpdateEditorSelectorNodeEntry,
    UpdateEditorTableNodeEntry,
)
from ycli.yandex.datalens.schemas.editor import CreateEditorChartResult as EditorChartCreated
from ycli.yandex.datalens.schemas.editor import GetEditorChartResult as EditorChart
from ycli.yandex.datalens.schemas.editor import UpdateEditorChartResult as EditorChartSaved
from ycli.yandex.datalens.schemas.ql import CreateQLChartArgsData as QLChartData
from ycli.yandex.datalens.schemas.ql import CreateQLChartResponse as QLChartCreated
from ycli.yandex.datalens.schemas.ql import UpdateQLChartArgsData as QLChartChange
from ycli.yandex.datalens.schemas.ql import UpdateQLChartResponse as QLChartSaved
from ycli.yandex.datalens.schemas.shared import EntryAnnotationArg as EntryAnnotation
from ycli.yandex.datalens.schemas.wizard import CreateWizardChartV1Result as WizardChartCreated
from ycli.yandex.datalens.schemas.wizard import GetWizardChartV1Result as WizardChart
from ycli.yandex.datalens.schemas.wizard import UpdateWizardV1Result as WizardChartSaved
from ycli.yandex.datalens.schemas.wizard import WizardV1ConfigSchema as WizardChartData
from ycli.yandex.models import APIModel

#: An Editor chart to create: `type` says which of the five kinds it is.
EditorChartCreate = Annotated[
    CreateEditorChartArgsEntryVariant1
    | CreateEditorChartArgsEntryVariant2
    | CreateEditorChartArgsEntryVariant3
    | CreateEditorChartArgsEntryVariant4
    | CreateEditorChartArgsEntryVariant5,
    Field(discriminator="type"),
]
#: An Editor chart to save, by its `entryId`: `type` says which kind it is.
EditorChartUpdate = Annotated[
    UpdateEditorTableNodeEntry
    | UpdateEditorGravityChartsNodeEntry
    | UpdateEditorMarkdownNodeEntry
    | UpdateEditorAdvancedChartNodeEntry
    | UpdateEditorSelectorNodeEntry,
    Field(discriminator="type"),
]


class QLChart(APIModel):
    """A QL chart as DataLens answers it.

    The specification describes no reply for a QL chart; these are the keys of a live one
    (2026-10-06). Unlike a chart of the wizard it comes flat, with no ``entry`` around it, and
    what it holds (``data``) is kept as it came.
    """

    entry_id: str | None = Field(default=None, alias="entryId", description="The chart's id.")
    key: str | None = Field(default=None, description="The chart's key: its path and name.")
    scope: str | None = Field(default=None, description="The kind of entry: `widget`.")
    type: str | None = Field(default=None, description="How it is built, e.g. `table_ql_node`.")
    # Both came as ``null`` from the live charts: their type is not known.
    version: int | str | None = Field(
        default=None, description="The version of the entry's format."
    )
    source_version: int | str | None = Field(
        default=None, alias="sourceVersion", description="The version it was saved in."
    )
    workbook_id: str | None = Field(
        default=None, alias="workbookId", description="The workbook it lies in."
    )
    collection_id: str | None = Field(
        default=None, alias="collectionId", description="The collection it lies in."
    )
    tenant_id: str | None = Field(
        default=None, alias="tenantId", description="The DataLens instance it belongs to."
    )
    hidden: bool | None = Field(default=None, description="Whether it is hidden in listings.")
    public: bool | None = Field(default=None, description="Whether it is published to the web.")
    annotation: dict[str, Any] | None = Field(default=None, description="Its description.")
    meta: dict[str, Any] | None = Field(default=None, description="Metadata of the entry.")
    data: dict[str, Any] | None = Field(
        default=None, description="What the chart holds: its query and how it is shown."
    )
    rev_id: str | None = Field(default=None, alias="revId", description="The revision read.")
    saved_id: str | None = Field(default=None, alias="savedId", description="The saved revision.")
    published_id: str | None = Field(
        default=None, alias="publishedId", description="The published revision."
    )
    created_at: str | None = Field(default=None, alias="createdAt", description="When created.")
    created_by: str | None = Field(default=None, alias="createdBy", description="Who created it.")
    updated_at: str | None = Field(default=None, alias="updatedAt", description="When changed.")
    updated_by: str | None = Field(default=None, alias="updatedBy", description="Who changed it.")
    rev_updated_at: str | None = Field(
        default=None, alias="revUpdatedAt", description="When the revision was changed."
    )
    rev_updated_by: str | None = Field(
        default=None, alias="revUpdatedBy", description="Who changed the revision."
    )


__all__ = [
    "ChartData",
    "EditorChart",
    "EditorChartCreate",
    "EditorChartCreated",
    "EditorChartSaved",
    "EditorChartUpdate",
    "EntryAnnotation",
    "QLChart",
    "QLChartChange",
    "QLChartCreated",
    "QLChartData",
    "QLChartSaved",
    "WizardChart",
    "WizardChartCreated",
    "WizardChartData",
    "WizardChartSaved",
]
