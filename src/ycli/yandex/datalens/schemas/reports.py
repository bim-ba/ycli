# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody

from . import shared
from .shared import EntryLocationIdentifiers


class EntryAnnotation(APIModel):
    description: str | None = Field(default=None, description="Description of the entry.")


class ReportMetaV2(RootModel[dict[str, Any] | None]):
    root: dict[str, Any] | None


class GetReportV2Args(RequestBody):
    entry_id: str = Field(..., alias="entryId")
    rev_id: str | None = Field(default=None, alias="revId")
    include_permissions: bool | None = Field(default=None, alias="includePermissions")
    include_favorite: bool | None = Field(default=None, alias="includeFavorite")


class DeleteReportArgs(RequestBody):
    entry_id: str = Field(..., alias="entryId")


class DeleteReportResponse(APIModel):
    pass


class ReportTabItemV2Variant1DataBackgroundSettings(APIModel):
    """Text item background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class ReportTabItemV2Variant2DataSizeVariant2(APIModel):
    font_size: float = Field(..., alias="fontSize", description="Title font size.")
    line_height: float | None = Field(
        default=None, alias="lineHeight", description="Title line height."
    )


class ReportTabItemV2Variant2DataTextSettingsColor(APIModel):
    """Title text color by theme in hex."""

    light: str | None = Field(default=None, description="Color for the light theme.")
    dark: str | None = Field(default=None, description="Color for the dark theme.")


class ReportTabItemV2Variant2DataHint(APIModel):
    """Title hint settings."""

    enabled: bool | None = Field(default=None, description="Whether the title hint is enabled.")
    text: str | None = Field(default=None, description="Title hint text.")


class ReportTabItemV2Variant2DataBackgroundSettings(APIModel):
    """Title item background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class ReportTabItemV2Variant3DataTabsItem(APIModel):
    id: str = Field(..., description="Widget tab identifier.")
    title: str = Field(..., description="Widget tab title.")
    description: str | None = Field(default=None, description="Widget tab description.")
    hint: str | None = Field(default=None, description="Widget tab hint.")
    enable_hint: bool | None = Field(
        default=None,
        alias="enableHint",
        description="Whether the widget tab hint is enabled.",
    )
    enable_description: bool | None = Field(
        default=None,
        alias="enableDescription",
        description="Whether the widget tab description is enabled.",
    )
    chart_id: str = Field(..., alias="chartId", description="Chart identifier.")
    is_default: bool | None = Field(
        default=None,
        alias="isDefault",
        description="Whether this is the default widget tab.",
    )
    params: dict[str, shared.DashStringDefaultValueV2] = Field(
        ..., description="Parameters passed to the chart."
    )
    enable_action_params: bool | None = Field(
        default=None,
        alias="enableActionParams",
        description="Whether chart actions can update parameters.",
    )


class ReportTabItemV2Variant3DataBackgroundSettings(APIModel):
    """Widget background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class ReportTabItemV2Variant4DataBackgroundSettings(APIModel):
    """Image background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class ReportTabItemV2Variant5Data(APIModel):
    """Control item data."""

    title: str = Field(..., description="Control title.")
    source_type: Literal["external"] = Field(
        ..., alias="sourceType", description="External control source type."
    )
    source: shared.DashControlSourceExternalV2


class ReportTabItemV2Variant7DataBackgroundSettings(APIModel):
    """Insight widget background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class ReportDataV2SlidesItem(APIModel):
    id: str = Field(..., description="Slide identifier.")


class ReportDataV2SlideGroupsItemAliases(APIModel):
    """Field aliases used in the slide group."""

    default: list[list[str]] | None = Field(
        default=None, description="Groups of field names treated as the same parameter."
    )


class ReportDataV2VisualSettingsBackgroundSettings(APIModel):
    """Report background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class ReportDataV2VisualSettingsWidgetsSettings(APIModel):
    """Default visual settings for report widgets."""

    border_radius: float | None = Field(
        default=None, alias="borderRadius", description="Default widget border radius."
    )
    internal_margins_enabled: bool | None = Field(
        default=None,
        alias="internalMarginsEnabled",
        description="Whether widgets include internal margins. This experimental field may change in future API versions.",
    )


class ReportDataV2SlideSettingsValueBackgroundSettings(APIModel):
    """Report background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class ReportDataV2SlideSettingsValueWidgetsSettings(APIModel):
    """Default visual settings for report widgets."""

    border_radius: float | None = Field(
        default=None, alias="borderRadius", description="Default widget border radius."
    )
    internal_margins_enabled: bool | None = Field(
        default=None,
        alias="internalMarginsEnabled",
        description="Whether widgets include internal margins. This experimental field may change in future API versions.",
    )


class ReportDataV2Settings(APIModel):
    """Report behavior settings."""

    enable_assistant: bool | None = Field(
        default=None,
        alias="enableAssistant",
        description="Whether the report assistant is enabled.",
    )
    dependent_selectors: bool | None = Field(
        default=None,
        alias="dependentSelectors",
        description="Whether selectors can depend on each other.",
    )
    load_only_visible_charts: bool | None = Field(
        default=None,
        alias="loadOnlyVisibleCharts",
        description="Whether to load only visible charts.",
    )


class ReportTabItemV2Variant1Data(APIModel):
    text: str = Field(..., description="Text item content.")
    auto_height: bool | None = Field(
        default=None,
        alias="autoHeight",
        description="Whether to adjust the item height to its content.",
    )
    background_settings: ReportTabItemV2Variant1DataBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    border_radius: float | None = Field(
        default=None, alias="borderRadius", description="Text item border radius."
    )


class ReportTabItemV2Variant2DataTextSettings(APIModel):
    """Title text settings."""

    color: ReportTabItemV2Variant2DataTextSettingsColor | None = None


class ReportTabItemV2Variant3Data(APIModel):
    """Widget item data."""

    hide_title: bool = Field(
        ..., alias="hideTitle", description="Whether to hide the widget title."
    )
    border_radius: float | None = Field(
        default=None, alias="borderRadius", description="Widget border radius."
    )
    tabs: list[ReportTabItemV2Variant3DataTabsItem] = Field(..., description="Report widget tabs.")
    background_settings: ReportTabItemV2Variant3DataBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )


class ReportTabItemV2Variant4Data(APIModel):
    """Image item data."""

    src: str = Field(..., description="Image source URL.")
    alt: str | None = Field(default=None, description="Alternative text for the image.")
    preserve_aspect_ratio: bool | None = Field(
        default=None,
        alias="preserveAspectRatio",
        description="Whether to preserve the image aspect ratio.",
    )
    background_settings: ReportTabItemV2Variant4DataBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    border_radius: float | None = Field(
        default=None, alias="borderRadius", description="Image border radius."
    )


class ReportTabItemV2Variant5(APIModel):
    id: str = Field(..., description="Dashboard item identifier.")
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: float | None = Field(default=None, alias="orderId", description="Current item order.")
    default_order_id: float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["control"] = Field(..., description="Control item type.")
    data: ReportTabItemV2Variant5Data
    defaults: dict[str, shared.DashStringDefaultValueV2] = Field(
        ..., description="Default control values."
    )


class ReportTabItemV2Variant6DataGroupItemVariant1(APIModel):
    title: str = Field(..., description="Control title.")
    id: str = Field(..., description="Control identifier.")
    namespace: Literal["default"] = Field(..., description="Control namespace.")
    defaults: dict[str, shared.DashStringDefaultValueV2] | None = Field(
        default=None,
        description='Selected values keyed by source.datasetFieldId for dataset controls or source.fieldName for manual controls. For a date or date range control with no selected value, keep the field key with an empty string value (e.g. {"fieldId": ""}); do not omit the key or use an empty defaults object. Prefix nonempty values with __<lowercase operation>_ when source.operation is set; leave empty values unprefixed.',
    )
    placement_mode: Literal["auto", "%", "px"] | str | None = Field(
        default=None, alias="placementMode", description="Control placement mode."
    )
    width: str | None = Field(default=None, description="Control width.")
    source_type: Literal["dataset"] = Field(
        ..., alias="sourceType", description="Dataset control source type."
    )
    source: shared.DashControlSourceDatasetV2Model4


class ReportTabItemV2Variant6DataGroupItemVariant2(APIModel):
    title: str = Field(..., description="Control title.")
    id: str = Field(..., description="Control identifier.")
    namespace: Literal["default"] = Field(..., description="Control namespace.")
    defaults: dict[str, shared.DashStringDefaultValueV2] | None = Field(
        default=None,
        description='Selected values keyed by source.datasetFieldId for dataset controls or source.fieldName for manual controls. For a date or date range control with no selected value, keep the field key with an empty string value (e.g. {"fieldId": ""}); do not omit the key or use an empty defaults object. Prefix nonempty values with __<lowercase operation>_ when source.operation is set; leave empty values unprefixed.',
    )
    placement_mode: Literal["auto", "%", "px"] | str | None = Field(
        default=None, alias="placementMode", description="Control placement mode."
    )
    width: str | None = Field(default=None, description="Control width.")
    source_type: Literal["manual"] = Field(
        ..., alias="sourceType", description="Manual control source type."
    )
    source: shared.DashControlSourceManualV2Model4


class ReportTabItemV2Variant7Data(APIModel):
    """Insight widget item data."""

    title: str | None = Field(default=None, description="Neuro widget title.")
    prompt: str = Field(..., description="Prompt used to generate the widget.")
    hide_title: bool = Field(
        ..., alias="hideTitle", description="Whether to hide the insight widget title."
    )
    background_settings: ReportTabItemV2Variant7DataBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    border_radius: float | None = Field(
        default=None, alias="borderRadius", description="Insight widget border radius."
    )
    hide_actions: bool | None = Field(
        default=None,
        alias="hideActions",
        description="Whether to hide insight widget actions.",
    )
    widget_tab_id: str = Field(..., alias="widgetTabId", description="Neuro widget tab identifier.")


class ReportDataV2VisualSettings(APIModel):
    """Default report visual settings."""

    background_color: str | None = Field(
        default=None,
        alias="backgroundColor",
        description="Legacy report background color.",
    )
    background_settings: ReportDataV2VisualSettingsBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    border_radius: float | None = Field(
        default=None, alias="borderRadius", description="Legacy widget border radius."
    )
    widgets_settings: ReportDataV2VisualSettingsWidgetsSettings | None = Field(
        default=None, alias="widgetsSettings"
    )
    theme: str | None = Field(default=None, description="Report theme.")
    contrast: str | None = Field(default=None, description="Report contrast level.")
    format: str | None = Field(default=None, description="Page format.")
    orientation: str | None = Field(default=None, description="Page orientation.")
    display_visual_grid: str | None = Field(
        default=None,
        alias="displayVisualGrid",
        description="Whether to show the visual grid.",
    )
    display_default_footer: str | None = Field(
        default=None,
        alias="displayDefaultFooter",
        description="Whether to show the default footer.",
    )
    footer_text: str | None = Field(
        default=None, alias="footerText", description="Custom footer text."
    )
    display_link: str | None = Field(
        default=None,
        alias="displayLink",
        description="Whether to show the footer link.",
    )
    footer_link: str | None = Field(
        default=None, alias="footerLink", description="Footer link URL."
    )
    display_on_first_page: str | None = Field(
        default=None,
        alias="displayOnFirstPage",
        description="Whether to show the footer on the first page.",
    )
    display_page_number: str | None = Field(
        default=None,
        alias="displayPageNumber",
        description="Whether to show page numbers.",
    )


class ReportDataV2SlideSettingsValue(APIModel):
    background_color: str | None = Field(
        default=None,
        alias="backgroundColor",
        description="Legacy report background color.",
    )
    background_settings: ReportDataV2SlideSettingsValueBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    border_radius: float | None = Field(
        default=None, alias="borderRadius", description="Legacy widget border radius."
    )
    widgets_settings: ReportDataV2SlideSettingsValueWidgetsSettings | None = Field(
        default=None, alias="widgetsSettings"
    )
    theme: str | None = Field(default=None, description="Report theme.")
    contrast: str | None = Field(default=None, description="Report contrast level.")
    format: str | None = Field(default=None, description="Page format.")
    orientation: str | None = Field(default=None, description="Page orientation.")
    display_visual_grid: str | None = Field(
        default=None,
        alias="displayVisualGrid",
        description="Whether to show the visual grid.",
    )
    display_default_footer: str | None = Field(
        default=None,
        alias="displayDefaultFooter",
        description="Whether to show the default footer.",
    )
    footer_text: str | None = Field(
        default=None, alias="footerText", description="Custom footer text."
    )
    display_link: str | None = Field(
        default=None,
        alias="displayLink",
        description="Whether to show the footer link.",
    )
    footer_link: str | None = Field(
        default=None, alias="footerLink", description="Footer link URL."
    )
    display_on_first_page: str | None = Field(
        default=None,
        alias="displayOnFirstPage",
        description="Whether to show the footer on the first page.",
    )
    display_page_number: str | None = Field(
        default=None,
        alias="displayPageNumber",
        description="Whether to show page numbers.",
    )


class ReportTabItemV2Variant1(APIModel):
    id: str = Field(..., description="Dashboard item identifier.")
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: float | None = Field(default=None, alias="orderId", description="Current item order.")
    default_order_id: float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    data: ReportTabItemV2Variant1Data
    type: Literal["text"] = Field(..., description="Text item type.")


class ReportTabItemV2Variant2Data(APIModel):
    """Title item data."""

    text: str = Field(..., description="Title text.")
    size: Literal["xl", "l", "m", "s", "xs"] | str | ReportTabItemV2Variant2DataSizeVariant2 = (
        Field(..., description="Title size settings.")
    )
    text_settings: ReportTabItemV2Variant2DataTextSettings | None = Field(
        default=None, alias="textSettings"
    )
    hint: ReportTabItemV2Variant2DataHint | None = None
    border_radius: float | None = Field(
        default=None, alias="borderRadius", description="Title border radius."
    )
    internal_margins_enabled: bool | None = Field(
        default=None,
        alias="internalMarginsEnabled",
        description="Whether the title includes internal margins. This experimental field may change in future API versions.",
    )
    background_settings: ReportTabItemV2Variant2DataBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )


class ReportTabItemV2Variant3(APIModel):
    id: str = Field(..., description="Dashboard item identifier.")
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: float | None = Field(default=None, alias="orderId", description="Current item order.")
    default_order_id: float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    data: ReportTabItemV2Variant3Data
    type: Literal["widget"] = Field(..., description="Widget item type.")


class ReportTabItemV2Variant4(APIModel):
    id: str = Field(..., description="Dashboard item identifier.")
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: float | None = Field(default=None, alias="orderId", description="Current item order.")
    default_order_id: float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["image"] = Field(..., description="Image item type.")
    data: ReportTabItemV2Variant4Data


class ReportTabItemV2Variant6Data(APIModel):
    """Control group item data."""

    auto_height: bool = Field(
        ...,
        alias="autoHeight",
        description="Whether to adjust the group height to its content.",
    )
    button_apply: bool = Field(
        ..., alias="buttonApply", description="Whether to show the Apply button."
    )
    button_reset: bool = Field(
        ..., alias="buttonReset", description="Whether to show the Reset button."
    )
    show_group_name: bool = Field(
        ...,
        alias="showGroupName",
        description="Whether to show the control group name.",
    )
    group_name: str | None = Field(
        default=None, alias="groupName", description="Control group name."
    )
    update_controls_on_change: bool | None = Field(
        default=None,
        alias="updateControlsOnChange",
        description="Whether controls update immediately after a value changes.",
    )
    group: list[
        ReportTabItemV2Variant6DataGroupItemVariant1 | ReportTabItemV2Variant6DataGroupItemVariant2
    ] = Field(..., description="Controls in the group.")


class ReportTabItemV2Variant7(APIModel):
    id: str = Field(..., description="Dashboard item identifier.")
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: float | None = Field(default=None, alias="orderId", description="Current item order.")
    default_order_id: float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["neuro_widget"] = Field(..., description="Insight widget item type.")
    data: ReportTabItemV2Variant7Data


class ReportTabItemV2Variant2(APIModel):
    id: str = Field(..., description="Dashboard item identifier.")
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: float | None = Field(default=None, alias="orderId", description="Current item order.")
    default_order_id: float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    data: ReportTabItemV2Variant2Data
    type: Literal["title"] = Field(..., description="Title item type.")


class ReportTabItemV2Variant6(APIModel):
    id: str = Field(..., description="Dashboard item identifier.")
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: float | None = Field(default=None, alias="orderId", description="Current item order.")
    default_order_id: float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["group_control"] = Field(..., description="Control group item type.")
    data: ReportTabItemV2Variant6Data


class ReportTabItemV2(
    RootModel[
        ReportTabItemV2Variant1
        | ReportTabItemV2Variant2
        | ReportTabItemV2Variant3
        | ReportTabItemV2Variant4
        | ReportTabItemV2Variant5
        | ReportTabItemV2Variant6
        | ReportTabItemV2Variant7
    ]
):
    root: (
        ReportTabItemV2Variant1
        | ReportTabItemV2Variant2
        | ReportTabItemV2Variant3
        | ReportTabItemV2Variant4
        | ReportTabItemV2Variant5
        | ReportTabItemV2Variant6
        | ReportTabItemV2Variant7
    )


class ReportDataV2SlideGroupsItem(APIModel):
    id: str = Field(..., description="Slide group identifier.")
    items: list[ReportTabItemV2] = Field(..., description="Items in the slide group.")
    layout: list[shared.DashLayoutItemV2] = Field(
        ..., description="Item layout in the slide group."
    )
    aliases: ReportDataV2SlideGroupsItemAliases
    connections: list[shared.DashConnectionV2] = Field(
        ..., description="Connections between slide group items."
    )


class ReportDataV2(APIModel):
    counter: int = Field(..., description="Counter used to generate item identifiers.")
    salt: str = Field(..., description="Salt used to generate item identifiers.")
    slides: list[ReportDataV2SlidesItem] = Field(..., description="Report slides.")
    slide_groups: list[ReportDataV2SlideGroupsItem] = Field(
        ..., alias="slideGroups", description="Slide groups in the report."
    )
    slides_order: list[str] = Field(
        ..., alias="slidesOrder", description="Slide identifiers in display order."
    )
    visual_settings: ReportDataV2VisualSettings = Field(..., alias="visualSettings")
    slide_settings: dict[str, ReportDataV2SlideSettingsValue] = Field(
        ...,
        alias="slideSettings",
        description="Visual settings keyed by slide identifier.",
    )
    settings: ReportDataV2Settings | None = None
    support_description: str | None = Field(
        default=None,
        alias="supportDescription",
        description="Custom message shown when contacting support.",
    )
    access_description: str | None = Field(
        default=None,
        alias="accessDescription",
        description="Custom message shown when access is denied.",
    )


class ReportV2(APIModel):
    annotation: EntryAnnotation | None = None
    created_by: str | None = Field(default=None, alias="createdBy")
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_by: str | None = Field(default=None, alias="updatedBy")
    updated_at: str | None = Field(default=None, alias="updatedAt")
    rev_updated_by: str | None = Field(default=None, alias="revUpdatedBy")
    rev_updated_at: str | None = Field(default=None, alias="revUpdatedAt")
    data: ReportDataV2 | None = None
    entry_id: str | None = Field(default=None, alias="entryId")
    key: str | None = None
    scope: Literal["report"]
    hidden: bool | None = None
    meta: ReportMetaV2 | None = None
    published_id: str | None = Field(default=None, alias="publishedId")
    saved_id: str | None = Field(default=None, alias="savedId")
    rev_id: str | None = Field(default=None, alias="revId")
    tenant_id: str | None = Field(default=None, alias="tenantId")
    type: Literal[""]
    workbook_id: str | None = Field(default=None, alias="workbookId")
    collection_id: str | None = Field(default=None, alias="collectionId")
    version: Literal[2]
    public: Literal[False]
    links: dict[str, Any] | None = None


class GetReportV2Result(APIModel):
    entry: ReportV2 | None = None
    is_favorite: bool | None = Field(default=None, alias="isFavorite")
    permissions: shared.EntryPermissions | None = None


class CreateReportV2Result(APIModel):
    entry: ReportV2 | None = None
    permissions: shared.EntryPermissions | None = None


class CreateReportV2Args(EntryLocationIdentifiers):
    data: ReportDataV2
    meta: ReportMetaV2 | None
    annotation: shared.EntryAnnotationArg | None = None
    include_permissions: bool | None = Field(default=None, alias="includePermissions")


class UpdateReportV2Result(APIModel):
    entry: ReportV2 | None = None


class UpdateReportV2Args(RequestBody):
    entry_id: str = Field(..., alias="entryId")
    data: ReportDataV2
    mode: Literal["save", "publish"] | str
    rev_id: str | None = Field(default=None, alias="revId")
    meta: ReportMetaV2 | None
    annotation: shared.EntryAnnotationArg | None = None
