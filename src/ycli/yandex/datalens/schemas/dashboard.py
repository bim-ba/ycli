# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody

from . import shared
from .shared import EntryLocationIdentifiers


class BackgroundSettings(APIModel):
    """Control background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class DashControlV2(APIModel):
    """Control item data."""

    title: str = Field(..., description="Control title.", min_length=1)
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
    background_settings: BackgroundSettings | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Control background settings.",
    )
    border_radius: float | None = Field(
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
    source: shared.DashControlSourceDatasetV2Model8


class DashControlV2Model(APIModel):
    """Control item data."""

    title: str = Field(..., description="Control title.", min_length=1)
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
    background_settings: BackgroundSettings | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Control background settings.",
    )
    border_radius: float | None = Field(
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
    source: shared.DashControlSourceManualV2Model8


class DashControlV2Model1(APIModel):
    """Control item data."""

    title: str = Field(..., description="Control title.", min_length=1)
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
    background_settings: BackgroundSettings | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Control background settings.",
    )
    border_radius: float | None = Field(
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
    source: shared.DashControlSourceExternalV2


class DashControlV2Model2(RootModel[DashControlV2 | DashControlV2Model | DashControlV2Model1]):
    root: DashControlV2 | DashControlV2Model | DashControlV2Model1 = Field(
        ..., description="Control item data."
    )


class DashTabControlItemV2(APIModel):
    id: str = Field(..., description="Dashboard item identifier.", min_length=1)
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: float | None = Field(default=None, alias="orderId", description="Current item order.")
    default_order_id: float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["control"] = Field(..., description="Control item type.")
    data: DashControlV2Model2
    defaults: dict[str, shared.DashStringDefaultValueV2] = Field(
        ...,
        description='Selected values keyed by source.datasetFieldId for dataset controls or source.fieldName for manual controls. For a date or date range control with no selected value, keep the field key with an empty string value (e.g. {"fieldId": ""}); do not omit the key or use an empty defaults object. Prefix nonempty values with __<lowercase operation>_ when source.operation is set; leave empty values unprefixed.',
    )


class DashGroupControlItemV2(APIModel):
    title: str = Field(..., description="Control title.", min_length=1)
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
    id: str = Field(..., description="Control identifier.", min_length=1)
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
    source: shared.DashControlSourceDatasetV2Model8


class DashGroupControlItemV2Model(APIModel):
    title: str = Field(..., description="Control title.", min_length=1)
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
    id: str = Field(..., description="Control identifier.", min_length=1)
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
    source: shared.DashControlSourceManualV2Model8


class DashGroupControlItemV2Model1(RootModel[DashGroupControlItemV2 | DashGroupControlItemV2Model]):
    root: DashGroupControlItemV2 | DashGroupControlItemV2Model


class BackgroundSettingsModel(APIModel):
    """Control group background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class DashGroupControlV2(APIModel):
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
    background_settings: BackgroundSettingsModel | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Control group background settings.",
    )
    border_radius: float | None = Field(
        default=None, alias="borderRadius", description="Control group border radius."
    )
    group: list[DashGroupControlItemV2Model1] = Field(..., description="Controls in the group.")


class DashTabGroupControlItemV2(APIModel):
    id: str = Field(..., description="Dashboard item identifier.", min_length=1)
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: float | None = Field(default=None, alias="orderId", description="Current item order.")
    default_order_id: float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["group_control"] = Field(..., description="Control group item type.")
    data: DashGroupControlV2


class Color(APIModel):
    """Widget background color by theme in hex."""

    light: str | None = Field(default=None, description="Color for the light theme.")
    dark: str | None = Field(default=None, description="Color for the dark theme.")


class BackgroundSettingsModel1(APIModel):
    """Text item background settings."""

    color: Color | None = Field(
        default=None, description="Widget background color by theme in hex."
    )


class Data(APIModel):
    """Text item data."""

    text: str = Field(..., description="Text item content.")
    auto_height: bool | None = Field(
        default=None,
        alias="autoHeight",
        description="Whether to adjust the item height to its content.",
    )
    background_settings: BackgroundSettingsModel1 | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Text item background settings.",
    )
    border_radius: float | None = Field(
        default=None, alias="borderRadius", description="Text item border radius."
    )


class DashTabItemV2(APIModel):
    id: str = Field(..., description="Dashboard item identifier.", min_length=1)
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: float | None = Field(default=None, alias="orderId", description="Current item order.")
    default_order_id: float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["text"] = Field(..., description="Text item type.")
    data: Data = Field(..., description="Text item data.")


class Size(APIModel):
    """Title size settings."""

    font_size: float = Field(..., alias="fontSize", description="Title font size.")
    line_height: float | None = Field(
        default=None, alias="lineHeight", description="Title line height."
    )


class ColorModel(APIModel):
    """Title text color by theme in hex."""

    light: str | None = Field(default=None, description="Color for the light theme.")
    dark: str | None = Field(default=None, description="Color for the dark theme.")


class TextSettings(APIModel):
    """Title text settings."""

    color: ColorModel | None = Field(default=None, description="Title text color by theme in hex.")


class Hint(APIModel):
    """Title hint settings."""

    enabled: bool | None = Field(default=None, description="Whether the title hint is enabled.")
    text: str | None = Field(default=None, description="Title hint text.")


class ColorModel1(APIModel):
    """Widget background color by theme in hex."""

    light: str | None = Field(default=None, description="Color for the light theme.")
    dark: str | None = Field(default=None, description="Color for the dark theme.")


class BackgroundSettingsModel2(APIModel):
    """Title background settings."""

    color: ColorModel1 | None = Field(
        default=None, description="Widget background color by theme in hex."
    )


class DataModel(APIModel):
    """Title item data."""

    text: str = Field(..., description="Title text.")
    size: Literal["xl", "l", "m", "s", "xs"] | str | Size = Field(
        ..., description="Title size settings."
    )
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
    text_settings: TextSettings | None = Field(
        default=None, alias="textSettings", description="Title text settings."
    )
    hint: Hint | None = Field(default=None, description="Title hint settings.")
    background_settings: BackgroundSettingsModel2 | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Title background settings.",
    )
    border_radius: float | None = Field(
        default=None, alias="borderRadius", description="Title border radius."
    )
    internal_margins_enabled: bool | None = Field(
        default=None,
        alias="internalMarginsEnabled",
        description="Whether the title includes internal margins. This experimental field may change in future API versions.",
    )


class DashTabItemV2Model(APIModel):
    id: str = Field(..., description="Dashboard item identifier.", min_length=1)
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: float | None = Field(default=None, alias="orderId", description="Current item order.")
    default_order_id: float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["title"] = Field(..., description="Title item type.")
    data: DataModel = Field(..., description="Title item data.")


class BackgroundSettingsModel3(APIModel):
    """Widget background settings."""

    color: ColorModel1 | None = Field(
        default=None, description="Widget background color by theme in hex."
    )


class Tab(APIModel):
    id: str = Field(..., description="Widget tab identifier.", min_length=1)
    title: str = Field(..., description="Widget tab title.", min_length=1)
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
    chart_id: str = Field(..., alias="chartId", description="Chart identifier.", min_length=1)
    is_default: bool | None = Field(
        default=None,
        alias="isDefault",
        description="Whether this is the default widget tab.",
    )
    params: dict[str, shared.DashStringDefaultValueV2] = Field(
        ..., description="Parameters passed to the chart."
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


class DataModel1(APIModel):
    """Widget item data."""

    hide_title: bool = Field(
        ..., alias="hideTitle", description="Whether to hide the widget title."
    )
    background_settings: BackgroundSettingsModel3 | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Widget background settings.",
    )
    border_radius: float | None = Field(
        default=None, alias="borderRadius", description="Widget border radius."
    )
    tabs: list[Tab] = Field(..., description="Widget tabs.")


class DashTabItemV2Model1(APIModel):
    id: str = Field(..., description="Dashboard item identifier.", min_length=1)
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: float | None = Field(default=None, alias="orderId", description="Current item order.")
    default_order_id: float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["widget"] = Field(..., description="Widget item type.")
    data: DataModel1 = Field(..., description="Widget item data.")


class BackgroundSettingsModel4(APIModel):
    """Image background settings."""

    color: ColorModel1 | None = Field(
        default=None, description="Widget background color by theme in hex."
    )


class DataModel2(APIModel):
    """Image item data."""

    src: str = Field(..., description="Image source URL.")
    alt: str | None = Field(default=None, description="Alternative text for the image.")
    preserve_aspect_ratio: bool | None = Field(
        default=None,
        alias="preserveAspectRatio",
        description="Whether to preserve the image aspect ratio.",
    )
    background_settings: BackgroundSettingsModel4 | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Image background settings.",
    )
    border_radius: float | None = Field(
        default=None, alias="borderRadius", description="Image border radius."
    )


class DashTabItemV2Model2(APIModel):
    id: str = Field(..., description="Dashboard item identifier.", min_length=1)
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: float | None = Field(default=None, alias="orderId", description="Current item order.")
    default_order_id: float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["image"] = Field(..., description="Image item type.")
    data: DataModel2 = Field(..., description="Image item data.")


class WidgetTabId(RootModel[str]):
    root: str = Field(..., min_length=1)


class BackgroundSettingsModel5(APIModel):
    """Neuro widget background settings."""

    color: ColorModel1 | None = Field(
        default=None, description="Widget background color by theme in hex."
    )


class DataModel3(APIModel):
    """Neuro widget item data."""

    widget_tab_ids: list[WidgetTabId] = Field(
        ...,
        alias="widgetTabIds",
        description="Neuro widget tab identifiers, one per analyzed chart.",
        max_length=5,
        min_length=1,
    )
    title: str | None = Field(default=None, description="Neuro widget title.")
    prompt: str = Field(..., description="Prompt used to generate the widget.", min_length=1)
    hide_title: bool = Field(
        ..., alias="hideTitle", description="Whether to hide the insight widget title."
    )
    background_settings: BackgroundSettingsModel5 | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Neuro widget background settings.",
    )
    border_radius: float | None = Field(
        default=None, alias="borderRadius", description="Insight widget border radius."
    )
    hide_actions: bool | None = Field(
        default=None,
        alias="hideActions",
        description="Whether to hide insight widget actions.",
    )


class DashTabItemV2Model3(APIModel):
    id: str = Field(..., description="Dashboard item identifier.", min_length=1)
    namespace: Literal["default"] = Field(..., description="Item namespace.")
    order_id: float | None = Field(default=None, alias="orderId", description="Current item order.")
    default_order_id: float | None = Field(
        default=None, alias="defaultOrderId", description="Default item order."
    )
    type: Literal["neuro_widget"] = Field(..., description="Insight widget item type.")
    data: DataModel3 = Field(..., description="Neuro widget item data.")


class DashTabItemV2Model4(
    RootModel[
        DashTabItemV2
        | DashTabItemV2Model
        | DashTabItemV2Model1
        | DashTabItemV2Model2
        | DashTabItemV2Model3
        | DashTabControlItemV2
        | DashTabGroupControlItemV2
    ]
):
    root: (
        DashTabItemV2
        | DashTabItemV2Model
        | DashTabItemV2Model1
        | DashTabItemV2Model2
        | DashTabItemV2Model3
        | DashTabControlItemV2
        | DashTabGroupControlItemV2
    )


class DashGlobalItemV2(RootModel[DashTabControlItemV2 | DashTabGroupControlItemV2]):
    root: DashTabControlItemV2 | DashTabGroupControlItemV2 = Field(..., discriminator="type")


class DefaultItemItem(RootModel[str]):
    root: str = Field(..., min_length=1)


class DefaultItem(RootModel[list[DefaultItemItem]]):
    root: list[DefaultItemItem] = Field(..., min_length=2)


class Aliases(APIModel):
    """Field aliases used on the tab."""

    default: list[DefaultItem] | None = Field(
        default=None, description="Groups of field names treated as the same parameter."
    )


class Settings(APIModel):
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


class DashTabV2(APIModel):
    id: str = Field(..., description="Tab identifier.", min_length=1)
    title: str = Field(..., description="Tab title.", min_length=1)
    hidden: bool | None = Field(default=None, description="Whether the tab is hidden.")
    items: list[DashTabItemV2Model4] = Field(..., description="Items displayed on the tab.")
    layout: list[shared.DashLayoutItemV2] = Field(..., description="Item layout on the tab.")
    connections: list[shared.DashConnectionV2] = Field(
        ..., description="Connections between tab items."
    )
    aliases: Aliases = Field(..., description="Field aliases used on the tab.")
    global_items: list[DashGlobalItemV2] | None = Field(
        default=None,
        alias="globalItems",
        description="Global items visible on the tab.",
    )
    settings: Settings | None = Field(default=None, description="Tab settings.")


class Annotation(APIModel):
    """Annotation of the dashboard."""

    description: str | None = Field(default=None, description="Description of the entry.")


class AutoupdateInterval(RootModel[float]):
    root: float = Field(..., description="Automatic refresh interval in seconds.", ge=30.0)


class MaxConcurrentRequests(RootModel[float]):
    root: float = Field(..., description="Maximum number of concurrent requests.", ge=1.0)


class BackgroundSettingsModel6(APIModel):
    """Dashboard background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class BackgroundSettingsModel7(APIModel):
    """Default widget background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class WidgetsSettings(APIModel):
    """Default visual settings for dashboard widgets."""

    border_radius: float | None = Field(
        default=None, alias="borderRadius", description="Default widget border radius."
    )
    background_settings: BackgroundSettingsModel7 | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Default widget background settings.",
    )


class SettingsModel(APIModel):
    """Dashboard settings."""

    autoupdate_interval: AutoupdateInterval | None = Field(
        ...,
        alias="autoupdateInterval",
        description="Automatic refresh interval in seconds.",
    )
    max_concurrent_requests: MaxConcurrentRequests | None = Field(
        ...,
        alias="maxConcurrentRequests",
        description="Maximum number of concurrent requests.",
    )
    load_priority: Literal["charts", "selectors"] | str | None = Field(
        default=None, alias="loadPriority", description="Dashboard loading priority."
    )
    silent_loading: bool = Field(
        ...,
        alias="silentLoading",
        description="Whether to suppress the loading indicator.",
    )
    dependent_selectors: bool = Field(
        ...,
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
    expand_toc: bool = Field(
        ..., alias="expandTOC", description="Whether to expand the table of contents."
    )
    background_settings: BackgroundSettingsModel6 | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Dashboard background settings.",
    )
    widgets_settings: WidgetsSettings | None = Field(
        default=None,
        alias="widgetsSettings",
        description="Default visual settings for dashboard widgets.",
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


class DataModel4(APIModel):
    """Versioned data of the dashboard."""

    counter: int = Field(..., description="Counter used to generate item identifiers.", ge=1)
    salt: str = Field(..., description="Salt used to generate item identifiers.", min_length=1)
    tabs: list[DashTabV2] = Field(..., description="Dashboard tabs.", min_length=1)
    settings: SettingsModel = Field(..., description="Dashboard settings.")
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


class DashboardV2(APIModel):
    annotation: Annotation | None = Field(default=None, description="Annotation of the dashboard.")
    created_at: str = Field(
        ...,
        alias="createdAt",
        description="Date and time when the dashboard was created.",
    )
    created_by: str = Field(
        ..., alias="createdBy", description="ID of the user who created the dashboard."
    )
    data: DataModel4 = Field(..., description="Versioned data of the dashboard.")
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the dashboard.")
    hidden: bool = Field(..., description="Whether the dashboard is hidden.")
    key: str | None = Field(..., description="Key of the dashboard entry.")
    links: dict[str, Any] | None = Field(
        default=None, description="Links associated with the dashboard."
    )
    meta: dict[str, Any] | None = Field(..., description="Metadata of the dashboard.")
    public: bool = Field(..., description="Whether the dashboard is public.")
    published_id: str | None = Field(
        ..., alias="publishedId", description="ID of the published dashboard revision."
    )
    rev_id: str = Field(..., alias="revId", description="ID of the current dashboard revision.")
    saved_id: str = Field(..., alias="savedId", description="ID of the saved dashboard revision.")
    scope: Literal["dash"] = Field(..., description="Scope of the dashboard entry.")
    tenant_id: str = Field(
        ..., alias="tenantId", description="ID of the tenant that owns the dashboard."
    )
    type: Literal[""] = Field(
        ..., description="Type of the dashboard entry. Always an empty string."
    )
    updated_at: str = Field(
        ...,
        alias="updatedAt",
        description="Date and time when the dashboard was last updated.",
    )
    updated_by: str = Field(
        ...,
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
        ...,
        alias="workbookId",
        description="ID of the workbook containing the dashboard.",
    )


class GetDashboardV2Result(APIModel):
    entry: DashboardV2
    is_favorite: bool | None = Field(default=None, alias="isFavorite")
    permissions: shared.EntryPermissions | None = None


class GetDashboardV2Args(RequestBody):
    dashboard_id: str = Field(..., alias="dashboardId")
    rev_id: str | None = Field(default=None, alias="revId")
    include_permissions: bool | None = Field(default=None, alias="includePermissions")
    include_links: bool | None = Field(default=None, alias="includeLinks")
    include_favorite: bool | None = Field(default=None, alias="includeFavorite")
    branch: shared.EntryBranch | None = None
    workbook_id: str | None = Field(default=None, alias="workbookId")


class BackgroundSettingsModel8(APIModel):
    """Dashboard background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class BackgroundSettingsModel9(APIModel):
    """Default widget background settings."""

    color: shared.DashColorByThemeV2 | str | None = Field(
        default=None, description="Widget background color in hex."
    )


class DashDataV2(APIModel):
    counter: int = Field(..., description="Counter used to generate item identifiers.", ge=1)
    salt: str = Field(..., description="Salt used to generate item identifiers.", min_length=1)
    tabs: list[DashTabV2] = Field(..., description="Dashboard tabs.", min_length=1)
    settings: SettingsModel = Field(..., description="Dashboard settings.")
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


class DashMetaV2(RootModel[dict[str, Any] | None]):
    root: dict[str, Any] | None


class Entry(EntryLocationIdentifiers):
    data: DashDataV2
    meta: DashMetaV2 | None
    annotation: shared.EntryAnnotationArg | None = None


class CreateDashboardV2Args(RequestBody):
    entry: Entry


class EntryModel(APIModel):
    entry_id: str = Field(..., alias="entryId")
    data: DashDataV2
    meta: DashMetaV2 | None
    rev_id: str | None = Field(default=None, alias="revId")
    annotation: shared.EntryAnnotationArg | None = None


class UpdateDashboardV2Args(RequestBody):
    entry: EntryModel
    mode: shared.EntryUpdateMode
    lock_token: str | None = Field(default=None, alias="lockToken")


class DeleteDashboardArgs(RequestBody):
    dashboard_id: str = Field(..., alias="dashboardId")
    lock_token: str | None = Field(default=None, alias="lockToken")


class CreateDashboardResponse(APIModel):
    entry: DashboardV2


class UpdateDashboardResponse(APIModel):
    entry: DashboardV2


class DeleteDashboardResponse(APIModel):
    pass
