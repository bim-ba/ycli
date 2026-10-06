# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from typing import Annotated, Any, Literal

from pydantic import Field

from ycli.yandex.models import APIModel, NoDropNull, RequestBody

from . import shared


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
    meta: str | None = Field(default=None, description="Configuration from the Meta tab.")
    params: str | None = Field(default=None, description="Configuration from the Params tab.")
    sources: str | None = Field(default=None, description="Configuration from the Sources tab.")
    controls: str | None = Field(default=None, description="Configuration from the Controls tab.")
    prepare: str | None = Field(default=None, description="Configuration from the Prepare tab.")
    config: str | None = Field(default=None, description="Configuration from the Config tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class EditorGravityChartsNodeAnnotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class EditorGravityChartsNodeData(APIModel):
    meta: str | None = Field(default=None, description="Configuration from the Meta tab.")
    params: str | None = Field(default=None, description="Configuration from the Params tab.")
    sources: str | None = Field(default=None, description="Configuration from the Sources tab.")
    controls: str | None = Field(default=None, description="Configuration from the Controls tab.")
    prepare: str | None = Field(default=None, description="Configuration from the Prepare tab.")
    config: str | None = Field(default=None, description="Configuration from the Config tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class EditorMarkdownNodeAnnotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class EditorMarkdownNodeData(APIModel):
    meta: str | None = Field(default=None, description="Configuration from the Meta tab.")
    params: str | None = Field(default=None, description="Configuration from the Params tab.")
    sources: str | None = Field(default=None, description="Configuration from the Sources tab.")
    controls: str | None = Field(default=None, description="Configuration from the Controls tab.")
    prepare: str | None = Field(default=None, description="Configuration from the Prepare tab.")


class EditorAdvancedChartNodeAnnotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class EditorAdvancedChartNodeData(APIModel):
    meta: str | None = Field(default=None, description="Configuration from the Meta tab.")
    params: str | None = Field(default=None, description="Configuration from the Params tab.")
    sources: str | None = Field(default=None, description="Configuration from the Sources tab.")
    controls: str | None = Field(default=None, description="Configuration from the Controls tab.")
    prepare: str | None = Field(default=None, description="Configuration from the Prepare tab.")


class EditorSelectorNodeAnnotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class EditorSelectorNodeData(APIModel):
    meta: str | None = Field(default=None, description="Configuration from the Meta tab.")
    params: str | None = Field(default=None, description="Configuration from the Params tab.")
    sources: str | None = Field(default=None, description="Configuration from the Sources tab.")
    controls: str | None = Field(default=None, description="Configuration from the Controls tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class GetEditorChartResultPermissions(APIModel):
    """Permissions for the chart."""

    execute: bool | None = Field(
        default=None, description="Indicates if there are permissions to execute."
    )
    read: bool | None = Field(
        default=None, description="Indicates if there are permissions to read."
    )
    edit: bool | None = Field(
        default=None, description="Indicates if there are permissions to edit."
    )
    admin: bool | None = Field(
        default=None, description="Indicates if there are permissions for admin."
    )


class CreateEditorChartArgsEntryVariant1Annotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class CreateEditorChartArgsEntryVariant1Data(APIModel):
    meta: str | None = Field(default=None, description="Configuration from the Meta tab.")
    params: str | None = Field(default=None, description="Configuration from the Params tab.")
    sources: str | None = Field(default=None, description="Configuration from the Sources tab.")
    controls: str | None = Field(default=None, description="Configuration from the Controls tab.")
    prepare: str | None = Field(default=None, description="Configuration from the Prepare tab.")
    config: str | None = Field(default=None, description="Configuration from the Config tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class CreateEditorChartArgsEntryVariant2Annotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class CreateEditorChartArgsEntryVariant2Data(APIModel):
    meta: str | None = Field(default=None, description="Configuration from the Meta tab.")
    params: str | None = Field(default=None, description="Configuration from the Params tab.")
    sources: str | None = Field(default=None, description="Configuration from the Sources tab.")
    controls: str | None = Field(default=None, description="Configuration from the Controls tab.")
    prepare: str | None = Field(default=None, description="Configuration from the Prepare tab.")
    config: str | None = Field(default=None, description="Configuration from the Config tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class CreateEditorChartArgsEntryVariant3Annotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class CreateEditorChartArgsEntryVariant3Data(APIModel):
    meta: str | None = Field(default=None, description="Configuration from the Meta tab.")
    params: str | None = Field(default=None, description="Configuration from the Params tab.")
    sources: str | None = Field(default=None, description="Configuration from the Sources tab.")
    controls: str | None = Field(default=None, description="Configuration from the Controls tab.")
    prepare: str | None = Field(default=None, description="Configuration from the Prepare tab.")


class CreateEditorChartArgsEntryVariant4Annotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class CreateEditorChartArgsEntryVariant4Data(APIModel):
    meta: str | None = Field(default=None, description="Configuration from the Meta tab.")
    params: str | None = Field(default=None, description="Configuration from the Params tab.")
    sources: str | None = Field(default=None, description="Configuration from the Sources tab.")
    controls: str | None = Field(default=None, description="Configuration from the Controls tab.")
    prepare: str | None = Field(default=None, description="Configuration from the Prepare tab.")


class CreateEditorChartArgsEntryVariant5Annotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class CreateEditorChartArgsEntryVariant5Data(APIModel):
    meta: str | None = Field(default=None, description="Configuration from the Meta tab.")
    params: str | None = Field(default=None, description="Configuration from the Params tab.")
    sources: str | None = Field(default=None, description="Configuration from the Sources tab.")
    controls: str | None = Field(default=None, description="Configuration from the Controls tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class UpdateEditorTableNodeEntryAnnotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class UpdateEditorTableNodeEntryData(APIModel):
    meta: str | None = Field(default=None, description="Configuration from the Meta tab.")
    params: str | None = Field(default=None, description="Configuration from the Params tab.")
    sources: str | None = Field(default=None, description="Configuration from the Sources tab.")
    controls: str | None = Field(default=None, description="Configuration from the Controls tab.")
    prepare: str | None = Field(default=None, description="Configuration from the Prepare tab.")
    config: str | None = Field(default=None, description="Configuration from the Config tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class UpdateEditorGravityChartsNodeEntryAnnotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class UpdateEditorGravityChartsNodeEntryData(APIModel):
    meta: str | None = Field(default=None, description="Configuration from the Meta tab.")
    params: str | None = Field(default=None, description="Configuration from the Params tab.")
    sources: str | None = Field(default=None, description="Configuration from the Sources tab.")
    controls: str | None = Field(default=None, description="Configuration from the Controls tab.")
    prepare: str | None = Field(default=None, description="Configuration from the Prepare tab.")
    config: str | None = Field(default=None, description="Configuration from the Config tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class UpdateEditorMarkdownNodeEntryAnnotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class UpdateEditorMarkdownNodeEntryData(APIModel):
    meta: str | None = Field(default=None, description="Configuration from the Meta tab.")
    params: str | None = Field(default=None, description="Configuration from the Params tab.")
    sources: str | None = Field(default=None, description="Configuration from the Sources tab.")
    controls: str | None = Field(default=None, description="Configuration from the Controls tab.")
    prepare: str | None = Field(default=None, description="Configuration from the Prepare tab.")


class UpdateEditorAdvancedChartNodeEntryAnnotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class UpdateEditorAdvancedChartNodeEntryData(APIModel):
    meta: str | None = Field(default=None, description="Configuration from the Meta tab.")
    params: str | None = Field(default=None, description="Configuration from the Params tab.")
    sources: str | None = Field(default=None, description="Configuration from the Sources tab.")
    controls: str | None = Field(default=None, description="Configuration from the Controls tab.")
    prepare: str | None = Field(default=None, description="Configuration from the Prepare tab.")


class UpdateEditorSelectorNodeEntryAnnotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class UpdateEditorSelectorNodeEntryData(APIModel):
    meta: str | None = Field(default=None, description="Configuration from the Meta tab.")
    params: str | None = Field(default=None, description="Configuration from the Params tab.")
    sources: str | None = Field(default=None, description="Configuration from the Sources tab.")
    controls: str | None = Field(default=None, description="Configuration from the Controls tab.")
    activities: str | None = Field(
        default=None, description="Configuration from the Activities tab."
    )


class EditorTableNode(APIModel):
    version: Literal[1] = Field(..., description="Editor version.")
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the entry."
    )
    key: Annotated[str | None, NoDropNull()] = Field(
        default=None, description="Key identifier of the entry."
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    created_by: str | None = Field(
        default=None, alias="createdBy", description="Creator of the entry."
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last update timestamp."
    )
    updated_by: str | None = Field(
        default=None, alias="updatedBy", description="Last updater of the entry."
    )
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    saved_id: str | None = Field(default=None, alias="savedId", description="Saved version ID.")
    published_id: Annotated[str | None, NoDropNull()] = Field(
        default=None, alias="publishedId", description="Published version ID."
    )
    tenant_id: str | None = Field(default=None, alias="tenantId", description="Tenant ID.")
    hidden: bool | None = Field(default=None, description="Indicates if the entry is hidden.")
    public: bool | None = Field(default=None, description="Indicates if the entry is public.")
    workbook_id: Annotated[str | None, NoDropNull()] = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook the Editor chart belongs to.",
    )
    scope: Literal["widget"] = Field(
        ..., description="Type of the entry. For charts takes value: widget"
    )
    meta: Annotated[dict[str, Any] | None, NoDropNull()] = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, Any] | None = Field(default=None, description="Link information.")
    annotation: EditorTableNodeAnnotation | None = None
    type: Literal["table_node"] = Field(
        ..., description="For Table Editor charts takes value: table_node"
    )
    data: EditorTableNodeData | None = None


class EditorGravityChartsNode(APIModel):
    version: Literal[1] = Field(..., description="Editor version.")
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the entry."
    )
    key: Annotated[str | None, NoDropNull()] = Field(
        default=None, description="Key identifier of the entry."
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    created_by: str | None = Field(
        default=None, alias="createdBy", description="Creator of the entry."
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last update timestamp."
    )
    updated_by: str | None = Field(
        default=None, alias="updatedBy", description="Last updater of the entry."
    )
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    saved_id: str | None = Field(default=None, alias="savedId", description="Saved version ID.")
    published_id: Annotated[str | None, NoDropNull()] = Field(
        default=None, alias="publishedId", description="Published version ID."
    )
    tenant_id: str | None = Field(default=None, alias="tenantId", description="Tenant ID.")
    hidden: bool | None = Field(default=None, description="Indicates if the entry is hidden.")
    public: bool | None = Field(default=None, description="Indicates if the entry is public.")
    workbook_id: Annotated[str | None, NoDropNull()] = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook the Editor chart belongs to.",
    )
    scope: Literal["widget"] = Field(
        ..., description="Type of the entry. For charts takes value: widget"
    )
    meta: Annotated[dict[str, Any] | None, NoDropNull()] = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, Any] | None = Field(default=None, description="Link information.")
    annotation: EditorGravityChartsNodeAnnotation | None = None
    type: Literal["d3_node"] = Field(..., description="For Gravity UI Charts takes value: d3_node")
    data: EditorGravityChartsNodeData | None = None


class EditorMarkdownNode(APIModel):
    version: Literal[1] = Field(..., description="Editor version.")
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the entry."
    )
    key: Annotated[str | None, NoDropNull()] = Field(
        default=None, description="Key identifier of the entry."
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    created_by: str | None = Field(
        default=None, alias="createdBy", description="Creator of the entry."
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last update timestamp."
    )
    updated_by: str | None = Field(
        default=None, alias="updatedBy", description="Last updater of the entry."
    )
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    saved_id: str | None = Field(default=None, alias="savedId", description="Saved version ID.")
    published_id: Annotated[str | None, NoDropNull()] = Field(
        default=None, alias="publishedId", description="Published version ID."
    )
    tenant_id: str | None = Field(default=None, alias="tenantId", description="Tenant ID.")
    hidden: bool | None = Field(default=None, description="Indicates if the entry is hidden.")
    public: bool | None = Field(default=None, description="Indicates if the entry is public.")
    workbook_id: Annotated[str | None, NoDropNull()] = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook the Editor chart belongs to.",
    )
    scope: Literal["widget"] = Field(
        ..., description="Type of the entry. For charts takes value: widget"
    )
    meta: Annotated[dict[str, Any] | None, NoDropNull()] = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, Any] | None = Field(default=None, description="Link information.")
    annotation: EditorMarkdownNodeAnnotation | None = None
    type: Literal["markdown_node"] = Field(
        ..., description="For Markdown Editor charts takes value: markdown_node"
    )
    data: EditorMarkdownNodeData | None = None


class EditorAdvancedChartNode(APIModel):
    version: Literal[1] = Field(..., description="Editor version.")
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the entry."
    )
    key: Annotated[str | None, NoDropNull()] = Field(
        default=None, description="Key identifier of the entry."
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    created_by: str | None = Field(
        default=None, alias="createdBy", description="Creator of the entry."
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last update timestamp."
    )
    updated_by: str | None = Field(
        default=None, alias="updatedBy", description="Last updater of the entry."
    )
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    saved_id: str | None = Field(default=None, alias="savedId", description="Saved version ID.")
    published_id: Annotated[str | None, NoDropNull()] = Field(
        default=None, alias="publishedId", description="Published version ID."
    )
    tenant_id: str | None = Field(default=None, alias="tenantId", description="Tenant ID.")
    hidden: bool | None = Field(default=None, description="Indicates if the entry is hidden.")
    public: bool | None = Field(default=None, description="Indicates if the entry is public.")
    workbook_id: Annotated[str | None, NoDropNull()] = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook the Editor chart belongs to.",
    )
    scope: Literal["widget"] = Field(
        ..., description="Type of the entry. For charts takes value: widget"
    )
    meta: Annotated[dict[str, Any] | None, NoDropNull()] = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, Any] | None = Field(default=None, description="Link information.")
    annotation: EditorAdvancedChartNodeAnnotation | None = None
    type: Literal["advanced-chart_node"] = Field(
        ..., description="For Advanced Editor charts takes value: advanced-chart_node"
    )
    data: EditorAdvancedChartNodeData | None = None


class EditorSelectorNode(APIModel):
    version: Literal[1] = Field(..., description="Editor version.")
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the entry."
    )
    key: Annotated[str | None, NoDropNull()] = Field(
        default=None, description="Key identifier of the entry."
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    created_by: str | None = Field(
        default=None, alias="createdBy", description="Creator of the entry."
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last update timestamp."
    )
    updated_by: str | None = Field(
        default=None, alias="updatedBy", description="Last updater of the entry."
    )
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    saved_id: str | None = Field(default=None, alias="savedId", description="Saved version ID.")
    published_id: Annotated[str | None, NoDropNull()] = Field(
        default=None, alias="publishedId", description="Published version ID."
    )
    tenant_id: str | None = Field(default=None, alias="tenantId", description="Tenant ID.")
    hidden: bool | None = Field(default=None, description="Indicates if the entry is hidden.")
    public: bool | None = Field(default=None, description="Indicates if the entry is public.")
    workbook_id: Annotated[str | None, NoDropNull()] = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook the Editor chart belongs to.",
    )
    scope: Literal["widget"] = Field(
        ..., description="Type of the entry. For charts takes value: widget"
    )
    meta: Annotated[dict[str, Any] | None, NoDropNull()] = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, Any] | None = Field(default=None, description="Link information.")
    annotation: EditorSelectorNodeAnnotation | None = None
    type: Literal["control_node"] = Field(
        ..., description="For Editor JS selectors takes value: control_node"
    )
    data: EditorSelectorNodeData | None = None


class GetEditorChartResult(APIModel):
    entry: (
        EditorTableNode
        | EditorGravityChartsNode
        | EditorMarkdownNode
        | EditorAdvancedChartNode
        | EditorSelectorNode
        | shared.OtherKind
        | None
    ) = None
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
        | shared.OtherKind
        | None
    ) = None


class UpdateEditorChartResult(APIModel):
    entry: (
        EditorTableNode
        | EditorGravityChartsNode
        | EditorMarkdownNode
        | EditorAdvancedChartNode
        | EditorSelectorNode
        | shared.OtherKind
        | None
    ) = None


class UpdateEditorTableNodeEntry(APIModel):
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the entry."
    )
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
    data: UpdateEditorTableNodeEntryData | None = None


class UpdateEditorGravityChartsNodeEntry(APIModel):
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the entry."
    )
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Editor chart."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: UpdateEditorGravityChartsNodeEntryAnnotation | None = None
    type: Literal["d3_node"] = Field(..., description="For Gravity UI Charts takes value: d3_node")
    data: UpdateEditorGravityChartsNodeEntryData | None = None


class UpdateEditorMarkdownNodeEntry(APIModel):
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the entry."
    )
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
    data: UpdateEditorMarkdownNodeEntryData | None = None


class UpdateEditorAdvancedChartNodeEntry(APIModel):
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the entry."
    )
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
    data: UpdateEditorAdvancedChartNodeEntryData | None = None


class UpdateEditorSelectorNodeEntry(APIModel):
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the entry."
    )
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
    data: UpdateEditorSelectorNodeEntryData | None = None


class UpdateEditorChartArgs(RequestBody):
    entry: (
        UpdateEditorTableNodeEntry
        | UpdateEditorGravityChartsNodeEntry
        | UpdateEditorMarkdownNodeEntry
        | UpdateEditorAdvancedChartNodeEntry
        | UpdateEditorSelectorNodeEntry
        | shared.OtherKind
    )
    mode: Literal["save", "publish"] | str = Field(..., description="Editor chart update mode.")


class CreateEditorChartArgsEntryVariant1(APIModel):
    key: str | None = Field(
        default=None, description="Entry key when creating the entry in a folder."
    )
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook where the entry should be created.",
    )
    name: str | None = Field(
        default=None, description="Entry name when creating the entry in a workbook."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: CreateEditorChartArgsEntryVariant1Annotation | None = None
    type: Literal["table_node"] = Field(
        ..., description="For Table Editor charts takes value: table_node"
    )
    data: CreateEditorChartArgsEntryVariant1Data | None = None


class CreateEditorChartArgsEntryVariant2(APIModel):
    key: str | None = Field(
        default=None, description="Entry key when creating the entry in a folder."
    )
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook where the entry should be created.",
    )
    name: str | None = Field(
        default=None, description="Entry name when creating the entry in a workbook."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: CreateEditorChartArgsEntryVariant2Annotation | None = None
    type: Literal["d3_node"] = Field(..., description="For Gravity UI Charts takes value: d3_node")
    data: CreateEditorChartArgsEntryVariant2Data | None = None


class CreateEditorChartArgsEntryVariant3(APIModel):
    key: str | None = Field(
        default=None, description="Entry key when creating the entry in a folder."
    )
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook where the entry should be created.",
    )
    name: str | None = Field(
        default=None, description="Entry name when creating the entry in a workbook."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: CreateEditorChartArgsEntryVariant3Annotation | None = None
    type: Literal["markdown_node"] = Field(
        ..., description="For Markdown Editor charts takes value: markdown_node"
    )
    data: CreateEditorChartArgsEntryVariant3Data | None = None


class CreateEditorChartArgsEntryVariant4(APIModel):
    key: str | None = Field(
        default=None, description="Entry key when creating the entry in a folder."
    )
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook where the entry should be created.",
    )
    name: str | None = Field(
        default=None, description="Entry name when creating the entry in a workbook."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: CreateEditorChartArgsEntryVariant4Annotation | None = None
    type: Literal["advanced-chart_node"] = Field(
        ..., description="For Advanced Editor charts takes value: advanced-chart_node"
    )
    data: CreateEditorChartArgsEntryVariant4Data | None = None


class CreateEditorChartArgsEntryVariant5(APIModel):
    key: str | None = Field(
        default=None, description="Entry key when creating the entry in a folder."
    )
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook where the entry should be created.",
    )
    name: str | None = Field(
        default=None, description="Entry name when creating the entry in a workbook."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, str] | None = Field(default=None, description="Link information.")
    annotation: CreateEditorChartArgsEntryVariant5Annotation | None = None
    type: Literal["control_node"] = Field(
        ..., description="For Editor JS selectors takes value: control_node"
    )
    data: CreateEditorChartArgsEntryVariant5Data | None = None


class CreateEditorChartArgs(RequestBody):
    entry: (
        CreateEditorChartArgsEntryVariant1
        | CreateEditorChartArgsEntryVariant2
        | CreateEditorChartArgsEntryVariant3
        | CreateEditorChartArgsEntryVariant4
        | CreateEditorChartArgsEntryVariant5
        | shared.OtherKind
    )
