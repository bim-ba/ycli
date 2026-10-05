# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody

from . import shared
from .shared import EntryLocationIdentifiers


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


class DeleteEditorChartResponse(APIModel):
    pass


class EditorTableNodeAnnotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class EditorTableNodeData(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")
    config: str = Field(..., description="Configuration from the Config tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class EditorGravityChartsNodeAnnotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class EditorGravityChartsNodeData(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")
    config: str = Field(..., description="Configuration from the Config tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class EditorMarkdownNodeAnnotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class EditorMarkdownNodeData(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")


class EditorAdvancedChartNodeAnnotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class EditorAdvancedChartNodeData(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")


class EditorSelectorNodeAnnotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class EditorSelectorNodeData(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class GetEditorChartResultPermissions(APIModel):
    """Permissions for the chart."""

    execute: bool = Field(..., description="Indicates if there are permissions to execute.")
    read: bool = Field(..., description="Indicates if there are permissions to read.")
    edit: bool = Field(..., description="Indicates if there are permissions to edit.")
    admin: bool = Field(..., description="Indicates if there are permissions for admin.")


class CreateEditorTableNodeEntryAnnotation(APIModel):
    """Annotation information."""

    description: str = Field(..., description="Description of the entry.")


class CreateEditorTableNodeEntryData(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")
    config: str = Field(..., description="Configuration from the Config tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class CreateEditorGravityChartsNodeEntryAnnotation(APIModel):
    """Annotation information."""

    description: str = Field(..., description="Description of the entry.")


class CreateEditorGravityChartsNodeEntryData(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")
    config: str = Field(..., description="Configuration from the Config tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class CreateEditorMarkdownNodeEntryAnnotation(APIModel):
    """Annotation information."""

    description: str = Field(..., description="Description of the entry.")


class CreateEditorMarkdownNodeEntryData(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")


class CreateEditorAdvancedChartNodeEntryAnnotation(APIModel):
    """Annotation information."""

    description: str = Field(..., description="Description of the entry.")


class CreateEditorAdvancedChartNodeEntryData(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")


class CreateEditorSelectorNodeEntryAnnotation(APIModel):
    """Annotation information."""

    description: str = Field(..., description="Description of the entry.")


class CreateEditorSelectorNodeEntryData(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class UpdateEditorTableNodeEntryAnnotation(APIModel):
    """Annotation information."""

    description: str = Field(..., description="Description of the entry.")


class UpdateEditorTableNodeEntryData(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")
    config: str = Field(..., description="Configuration from the Config tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class UpdateEditorGravityChartsNodeEntryAnnotation(APIModel):
    """Annotation information."""

    description: str = Field(..., description="Description of the entry.")


class UpdateEditorGravityChartsNodeEntryData(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")
    config: str = Field(..., description="Configuration from the Config tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class UpdateEditorMarkdownNodeEntryAnnotation(APIModel):
    """Annotation information."""

    description: str = Field(..., description="Description of the entry.")


class UpdateEditorMarkdownNodeEntryData(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")


class UpdateEditorAdvancedChartNodeEntryAnnotation(APIModel):
    """Annotation information."""

    description: str = Field(..., description="Description of the entry.")


class UpdateEditorAdvancedChartNodeEntryData(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
    prepare: str = Field(..., description="Configuration from the Prepare tab.")


class UpdateEditorSelectorNodeEntryAnnotation(APIModel):
    """Annotation information."""

    description: str = Field(..., description="Description of the entry.")


class UpdateEditorSelectorNodeEntryData(APIModel):
    meta: str = Field(..., description="Configuration from the Meta tab.")
    params: str = Field(..., description="Configuration from the Params tab.")
    sources: str = Field(..., description="Configuration from the Sources tab.")
    controls: str = Field(..., description="Configuration from the Controls tab.")
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
    annotation: EditorTableNodeAnnotation | None = None
    type: Literal["table_node"] = Field(
        ..., description="For Table Editor charts takes value: table_node"
    )
    data: EditorTableNodeData


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
    annotation: EditorGravityChartsNodeAnnotation | None = None
    type: Literal["d3_node"] = Field(..., description="For Gravity UI Charts takes value: d3_node")
    data: EditorGravityChartsNodeData


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
    annotation: EditorMarkdownNodeAnnotation | None = None
    type: Literal["markdown_node"] = Field(
        ..., description="For Markdown Editor charts takes value: markdown_node"
    )
    data: EditorMarkdownNodeData


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
    annotation: EditorAdvancedChartNodeAnnotation | None = None
    type: Literal["advanced-chart_node"] = Field(
        ..., description="For Advanced Editor charts takes value: advanced-chart_node"
    )
    data: EditorAdvancedChartNodeData


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
    annotation: EditorSelectorNodeAnnotation | None = None
    type: Literal["control_node"] = Field(
        ..., description="For Editor JS selectors takes value: control_node"
    )
    data: EditorSelectorNodeData


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
    permissions: GetEditorChartResultPermissions | None = None


class CreateEditorChartResult(APIModel):
    entry: (
        EditorTableNode
        | EditorGravityChartsNode
        | EditorMarkdownNode
        | EditorAdvancedChartNode
        | EditorSelectorNode
    ) = Field(..., discriminator="type")


class CreateEditorTableNodeEntry(APIModel):
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: CreateEditorTableNodeEntryAnnotation | None = None
    type: Literal["table_node"] = Field(
        ..., description="For Table Editor charts takes value: table_node"
    )
    data: CreateEditorTableNodeEntryData


class CreateEditorGravityChartsNodeEntry(APIModel):
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: CreateEditorGravityChartsNodeEntryAnnotation | None = None
    type: Literal["d3_node"] = Field(..., description="For Gravity UI Charts takes value: d3_node")
    data: CreateEditorGravityChartsNodeEntryData


class CreateEditorMarkdownNodeEntry(APIModel):
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: CreateEditorMarkdownNodeEntryAnnotation | None = None
    type: Literal["markdown_node"] = Field(
        ..., description="For Markdown Editor charts takes value: markdown_node"
    )
    data: CreateEditorMarkdownNodeEntryData


class CreateEditorAdvancedChartNodeEntry(APIModel):
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: CreateEditorAdvancedChartNodeEntryAnnotation | None = None
    type: Literal["advanced-chart_node"] = Field(
        ..., description="For Advanced Editor charts takes value: advanced-chart_node"
    )
    data: CreateEditorAdvancedChartNodeEntryData


class CreateEditorSelectorNodeEntry(APIModel):
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: CreateEditorSelectorNodeEntryAnnotation | None = None
    type: Literal["control_node"] = Field(
        ..., description="For Editor JS selectors takes value: control_node"
    )
    data: CreateEditorSelectorNodeEntryData


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


class UpdateEditorTableNodeEntry(APIModel):
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: UpdateEditorTableNodeEntryAnnotation | None = None
    type: Literal["table_node"] = Field(
        ..., description="For Table Editor charts takes value: table_node"
    )
    data: UpdateEditorTableNodeEntryData


class UpdateEditorGravityChartsNodeEntry(APIModel):
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: UpdateEditorGravityChartsNodeEntryAnnotation | None = None
    type: Literal["d3_node"] = Field(..., description="For Gravity UI Charts takes value: d3_node")
    data: UpdateEditorGravityChartsNodeEntryData


class UpdateEditorMarkdownNodeEntry(APIModel):
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: UpdateEditorMarkdownNodeEntryAnnotation | None = None
    type: Literal["markdown_node"] = Field(
        ..., description="For Markdown Editor charts takes value: markdown_node"
    )
    data: UpdateEditorMarkdownNodeEntryData


class UpdateEditorAdvancedChartNodeEntry(APIModel):
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: UpdateEditorAdvancedChartNodeEntryAnnotation | None = None
    type: Literal["advanced-chart_node"] = Field(
        ..., description="For Advanced Editor charts takes value: advanced-chart_node"
    )
    data: UpdateEditorAdvancedChartNodeEntryData


class UpdateEditorSelectorNodeEntry(APIModel):
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: UpdateEditorSelectorNodeEntryAnnotation | None = None
    type: Literal["control_node"] = Field(
        ..., description="For Editor JS selectors takes value: control_node"
    )
    data: UpdateEditorSelectorNodeEntryData


class UpdateEditorChartArgs(RequestBody):
    entry: (
        UpdateEditorTableNodeEntry
        | UpdateEditorGravityChartsNodeEntry
        | UpdateEditorMarkdownNodeEntry
        | UpdateEditorAdvancedChartNodeEntry
        | UpdateEditorSelectorNodeEntry
    ) = Field(..., discriminator="type")
    mode: Literal["save", "publish"] | str = Field(..., description="Editor chart update mode.")
