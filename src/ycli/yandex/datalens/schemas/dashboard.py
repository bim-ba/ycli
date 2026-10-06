# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody

from . import shared
from .shared import EntryLocationIdentifiers


class GetDashboardV2Args(RequestBody):
    dashboard_id: str = Field(..., alias="dashboardId")
    rev_id: str | None = Field(default=None, alias="revId")
    include_permissions: bool | None = Field(default=None, alias="includePermissions")
    include_links: bool | None = Field(default=None, alias="includeLinks")
    include_favorite: bool | None = Field(default=None, alias="includeFavorite")
    branch: shared.EntryBranch | None = None
    workbook_id: str | None = Field(default=None, alias="workbookId")


class DashMetaV2(RootModel[dict[str, Any] | None]):
    root: dict[str, Any] | None


class DeleteDashboardArgs(RequestBody):
    dashboard_id: str = Field(..., alias="dashboardId")
    lock_token: str | None = Field(default=None, alias="lockToken")


class DeleteDashboardResponse(APIModel):
    pass


class DashControlV2Variant1BackgroundSettings(APIModel):
    """Control background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class DashControlV2Variant2BackgroundSettings(APIModel):
    """Control background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class DashControlV2Variant3BackgroundSettings(APIModel):
    """Control background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class DashGroupControlV2BackgroundSettings(APIModel):
    """Control group background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class DashTabItemV2Variant1DataBackgroundSettingsColor(APIModel):
    """Widget background color by theme in hex."""

    light: str | None = Field(default=None, description="Color for the light theme.")
    dark: str | None = Field(default=None, description="Color for the dark theme.")


class DashTabItemV2Variant2DataSizeVariant2(APIModel):
    font_size: int | float | None = Field(
        default=None, alias="fontSize", description="Title font size."
    )
    line_height: int | float | None = Field(
        default=None, alias="lineHeight", description="Title line height."
    )


class DashTabItemV2Variant2DataTextSettingsColor(APIModel):
    """Title text color by theme in hex."""

    light: str | None = Field(default=None, description="Color for the light theme.")
    dark: str | None = Field(default=None, description="Color for the dark theme.")


class DashTabItemV2Variant2DataHint(APIModel):
    """Title hint settings."""

    enabled: bool | None = Field(default=None, description="Whether the title hint is enabled.")
    text: str | None = Field(default=None, description="Title hint text.")


class DashTabItemV2Variant2DataBackgroundSettingsColor(APIModel):
    """Widget background color by theme in hex."""

    light: str | None = Field(default=None, description="Color for the light theme.")
    dark: str | None = Field(default=None, description="Color for the dark theme.")


class DashTabItemV2Variant3DataBackgroundSettingsColor(APIModel):
    """Widget background color by theme in hex."""

    light: str | None = Field(default=None, description="Color for the light theme.")
    dark: str | None = Field(default=None, description="Color for the dark theme.")


class DashTabItemV2Variant3DataTabsItem(APIModel):
    id: str | None = Field(default=None, description="Widget tab identifier.")
    title: str | None = Field(default=None, description="Widget tab title.")
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
    chart_id: str | None = Field(default=None, alias="chartId", description="Chart identifier.")
    is_default: bool | None = Field(
        default=None,
        alias="isDefault",
        description="Whether this is the default widget tab.",
    )
    params: dict[str, shared.DashStringDefaultValueV2] | None = Field(
        default=None, description="Parameters passed to the chart."
    )
    auto_height: bool | None = Field(
        default=None,
        alias="autoHeight",
        description="Whether to adjust the widget height to its content.",
    )
    enable_action_params: bool | None = Field(
        default=None,
        alias="enableActionParams",
        description="Whether chart actions can update parameters.",
    )


class DashTabItemV2Variant4DataBackgroundSettingsColor(APIModel):
    """Widget background color by theme in hex."""

    light: str | None = Field(default=None, description="Color for the light theme.")
    dark: str | None = Field(default=None, description="Color for the dark theme.")


class DashTabItemV2Variant5DataBackgroundSettingsColor(APIModel):
    """Widget background color by theme in hex."""

    light: str | None = Field(default=None, description="Color for the light theme.")
    dark: str | None = Field(default=None, description="Color for the dark theme.")


class DashTabV2Aliases(APIModel):
    """Field aliases used on the tab."""

    default: list[list[str]] | None = Field(
        default=None, description="Groups of field names treated as the same parameter."
    )


class DashTabV2Settings(APIModel):
    """Tab settings."""

    fixed_header_collapsed_default: bool | None = Field(
        default=None,
        alias="fixedHeaderCollapsedDefault",
        description="Whether the fixed header is collapsed by default.",
    )
    is_goldenset: bool | None = Field(
        default=None,
        alias="isGoldenset",
        description="Whether the tab is the reference tab for the AI assistant.",
    )


class DashboardV2Annotation(APIModel):
    """Annotation of the dashboard."""

    description: str | None = Field(default=None, description="Description of the entry.")


class DashboardV2DataSettingsBackgroundSettings(APIModel):
    """Dashboard background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class DashboardV2DataSettingsWidgetsSettingsBackgroundSettings(APIModel):
    """Default widget background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class DashDataV2SettingsBackgroundSettings(APIModel):
    """Dashboard background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class DashDataV2SettingsWidgetsSettingsBackgroundSettings(APIModel):
    """Default widget background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class DashControlV2Variant1(APIModel):
    title: str | None = Field(default=None, description="Control title.")
    impact_type: Literal["allTabs", "currentTab", "selectedTabs", "asGroup"] | str | None = Field(
        default=None,
        alias="impactType",
        description="Determines where the control is displayed: 'allTabs' on all tabs, 'currentTab' on its current tab, 'selectedTabs' on the tabs listed in 'impactTabsIds', and 'asGroup' according to the containing group's settings.",
    )
    impact_tabs_ids: list[str] | None = Field(
        default=None,
        alias="impactTabsIds",
        description="Identifiers of the tabs where the control is displayed when 'impactType' is 'currentTab' or 'selectedTabs'.",
    )
    background_settings: DashControlV2Variant1BackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    border_radius: int | float | None = Field(
        default=None, alias="borderRadius", description="Control border radius."
    )
    auto_height: bool | None = Field(
        default=None,
        alias="autoHeight",
        description="Whether to adjust the control height to its content.",
    )
    source_type: Literal["dataset"] = Field(
        ..., alias="sourceType", description="Dataset control source type."
    )
    source: shared.DashControlSourceDatasetV2Model4 | None = None


class DashControlV2Variant2(APIModel):
    title: str | None = Field(default=None, description="Control title.")
    impact_type: Literal["allTabs", "currentTab", "selectedTabs", "asGroup"] | str | None = Field(
        default=None,
        alias="impactType",
        description="Determines where the control is displayed: 'allTabs' on all tabs, 'currentTab' on its current tab, 'selectedTabs' on the tabs listed in 'impactTabsIds', and 'asGroup' according to the containing group's settings.",
    )
    impact_tabs_ids: list[str] | None = Field(
        default=None,
        alias="impactTabsIds",
        description="Identifiers of the tabs where the control is displayed when 'impactType' is 'currentTab' or 'selectedTabs'.",
    )
    background_settings: DashControlV2Variant2BackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    border_radius: int | float | None = Field(
        default=None, alias="borderRadius", description="Control border radius."
    )
    auto_height: bool | None = Field(
        default=None,
        alias="autoHeight",
        description="Whether to adjust the control height to its content.",
    )
    source_type: Literal["manual"] = Field(
        ..., alias="sourceType", description="Manual control source type."
    )
    source: shared.DashControlSourceManualV2Model4 | None = None


class DashControlV2Variant3(APIModel):
    title: str | None = Field(default=None, description="Control title.")
    impact_type: Literal["allTabs", "currentTab", "selectedTabs", "asGroup"] | str | None = Field(
        default=None,
        alias="impactType",
        description="Determines where the control is displayed: 'allTabs' on all tabs, 'currentTab' on its current tab, 'selectedTabs' on the tabs listed in 'impactTabsIds', and 'asGroup' according to the containing group's settings.",
    )
    impact_tabs_ids: list[str] | None = Field(
        default=None,
        alias="impactTabsIds",
        description="Identifiers of the tabs where the control is displayed when 'impactType' is 'currentTab' or 'selectedTabs'.",
    )
    background_settings: DashControlV2Variant3BackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    border_radius: int | float | None = Field(
        default=None, alias="borderRadius", description="Control border radius."
    )
    auto_height: bool | None = Field(
        default=None,
        alias="autoHeight",
        description="Whether to adjust the control height to its content.",
    )
    source_type: Literal["external"] = Field(
        ..., alias="sourceType", description="External control source type."
    )
    source: shared.DashControlSourceExternalV2 | None = None


class DashGroupControlItemV2Variant1(APIModel):
    title: str | None = Field(default=None, description="Control title.")
    impact_type: Literal["allTabs", "currentTab", "selectedTabs", "asGroup"] | str | None = Field(
        default=None,
        alias="impactType",
        description="Determines where the control is displayed: 'allTabs' on all tabs, 'currentTab' on its current tab, 'selectedTabs' on the tabs listed in 'impactTabsIds', and 'asGroup' according to the containing group's settings.",
    )
    impact_tabs_ids: list[str] | None = Field(
        default=None,
        alias="impactTabsIds",
        description="Identifiers of the tabs where the control is displayed when 'impactType' is 'currentTab' or 'selectedTabs'.",
    )
    id: str | None = Field(default=None, description="Control identifier.")
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
    source: shared.DashControlSourceDatasetV2Model4 | None = None


class DashGroupControlItemV2Variant2(APIModel):
    title: str | None = Field(default=None, description="Control title.")
    impact_type: Literal["allTabs", "currentTab", "selectedTabs", "asGroup"] | str | None = Field(
        default=None,
        alias="impactType",
        description="Determines where the control is displayed: 'allTabs' on all tabs, 'currentTab' on its current tab, 'selectedTabs' on the tabs listed in 'impactTabsIds', and 'asGroup' according to the containing group's settings.",
    )
    impact_tabs_ids: list[str] | None = Field(
        default=None,
        alias="impactTabsIds",
        description="Identifiers of the tabs where the control is displayed when 'impactType' is 'currentTab' or 'selectedTabs'.",
    )
    id: str | None = Field(default=None, description="Control identifier.")
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
    source: shared.DashControlSourceManualV2Model4 | None = None


class DashTabItemV2Variant1DataBackgroundSettings(APIModel):
    """Text item background settings."""

    color: DashTabItemV2Variant1DataBackgroundSettingsColor | None = None


class DashTabItemV2Variant2DataTextSettings(APIModel):
    """Title text settings."""

    color: DashTabItemV2Variant2DataTextSettingsColor | None = None


class DashTabItemV2Variant2DataBackgroundSettings(APIModel):
    """Title background settings."""

    color: DashTabItemV2Variant2DataBackgroundSettingsColor | None = None


class DashTabItemV2Variant3DataBackgroundSettings(APIModel):
    """Widget background settings."""

    color: DashTabItemV2Variant3DataBackgroundSettingsColor | None = None


class DashTabItemV2Variant4DataBackgroundSettings(APIModel):
    """Image background settings."""

    color: DashTabItemV2Variant4DataBackgroundSettingsColor | None = None


class DashTabItemV2Variant5DataBackgroundSettings(APIModel):
    """Neuro widget background settings."""

    color: DashTabItemV2Variant5DataBackgroundSettingsColor | None = None


class DashboardV2DataSettingsWidgetsSettings(APIModel):
    """Default visual settings for dashboard widgets."""

    border_radius: int | float | None = Field(
        default=None, alias="borderRadius", description="Default widget border radius."
    )
    background_settings: DashboardV2DataSettingsWidgetsSettingsBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )


class DashDataV2SettingsWidgetsSettings(APIModel):
    """Default visual settings for dashboard widgets."""

    border_radius: int | float | None = Field(
        default=None, alias="borderRadius", description="Default widget border radius."
    )
    background_settings: DashDataV2SettingsWidgetsSettingsBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )


class DashControlV2(
    RootModel[DashControlV2Variant1 | DashControlV2Variant2 | DashControlV2Variant3]
):
    root: DashControlV2Variant1 | DashControlV2Variant2 | DashControlV2Variant3 = Field(
        ..., description="Control item data."
    )


class DashTabControlItemV2(APIModel):
    id: str | None = Field(default=None, description="Dashboard item identifier.")
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: int | float | None = Field(
        default=None, alias="orderId", description="Current item order."
    )
    default_order_id: int | float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["control"] = Field(..., description="Control item type.")
    data: DashControlV2 | None = None
    defaults: dict[str, shared.DashStringDefaultValueV2] | None = Field(
        default=None,
        description='Selected values keyed by source.datasetFieldId for dataset controls or source.fieldName for manual controls. For a date or date range control with no selected value, keep the field key with an empty string value (e.g. {"fieldId": ""}); do not omit the key or use an empty defaults object. Prefix nonempty values with __<lowercase operation>_ when source.operation is set; leave empty values unprefixed.',
    )


class DashGroupControlItemV2(
    RootModel[DashGroupControlItemV2Variant1 | DashGroupControlItemV2Variant2]
):
    root: DashGroupControlItemV2Variant1 | DashGroupControlItemV2Variant2


class DashGroupControlV2(APIModel):
    """Control group item data."""

    auto_height: bool | None = Field(
        default=None,
        alias="autoHeight",
        description="Whether to adjust the group height to its content.",
    )
    button_apply: bool | None = Field(
        default=None,
        alias="buttonApply",
        description="Whether to show the Apply button.",
    )
    button_reset: bool | None = Field(
        default=None,
        alias="buttonReset",
        description="Whether to show the Reset button.",
    )
    show_group_name: bool | None = Field(
        default=None,
        alias="showGroupName",
        description="Whether to show the control group name.",
    )
    group_name: str | None = Field(
        default=None, alias="groupName", description="Control group name."
    )
    impact_type: Literal["allTabs", "currentTab", "selectedTabs"] | str | None = Field(
        default=None,
        alias="impactType",
        description="Tabs affected by the control group.",
    )
    impact_tabs_ids: list[str] | None = Field(
        default=None,
        alias="impactTabsIds",
        description="Identifiers of tabs affected by the control group.",
    )
    update_controls_on_change: bool | None = Field(
        default=None,
        alias="updateControlsOnChange",
        description="Whether controls update immediately after a value changes.",
    )
    background_settings: DashGroupControlV2BackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    border_radius: int | float | None = Field(
        default=None, alias="borderRadius", description="Control group border radius."
    )
    group: list[DashGroupControlItemV2] | None = Field(
        default=None, description="Controls in the group."
    )


class DashTabGroupControlItemV2(APIModel):
    id: str | None = Field(default=None, description="Dashboard item identifier.")
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: int | float | None = Field(
        default=None, alias="orderId", description="Current item order."
    )
    default_order_id: int | float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["group_control"] = Field(..., description="Control group item type.")
    data: DashGroupControlV2 | None = None


class DashGlobalItemV2(RootModel[DashTabControlItemV2 | DashTabGroupControlItemV2]):
    root: DashTabControlItemV2 | DashTabGroupControlItemV2 = Field(..., discriminator="type")


class DashTabItemV2Variant1Data(APIModel):
    """Text item data."""

    text: str | None = Field(default=None, description="Text item content.")
    auto_height: bool | None = Field(
        default=None,
        alias="autoHeight",
        description="Whether to adjust the item height to its content.",
    )
    background_settings: DashTabItemV2Variant1DataBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    border_radius: int | float | None = Field(
        default=None, alias="borderRadius", description="Text item border radius."
    )


class DashTabItemV2Variant2Data(APIModel):
    """Title item data."""

    text: str | None = Field(default=None, description="Title text.")
    size: (
        Literal["xl", "l", "m", "s", "xs"] | str | DashTabItemV2Variant2DataSizeVariant2 | None
    ) = Field(default=None, description="Title size settings.")
    show_in_toc: bool | None = Field(
        default=None,
        alias="showInTOC",
        description="Whether to show the title in the table of contents.",
    )
    auto_height: bool | None = Field(
        default=None,
        alias="autoHeight",
        description="Whether to adjust the title height to its content.",
    )
    text_settings: DashTabItemV2Variant2DataTextSettings | None = Field(
        default=None, alias="textSettings"
    )
    hint: DashTabItemV2Variant2DataHint | None = None
    background_settings: DashTabItemV2Variant2DataBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    border_radius: int | float | None = Field(
        default=None, alias="borderRadius", description="Title border radius."
    )
    internal_margins_enabled: bool | None = Field(
        default=None,
        alias="internalMarginsEnabled",
        description="Whether the title includes internal margins. This experimental field may change in future API versions.",
    )


class DashTabItemV2Variant3Data(APIModel):
    """Widget item data."""

    hide_title: bool | None = Field(
        default=None, alias="hideTitle", description="Whether to hide the widget title."
    )
    background_settings: DashTabItemV2Variant3DataBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    border_radius: int | float | None = Field(
        default=None, alias="borderRadius", description="Widget border radius."
    )
    tabs: list[DashTabItemV2Variant3DataTabsItem] | None = Field(
        default=None, description="Widget tabs."
    )


class DashTabItemV2Variant4Data(APIModel):
    """Image item data."""

    src: str | None = Field(default=None, description="Image source URL.")
    alt: str | None = Field(default=None, description="Alternative text for the image.")
    preserve_aspect_ratio: bool | None = Field(
        default=None,
        alias="preserveAspectRatio",
        description="Whether to preserve the image aspect ratio.",
    )
    background_settings: DashTabItemV2Variant4DataBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    border_radius: int | float | None = Field(
        default=None, alias="borderRadius", description="Image border radius."
    )


class DashTabItemV2Variant5Data(APIModel):
    """Neuro widget item data."""

    widget_tab_ids: list[str] | None = Field(
        default=None,
        alias="widgetTabIds",
        description="Neuro widget tab identifiers, one per analyzed chart.",
    )
    title: str | None = Field(default=None, description="Neuro widget title.")
    prompt: str | None = Field(default=None, description="Prompt used to generate the widget.")
    hide_title: bool | None = Field(
        default=None,
        alias="hideTitle",
        description="Whether to hide the insight widget title.",
    )
    background_settings: DashTabItemV2Variant5DataBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    border_radius: int | float | None = Field(
        default=None, alias="borderRadius", description="Insight widget border radius."
    )
    hide_actions: bool | None = Field(
        default=None,
        alias="hideActions",
        description="Whether to hide insight widget actions.",
    )


class DashboardV2DataSettings(APIModel):
    """Dashboard settings."""

    autoupdate_interval: int | float | None = Field(
        default=None,
        alias="autoupdateInterval",
        description="Automatic refresh interval in seconds.",
    )
    max_concurrent_requests: int | float | None = Field(
        default=None,
        alias="maxConcurrentRequests",
        description="Maximum number of concurrent requests.",
    )
    load_priority: Literal["charts", "selectors"] | str | None = Field(
        default=None, alias="loadPriority", description="Dashboard loading priority."
    )
    silent_loading: bool | None = Field(
        default=None,
        alias="silentLoading",
        description="Whether to suppress the loading indicator.",
    )
    dependent_selectors: bool | None = Field(
        default=None,
        alias="dependentSelectors",
        description="Whether selectors can depend on each other.",
    )
    global_params: dict[str, str | list[str]] | None = Field(
        default=None,
        alias="globalParams",
        description="Dashboard-wide parameter values.",
    )
    signed_global_params: dict[str, str | list[str]] | None = Field(
        default=None,
        alias="signedGlobalParams",
        description="Signed dashboard-wide parameters for secure use cases.",
    )
    hide_tabs: bool | None = Field(
        default=None, alias="hideTabs", description="Whether to hide the tab bar."
    )
    hide_dash_title: bool | None = Field(
        default=None,
        alias="hideDashTitle",
        description="Whether to hide the dashboard title.",
    )
    expand_toc: bool | None = Field(
        default=None,
        alias="expandTOC",
        description="Whether to expand the table of contents.",
    )
    background_settings: DashboardV2DataSettingsBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    widgets_settings: DashboardV2DataSettingsWidgetsSettings | None = Field(
        default=None, alias="widgetsSettings"
    )
    load_only_visible_charts: bool | None = Field(
        default=None,
        alias="loadOnlyVisibleCharts",
        description="Whether to load only visible charts.",
    )
    margins: list[Any] | None = Field(
        default=None, description="Spacing between dashboard widgets."
    )
    enable_assistant: bool | None = Field(
        default=None,
        alias="enableAssistant",
        description="Whether the Neuroanalyst on a dashboard is enabled.",
    )
    ai_chat_history_enabled: bool | None = Field(
        default=None,
        alias="aiChatHistoryEnabled",
        description="Whether AI chat history is enabled for the dashboard.",
    )


class DashDataV2Settings(APIModel):
    """Dashboard settings."""

    autoupdate_interval: int | float | None = Field(
        default=None,
        alias="autoupdateInterval",
        description="Automatic refresh interval in seconds.",
    )
    max_concurrent_requests: int | float | None = Field(
        default=None,
        alias="maxConcurrentRequests",
        description="Maximum number of concurrent requests.",
    )
    load_priority: Literal["charts", "selectors"] | str | None = Field(
        default=None, alias="loadPriority", description="Dashboard loading priority."
    )
    silent_loading: bool | None = Field(
        default=None,
        alias="silentLoading",
        description="Whether to suppress the loading indicator.",
    )
    dependent_selectors: bool | None = Field(
        default=None,
        alias="dependentSelectors",
        description="Whether selectors can depend on each other.",
    )
    global_params: dict[str, str | list[str]] | None = Field(
        default=None,
        alias="globalParams",
        description="Dashboard-wide parameter values.",
    )
    signed_global_params: dict[str, str | list[str]] | None = Field(
        default=None,
        alias="signedGlobalParams",
        description="Signed dashboard-wide parameters for secure use cases.",
    )
    hide_tabs: bool | None = Field(
        default=None, alias="hideTabs", description="Whether to hide the tab bar."
    )
    hide_dash_title: bool | None = Field(
        default=None,
        alias="hideDashTitle",
        description="Whether to hide the dashboard title.",
    )
    expand_toc: bool | None = Field(
        default=None,
        alias="expandTOC",
        description="Whether to expand the table of contents.",
    )
    background_settings: DashDataV2SettingsBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    widgets_settings: DashDataV2SettingsWidgetsSettings | None = Field(
        default=None, alias="widgetsSettings"
    )
    load_only_visible_charts: bool | None = Field(
        default=None,
        alias="loadOnlyVisibleCharts",
        description="Whether to load only visible charts.",
    )
    margins: list[Any] | None = Field(
        default=None, description="Spacing between dashboard widgets."
    )
    enable_assistant: bool | None = Field(
        default=None,
        alias="enableAssistant",
        description="Whether the Neuroanalyst on a dashboard is enabled.",
    )
    ai_chat_history_enabled: bool | None = Field(
        default=None,
        alias="aiChatHistoryEnabled",
        description="Whether AI chat history is enabled for the dashboard.",
    )


class DashTabItemV2Variant1(APIModel):
    id: str | None = Field(default=None, description="Dashboard item identifier.")
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: int | float | None = Field(
        default=None, alias="orderId", description="Current item order."
    )
    default_order_id: int | float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["text"] = Field(..., description="Text item type.")
    data: DashTabItemV2Variant1Data | None = None


class DashTabItemV2Variant2(APIModel):
    id: str | None = Field(default=None, description="Dashboard item identifier.")
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: int | float | None = Field(
        default=None, alias="orderId", description="Current item order."
    )
    default_order_id: int | float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["title"] = Field(..., description="Title item type.")
    data: DashTabItemV2Variant2Data | None = None


class DashTabItemV2Variant3(APIModel):
    id: str | None = Field(default=None, description="Dashboard item identifier.")
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: int | float | None = Field(
        default=None, alias="orderId", description="Current item order."
    )
    default_order_id: int | float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["widget"] = Field(..., description="Widget item type.")
    data: DashTabItemV2Variant3Data | None = None


class DashTabItemV2Variant4(APIModel):
    id: str | None = Field(default=None, description="Dashboard item identifier.")
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: int | float | None = Field(
        default=None, alias="orderId", description="Current item order."
    )
    default_order_id: int | float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["image"] = Field(..., description="Image item type.")
    data: DashTabItemV2Variant4Data | None = None


class DashTabItemV2Variant5(APIModel):
    id: str | None = Field(default=None, description="Dashboard item identifier.")
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: int | float | None = Field(
        default=None, alias="orderId", description="Current item order."
    )
    default_order_id: int | float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["neuro_widget"] = Field(..., description="Insight widget item type.")
    data: DashTabItemV2Variant5Data | None = None


class DashTabItemV2(
    RootModel[
        DashTabItemV2Variant1
        | DashTabItemV2Variant2
        | DashTabItemV2Variant3
        | DashTabItemV2Variant4
        | DashTabItemV2Variant5
        | DashTabControlItemV2
        | DashTabGroupControlItemV2
    ]
):
    root: (
        DashTabItemV2Variant1
        | DashTabItemV2Variant2
        | DashTabItemV2Variant3
        | DashTabItemV2Variant4
        | DashTabItemV2Variant5
        | DashTabControlItemV2
        | DashTabGroupControlItemV2
    )


class DashTabV2(APIModel):
    id: str | None = Field(default=None, description="Tab identifier.")
    title: str | None = Field(default=None, description="Tab title.")
    hidden: bool | None = Field(default=None, description="Whether the tab is hidden.")
    items: list[DashTabItemV2] | None = Field(
        default=None, description="Items displayed on the tab."
    )
    layout: list[shared.DashLayoutItemV2] | None = Field(
        default=None, description="Item layout on the tab."
    )
    connections: list[shared.DashConnectionV2] | None = Field(
        default=None, description="Connections between tab items."
    )
    aliases: DashTabV2Aliases | None = None
    global_items: list[DashGlobalItemV2] | None = Field(
        default=None,
        alias="globalItems",
        description="Global items visible on the tab.",
    )
    settings: DashTabV2Settings | None = None


class DashDataV2(APIModel):
    counter: int | None = Field(
        default=None, description="Counter used to generate item identifiers."
    )
    salt: str | None = Field(default=None, description="Salt used to generate item identifiers.")
    tabs: list[DashTabV2] | None = Field(default=None, description="Dashboard tabs.")
    settings: DashDataV2Settings | None = None
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


class Entry(EntryLocationIdentifiers):
    data: DashDataV2 | None = None
    meta: DashMetaV2 | None = None
    annotation: shared.EntryAnnotationArg | None = None


class CreateDashboardV2Args(RequestBody):
    entry: Entry


class DashboardV2Data(APIModel):
    """Versioned data of the dashboard."""

    counter: int | None = Field(
        default=None, description="Counter used to generate item identifiers."
    )
    salt: str | None = Field(default=None, description="Salt used to generate item identifiers.")
    tabs: list[DashTabV2] | None = Field(default=None, description="Dashboard tabs.")
    settings: DashboardV2DataSettings | None = None
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


class UpdateDashboardV2ArgsEntry(APIModel):
    entry_id: str | None = Field(default=None, alias="entryId")
    data: DashDataV2 | None = None
    meta: DashMetaV2 | None = None
    rev_id: str | None = Field(default=None, alias="revId")
    annotation: shared.EntryAnnotationArg | None = None


class DashboardV2(APIModel):
    annotation: DashboardV2Annotation | None = None
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Date and time when the dashboard was created.",
    )
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the dashboard.",
    )
    data: DashboardV2Data | None = None
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the dashboard."
    )
    hidden: bool | None = Field(default=None, description="Whether the dashboard is hidden.")
    key: str | None = Field(default=None, description="Key of the dashboard entry.")
    links: dict[str, Any] | None = Field(
        default=None, description="Links associated with the dashboard."
    )
    meta: dict[str, Any] | None = Field(default=None, description="Metadata of the dashboard.")
    public: bool | None = Field(default=None, description="Whether the dashboard is public.")
    published_id: str | None = Field(
        default=None,
        alias="publishedId",
        description="ID of the published dashboard revision.",
    )
    rev_id: str | None = Field(
        default=None, alias="revId", description="ID of the current dashboard revision."
    )
    saved_id: str | None = Field(
        default=None, alias="savedId", description="ID of the saved dashboard revision."
    )
    scope: Literal["dash"] = Field(..., description="Scope of the dashboard entry.")
    tenant_id: str | None = Field(
        default=None,
        alias="tenantId",
        description="ID of the tenant that owns the dashboard.",
    )
    type: Literal[""] = Field(
        ..., description="Type of the dashboard entry. Always an empty string."
    )
    updated_at: str | None = Field(
        default=None,
        alias="updatedAt",
        description="Date and time when the dashboard was last updated.",
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who last updated the dashboard.",
    )
    rev_updated_at: str | None = Field(
        default=None,
        alias="revUpdatedAt",
        description="Date and time when the current revision was last updated.",
    )
    rev_updated_by: str | None = Field(
        default=None,
        alias="revUpdatedBy",
        description="ID of the user who last updated the current revision.",
    )
    version: Literal[2] = Field(..., description="Schema version of the dashboard.")
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook containing the dashboard.",
    )


class GetDashboardV2Result(APIModel):
    entry: DashboardV2 | None = None
    is_favorite: bool | None = Field(default=None, alias="isFavorite")
    permissions: shared.EntryPermissions | None = None


class UpdateDashboardV2Args(RequestBody):
    entry: UpdateDashboardV2ArgsEntry
    mode: shared.EntryUpdateMode
    lock_token: str | None = Field(default=None, alias="lockToken")


class CreateDashboardResponse(APIModel):
    entry: DashboardV2 | None = None


class UpdateDashboardResponse(APIModel):
    entry: DashboardV2 | None = None
