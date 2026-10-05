# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody

from . import shared
from .shared import EntryLocationIdentifiers


class Annotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class Data(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")
    config: str = Field(..., description="Configuration from the Config tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class EditorTableNode(APIModel):
    version: Literal[1] = Field(..., description="Editor version.")
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    key: str | None = Field(..., description="Key identifier of the entry.")
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp.")
    created_by: str = Field(..., alias="createdBy", description="Creator of the entry.")
    updated_at: str = Field(..., alias="updatedAt", description="Last update timestamp.")
    updated_by: str = Field(..., alias="updatedBy", description="Last updater of the entry.")
    rev_id: str = Field(..., alias="revId", description="Version ID for the Editor chart.")
    saved_id: str = Field(..., alias="savedId", description="Saved version ID.")
    published_id: str | None = Field(..., alias="publishedId", description="Published version ID.")
    tenant_id: str = Field(..., alias="tenantId", description="Tenant ID.")
    hidden: bool = Field(..., description="Indicates if the entry is hidden.")
    public: bool = Field(..., description="Indicates if the entry is public.")
    workbook_id: str | None = Field(
        ...,
        alias="workbookId",
        description="ID of the workbook the Editor chart belongs to.",
    )
    scope: Literal["widget"] = Field(
        ..., description="Type of the entry. For charts takes value: widget"
    )
    meta: dict[str, Any] | None = Field(..., description="Metadata associated with the entry.")
    links: dict[str, Any] | None = Field(default=None, description="Link information.")
    annotation: Annotation | None = Field(default=None, description="Annotation information.")
    type: Literal["table_node"] = Field(
        ..., description="For Table Editor charts takes value: table_node"
    )
    data: Data


class EditorGravityChartsNode(APIModel):
    version: Literal[1] = Field(..., description="Editor version.")
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    key: str | None = Field(..., description="Key identifier of the entry.")
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp.")
    created_by: str = Field(..., alias="createdBy", description="Creator of the entry.")
    updated_at: str = Field(..., alias="updatedAt", description="Last update timestamp.")
    updated_by: str = Field(..., alias="updatedBy", description="Last updater of the entry.")
    rev_id: str = Field(..., alias="revId", description="Version ID for the Editor chart.")
    saved_id: str = Field(..., alias="savedId", description="Saved version ID.")
    published_id: str | None = Field(..., alias="publishedId", description="Published version ID.")
    tenant_id: str = Field(..., alias="tenantId", description="Tenant ID.")
    hidden: bool = Field(..., description="Indicates if the entry is hidden.")
    public: bool = Field(..., description="Indicates if the entry is public.")
    workbook_id: str | None = Field(
        ...,
        alias="workbookId",
        description="ID of the workbook the Editor chart belongs to.",
    )
    scope: Literal["widget"] = Field(
        ..., description="Type of the entry. For charts takes value: widget"
    )
    meta: dict[str, Any] | None = Field(..., description="Metadata associated with the entry.")
    links: dict[str, Any] | None = Field(default=None, description="Link information.")
    annotation: Annotation | None = Field(default=None, description="Annotation information.")
    type: Literal["d3_node"] = Field(..., description="For Gravity UI Charts takes value: d3_node")
    data: Data


class DataModel(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")


class EditorMarkdownNode(APIModel):
    version: Literal[1] = Field(..., description="Editor version.")
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    key: str | None = Field(..., description="Key identifier of the entry.")
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp.")
    created_by: str = Field(..., alias="createdBy", description="Creator of the entry.")
    updated_at: str = Field(..., alias="updatedAt", description="Last update timestamp.")
    updated_by: str = Field(..., alias="updatedBy", description="Last updater of the entry.")
    rev_id: str = Field(..., alias="revId", description="Version ID for the Editor chart.")
    saved_id: str = Field(..., alias="savedId", description="Saved version ID.")
    published_id: str | None = Field(..., alias="publishedId", description="Published version ID.")
    tenant_id: str = Field(..., alias="tenantId", description="Tenant ID.")
    hidden: bool = Field(..., description="Indicates if the entry is hidden.")
    public: bool = Field(..., description="Indicates if the entry is public.")
    workbook_id: str | None = Field(
        ...,
        alias="workbookId",
        description="ID of the workbook the Editor chart belongs to.",
    )
    scope: Literal["widget"] = Field(
        ..., description="Type of the entry. For charts takes value: widget"
    )
    meta: dict[str, Any] | None = Field(..., description="Metadata associated with the entry.")
    links: dict[str, Any] | None = Field(default=None, description="Link information.")
    annotation: Annotation | None = Field(default=None, description="Annotation information.")
    type: Literal["markdown_node"] = Field(
        ..., description="For Markdown Editor charts takes value: markdown_node"
    )
    data: DataModel


class EditorAdvancedChartNode(APIModel):
    version: Literal[1] = Field(..., description="Editor version.")
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    key: str | None = Field(..., description="Key identifier of the entry.")
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp.")
    created_by: str = Field(..., alias="createdBy", description="Creator of the entry.")
    updated_at: str = Field(..., alias="updatedAt", description="Last update timestamp.")
    updated_by: str = Field(..., alias="updatedBy", description="Last updater of the entry.")
    rev_id: str = Field(..., alias="revId", description="Version ID for the Editor chart.")
    saved_id: str = Field(..., alias="savedId", description="Saved version ID.")
    published_id: str | None = Field(..., alias="publishedId", description="Published version ID.")
    tenant_id: str = Field(..., alias="tenantId", description="Tenant ID.")
    hidden: bool = Field(..., description="Indicates if the entry is hidden.")
    public: bool = Field(..., description="Indicates if the entry is public.")
    workbook_id: str | None = Field(
        ...,
        alias="workbookId",
        description="ID of the workbook the Editor chart belongs to.",
    )
    scope: Literal["widget"] = Field(
        ..., description="Type of the entry. For charts takes value: widget"
    )
    meta: dict[str, Any] | None = Field(..., description="Metadata associated with the entry.")
    links: dict[str, Any] | None = Field(default=None, description="Link information.")
    annotation: Annotation | None = Field(default=None, description="Annotation information.")
    type: Literal["advanced-chart_node"] = Field(
        ..., description="For Advanced Editor charts takes value: advanced-chart_node"
    )
    data: DataModel


class DataModel1(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class EditorSelectorNode(APIModel):
    version: Literal[1] = Field(..., description="Editor version.")
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    key: str | None = Field(..., description="Key identifier of the entry.")
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp.")
    created_by: str = Field(..., alias="createdBy", description="Creator of the entry.")
    updated_at: str = Field(..., alias="updatedAt", description="Last update timestamp.")
    updated_by: str = Field(..., alias="updatedBy", description="Last updater of the entry.")
    rev_id: str = Field(..., alias="revId", description="Version ID for the Editor chart.")
    saved_id: str = Field(..., alias="savedId", description="Saved version ID.")
    published_id: str | None = Field(..., alias="publishedId", description="Published version ID.")
    tenant_id: str = Field(..., alias="tenantId", description="Tenant ID.")
    hidden: bool = Field(..., description="Indicates if the entry is hidden.")
    public: bool = Field(..., description="Indicates if the entry is public.")
    workbook_id: str | None = Field(
        ...,
        alias="workbookId",
        description="ID of the workbook the Editor chart belongs to.",
    )
    scope: Literal["widget"] = Field(
        ..., description="Type of the entry. For charts takes value: widget"
    )
    meta: dict[str, Any] | None = Field(..., description="Metadata associated with the entry.")
    links: dict[str, Any] | None = Field(default=None, description="Link information.")
    annotation: Annotation | None = Field(default=None, description="Annotation information.")
    type: Literal["control_node"] = Field(
        ..., description="For Editor JS selectors takes value: control_node"
    )
    data: DataModel1


class Permissions(APIModel):
    """Permissions for the chart."""

    execute: bool = Field(..., description="Indicates if there are permissions to execute.")
    read: bool = Field(..., description="Indicates if there are permissions to read.")
    edit: bool = Field(..., description="Indicates if there are permissions to edit.")
    admin: bool = Field(..., description="Indicates if there are permissions for admin.")


class GetEditorChartResult(APIModel):
    entry: (
        EditorTableNode
        | EditorGravityChartsNode
        | EditorMarkdownNode
        | EditorAdvancedChartNode
        | EditorSelectorNode
    ) = Field(..., discriminator="type")
    is_favorite: bool | None = Field(
        default=None,
        alias="isFavorite",
        description="Indicates if the chart is marked as favorite.",
    )
    permissions: Permissions | None = Field(default=None, description="Permissions for the chart.")


class GetEditorChartArgs(RequestBody):
    chart_id: str = Field(
        ...,
        alias="chartId",
        description="ID of the Editor chart. You can find it in the chart settings in DataLens interface.",
    )
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook the Editor chart belongs to. If navigation across folders is enabled and the Editor chart belongs to a folder, the value must be null.",
    )
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    include_permissions: bool | None = Field(
        default=None,
        alias="includePermissions",
        description="Include information on configured permissions in the response.",
    )
    include_links: bool | None = Field(
        default=None,
        alias="includeLinks",
        description="Include information on configured links in the response.",
    )
    include_favorite: bool | None = Field(
        default=None,
        alias="includeFavorite",
        description="Include favorite status in the response.",
    )
    branch: shared.EntryBranch | None = None


class DeleteEditorChartArgs(RequestBody):
    chart_id: str = Field(..., alias="chartId", description="ID of the Editor chart to delete.")


class CreateEditorChartResult(APIModel):
    entry: (
        EditorTableNode
        | EditorGravityChartsNode
        | EditorMarkdownNode
        | EditorAdvancedChartNode
        | EditorSelectorNode
    ) = Field(..., discriminator="type")


class AnnotationModel(APIModel):
    """Annotation information."""

    description: str = Field(..., description="Description of the entry.")


class DataModel2(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")
    config: str = Field(..., description="Configuration from the Config tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class CreateEditorTableNodeEntry(APIModel):
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: AnnotationModel | None = Field(default=None, description="Annotation information.")
    type: Literal["table_node"] = Field(
        ..., description="For Table Editor charts takes value: table_node"
    )
    data: DataModel2


class CreateEditorGravityChartsNodeEntry(APIModel):
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: AnnotationModel | None = Field(default=None, description="Annotation information.")
    type: Literal["d3_node"] = Field(..., description="For Gravity UI Charts takes value: d3_node")
    data: DataModel2


class DataModel3(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")


class CreateEditorMarkdownNodeEntry(APIModel):
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: AnnotationModel | None = Field(default=None, description="Annotation information.")
    type: Literal["markdown_node"] = Field(
        ..., description="For Markdown Editor charts takes value: markdown_node"
    )
    data: DataModel3


class CreateEditorAdvancedChartNodeEntry(APIModel):
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: AnnotationModel | None = Field(default=None, description="Annotation information.")
    type: Literal["advanced-chart_node"] = Field(
        ..., description="For Advanced Editor charts takes value: advanced-chart_node"
    )
    data: DataModel3


class DataModel4(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class CreateEditorSelectorNodeEntry(APIModel):
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: AnnotationModel | None = Field(default=None, description="Annotation information.")
    type: Literal["control_node"] = Field(
        ..., description="For Editor JS selectors takes value: control_node"
    )
    data: DataModel4


class Entry(CreateEditorTableNodeEntry, EntryLocationIdentifiers):
    pass


class EntryModel(CreateEditorGravityChartsNodeEntry, EntryLocationIdentifiers):
    pass


class EntryModel1(CreateEditorMarkdownNodeEntry, EntryLocationIdentifiers):
    pass


class EntryModel2(CreateEditorAdvancedChartNodeEntry, EntryLocationIdentifiers):
    pass


class EntryModel3(CreateEditorSelectorNodeEntry, EntryLocationIdentifiers):
    pass


class EntryModel4(RootModel[Entry | EntryModel | EntryModel1 | EntryModel2 | EntryModel3]):
    root: Entry | EntryModel | EntryModel1 | EntryModel2 | EntryModel3


class CreateEditorChartArgs(RequestBody):
    entry: EntryModel4


class UpdateEditorChartResult(APIModel):
    entry: (
        EditorTableNode
        | EditorGravityChartsNode
        | EditorMarkdownNode
        | EditorAdvancedChartNode
        | EditorSelectorNode
    ) = Field(..., discriminator="type")


class DataModel5(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")
    config: str = Field(..., description="Configuration from the Config tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class UpdateEditorTableNodeEntry(APIModel):
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: AnnotationModel | None = Field(default=None, description="Annotation information.")
    type: Literal["table_node"] = Field(
        ..., description="For Table Editor charts takes value: table_node"
    )
    data: DataModel5


class UpdateEditorGravityChartsNodeEntry(APIModel):
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: AnnotationModel | None = Field(default=None, description="Annotation information.")
    type: Literal["d3_node"] = Field(..., description="For Gravity UI Charts takes value: d3_node")
    data: DataModel5


class DataModel6(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")


class UpdateEditorMarkdownNodeEntry(APIModel):
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: AnnotationModel | None = Field(default=None, description="Annotation information.")
    type: Literal["markdown_node"] = Field(
        ..., description="For Markdown Editor charts takes value: markdown_node"
    )
    data: DataModel6


class UpdateEditorAdvancedChartNodeEntry(APIModel):
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: AnnotationModel | None = Field(default=None, description="Annotation information.")
    type: Literal["advanced-chart_node"] = Field(
        ..., description="For Advanced Editor charts takes value: advanced-chart_node"
    )
    data: DataModel6


class DataModel7(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class UpdateEditorSelectorNodeEntry(APIModel):
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: AnnotationModel | None = Field(default=None, description="Annotation information.")
    type: Literal["control_node"] = Field(
        ..., description="For Editor JS selectors takes value: control_node"
    )
    data: DataModel7


class UpdateEditorChartArgs(RequestBody):
    entry: (
        UpdateEditorTableNodeEntry
        | UpdateEditorGravityChartsNodeEntry
        | UpdateEditorMarkdownNodeEntry
        | UpdateEditorAdvancedChartNodeEntry
        | UpdateEditorSelectorNodeEntry
    ) = Field(..., discriminator="type")
    mode: Literal["save", "publish"] | str = Field(..., description="Editor chart update mode.")


class DeleteEditorChartResponse(APIModel):
    pass
