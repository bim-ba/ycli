# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody

from . import shared
from .shared import EntryLocationIdentifiers


class Operation(APIModel):
    """Operation used to compare field values."""

    code: str = Field(..., description="Filter operation code.")


class Filter(APIModel):
    """Filter applied to the field."""

    operation: Operation = Field(..., description="Operation used to compare field values.")
    value: str | list[str] | None = Field(
        default=None, description="Value or values used by the filter operation."
    )


class WizardV1FiltersItemSchema(APIModel):
    guid: str = Field(..., description="Identifier of the field used for filtering.")
    dataset_id: str = Field(
        ...,
        alias="datasetId",
        description="Identifier of the dataset containing the field.",
    )
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    filter: Filter = Field(..., description="Filter applied to the field.")


class Formatting(APIModel):
    """Numeric formatting settings for the field."""

    format: Literal["number", "percent"] | str | None = Field(
        default=None, description="Number formatting mode."
    )
    show_rank_delimiter: bool | None = Field(
        default=None,
        alias="showRankDelimiter",
        description="Whether to separate digit groups in numbers.",
    )
    prefix: str | None = Field(
        default=None, description="Text displayed before the formatted value."
    )
    postfix: str | None = Field(
        default=None, description="Text displayed after the formatted value."
    )
    unit: Literal["auto", "k", "m", "b", "t"] | str | None = Field(
        default=None, description="Unit used to scale the numeric value."
    )
    precision: float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class Thresholds(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class ThresholdsModel(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str = Field(..., description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str = Field(..., description="Upper gradient threshold.")


class Settings(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str = Field(
        ..., alias="gradientType", description="Gradient type."
    )
    thresholds: Thresholds | ThresholdsModel = Field(
        ..., description="Thresholds that define the gradient color scale."
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class ColorSettings(APIModel):
    """Bar color settings."""

    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: Settings = Field(..., description="Gradient bar color settings.")


class SettingsModel(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class ColorSettingsModel(APIModel):
    """Bar color settings."""

    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: SettingsModel = Field(..., description="Single-color bar settings.")


class SettingsModel1(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class ColorSettingsModel1(APIModel):
    """Bar color settings."""

    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: SettingsModel1 = Field(..., description="Two-color bar settings.")


class Scale(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class SettingsModel2(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class ScaleModel(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: SettingsModel2 = Field(..., description="Manual bar scale boundaries.")


class BarsSettings(APIModel):
    """In-cell bar settings."""

    enabled: bool = Field(..., description="Whether to display bars in table cells.")
    color_settings: ColorSettings | ColorSettingsModel | ColorSettingsModel1 = Field(
        ..., alias="colorSettings", description="Bar color settings."
    )
    show_labels: bool = Field(
        ..., alias="showLabels", description="Whether to display values over bars."
    )
    align: Literal["left", "right", "default"] | str = Field(
        ..., description="Bar alignment within table cells."
    )
    scale: Scale | ScaleModel = Field(..., description="Scale used to calculate bar lengths.")
    show_bars_in_totals: bool = Field(
        ...,
        alias="showBarsInTotals",
        description="Whether to display bars in total rows.",
    )


class SubTotalsSettings(APIModel):
    """Subtotal settings."""

    enabled: bool = Field(..., description="Whether to display subtotals for the field.")


class PaletteState(APIModel):
    """Discrete palette settings."""

    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")


class GradientState(APIModel):
    """Continuous gradient settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    reversed: bool | None = Field(
        default=None, description="Whether to reverse the gradient palette."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class SettingsModel3(APIModel):
    """Background color configuration."""

    palette_state: PaletteState = Field(
        ..., alias="paletteState", description="Discrete palette settings."
    )
    gradient_state: GradientState = Field(
        ..., alias="gradientState", description="Continuous gradient settings."
    )
    is_continuous: bool = Field(
        ...,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class BackgroundSettings(APIModel):
    """Conditional background settings."""

    enabled: bool = Field(..., description="Whether conditional background coloring is enabled.")
    color_field_guid: str = Field(
        ...,
        alias="colorFieldGuid",
        description="Identifier of the field used to color the background.",
    )
    settings_id: str = Field(
        ...,
        alias="settingsId",
        description="Identifier of the background color settings.",
    )
    settings: SettingsModel3 = Field(..., description="Background color configuration.")


class Width(APIModel):
    """Table column width settings."""

    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WidthModel(APIModel):
    """Table column width settings."""

    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str = Field(..., description="Column width percentage.")


class WidthModel1(APIModel):
    """Table column width settings."""

    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str = Field(..., description="Column width in pixels.")


class ColumnSettings(APIModel):
    """Table column settings."""

    width: Width | WidthModel | WidthModel1 = Field(..., description="Table column width settings.")
    horizontal_alignment: Literal["auto", "start", "center", "end"] | str | None = Field(
        default=None,
        alias="horizontalAlignment",
        description="Horizontal alignment of values in the column.",
    )


class HintSettings(APIModel):
    """Field hint settings."""

    enabled: bool | None = Field(default=None, description="Whether the field hint is enabled.")
    text: str | None = Field(default=None, description="Hint text displayed for the field.")


class ThresholdsModel1(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class ThresholdsModel2(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str = Field(..., description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str = Field(..., description="Upper gradient threshold.")


class SettingsModel4(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str = Field(
        ..., alias="gradientType", description="Gradient type."
    )
    thresholds: ThresholdsModel1 | ThresholdsModel2 = Field(
        ..., description="Thresholds that define the gradient color scale."
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class ColorSettingsModel2(APIModel):
    """Bar color settings."""

    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: SettingsModel4 = Field(..., description="Gradient bar color settings.")


class SettingsModel5(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class ColorSettingsModel3(APIModel):
    """Bar color settings."""

    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: SettingsModel5 = Field(..., description="Single-color bar settings.")


class SettingsModel6(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class ColorSettingsModel4(APIModel):
    """Bar color settings."""

    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: SettingsModel6 = Field(..., description="Two-color bar settings.")


class ScaleModel1(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class SettingsModel7(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class ScaleModel2(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: SettingsModel7 = Field(..., description="Manual bar scale boundaries.")


class SettingsModel8(APIModel):
    """Background color configuration."""

    palette_state: PaletteState = Field(
        ..., alias="paletteState", description="Discrete palette settings."
    )
    gradient_state: GradientState = Field(
        ..., alias="gradientState", description="Continuous gradient settings."
    )
    is_continuous: bool = Field(
        ...,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WidthModel2(APIModel):
    """Table column width settings."""

    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WidthModel3(APIModel):
    """Table column width settings."""

    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str = Field(..., description="Column width percentage.")


class WidthModel4(APIModel):
    """Table column width settings."""

    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str = Field(..., description="Column width in pixels.")


class FieldModel(APIModel):
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    markup_type: Literal["none", "md", "html"] | str | None = Field(
        default=None,
        alias="markupType",
        description="Markup type used to render field values.",
    )
    formatting: Formatting | None = Field(
        default=None, description="Numeric formatting settings for the field."
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: BarsSettings | None = Field(
        default=None, alias="barsSettings", description="In-cell bar settings."
    )
    sub_totals_settings: SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings", description="Subtotal settings."
    )
    background_settings: BackgroundSettings | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Conditional background settings.",
    )
    column_settings: ColumnSettings | None = Field(
        default=None, alias="columnSettings", description="Table column settings."
    )
    hint_settings: HintSettings | None = Field(
        default=None, alias="hintSettings", description="Field hint settings."
    )
    guid: str = Field(..., description="Field identifier.")
    dataset_id: str = Field(
        ...,
        alias="datasetId",
        description="Identifier of the dataset containing the field.",
    )


class WizardFieldSchema(APIModel):
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    markup_type: Literal["none", "md", "html"] | str | None = Field(
        default=None,
        alias="markupType",
        description="Markup type used to render field values.",
    )
    formatting: Formatting | None = Field(
        default=None, description="Numeric formatting settings for the field."
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: BarsSettings | None = Field(
        default=None, alias="barsSettings", description="In-cell bar settings."
    )
    sub_totals_settings: SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings", description="Subtotal settings."
    )
    background_settings: BackgroundSettings | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Conditional background settings.",
    )
    column_settings: ColumnSettings | None = Field(
        default=None, alias="columnSettings", description="Table column settings."
    )
    hint_settings: HintSettings | None = Field(
        default=None, alias="hintSettings", description="Field hint settings."
    )
    guid: str = Field(..., description="Hierarchy identifier.")
    title: str = Field(..., description="Hierarchy display title.")
    data_type: Literal["hierarchy"] = Field(
        ..., description="Data type identifying this field as a hierarchy."
    )
    fields: list[FieldModel] = Field(..., description="Fields included in the hierarchy.")


class ThresholdsModel3(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class ThresholdsModel4(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str = Field(..., description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str = Field(..., description="Upper gradient threshold.")


class SettingsModel9(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str = Field(
        ..., alias="gradientType", description="Gradient type."
    )
    thresholds: ThresholdsModel3 | ThresholdsModel4 = Field(
        ..., description="Thresholds that define the gradient color scale."
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class ColorSettingsModel5(APIModel):
    """Bar color settings."""

    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: SettingsModel9 = Field(..., description="Gradient bar color settings.")


class SettingsModel10(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class ColorSettingsModel6(APIModel):
    """Bar color settings."""

    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: SettingsModel10 = Field(..., description="Single-color bar settings.")


class SettingsModel11(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class ColorSettingsModel7(APIModel):
    """Bar color settings."""

    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: SettingsModel11 = Field(..., description="Two-color bar settings.")


class ScaleModel3(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class SettingsModel12(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class ScaleModel4(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: SettingsModel12 = Field(..., description="Manual bar scale boundaries.")


class SettingsModel13(APIModel):
    """Background color configuration."""

    palette_state: PaletteState = Field(
        ..., alias="paletteState", description="Discrete palette settings."
    )
    gradient_state: GradientState = Field(
        ..., alias="gradientState", description="Continuous gradient settings."
    )
    is_continuous: bool = Field(
        ...,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WidthModel5(APIModel):
    """Table column width settings."""

    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WidthModel6(APIModel):
    """Table column width settings."""

    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str = Field(..., description="Column width percentage.")


class WidthModel7(APIModel):
    """Table column width settings."""

    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str = Field(..., description="Column width in pixels.")


class WizardFieldSchemaModel(APIModel):
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    markup_type: Literal["none", "md", "html"] | str | None = Field(
        default=None,
        alias="markupType",
        description="Markup type used to render field values.",
    )
    formatting: Formatting | None = Field(
        default=None, description="Numeric formatting settings for the field."
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: BarsSettings | None = Field(
        default=None, alias="barsSettings", description="In-cell bar settings."
    )
    sub_totals_settings: SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings", description="Subtotal settings."
    )
    background_settings: BackgroundSettings | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Conditional background settings.",
    )
    column_settings: ColumnSettings | None = Field(
        default=None, alias="columnSettings", description="Table column settings."
    )
    hint_settings: HintSettings | None = Field(
        default=None, alias="hintSettings", description="Field hint settings."
    )
    guid: str = Field(..., description="Field identifier.")
    dataset_id: str = Field(
        ...,
        alias="datasetId",
        description="Identifier of the dataset containing the field.",
    )


class ThresholdsModel5(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class ThresholdsModel6(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str = Field(..., description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str = Field(..., description="Upper gradient threshold.")


class SettingsModel14(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str = Field(
        ..., alias="gradientType", description="Gradient type."
    )
    thresholds: ThresholdsModel5 | ThresholdsModel6 = Field(
        ..., description="Thresholds that define the gradient color scale."
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class ColorSettingsModel8(APIModel):
    """Bar color settings."""

    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: SettingsModel14 = Field(..., description="Gradient bar color settings.")


class SettingsModel15(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class ColorSettingsModel9(APIModel):
    """Bar color settings."""

    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: SettingsModel15 = Field(..., description="Single-color bar settings.")


class SettingsModel16(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class ColorSettingsModel10(APIModel):
    """Bar color settings."""

    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: SettingsModel16 = Field(..., description="Two-color bar settings.")


class ScaleModel5(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class SettingsModel17(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class ScaleModel6(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: SettingsModel17 = Field(..., description="Manual bar scale boundaries.")


class SettingsModel18(APIModel):
    """Background color configuration."""

    palette_state: PaletteState = Field(
        ..., alias="paletteState", description="Discrete palette settings."
    )
    gradient_state: GradientState = Field(
        ..., alias="gradientState", description="Continuous gradient settings."
    )
    is_continuous: bool = Field(
        ...,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WidthModel8(APIModel):
    """Table column width settings."""

    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WidthModel9(APIModel):
    """Table column width settings."""

    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str = Field(..., description="Column width percentage.")


class WidthModel10(APIModel):
    """Table column width settings."""

    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str = Field(..., description="Column width in pixels.")


class WizardFieldSchemaModel1(APIModel):
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    markup_type: Literal["none", "md", "html"] | str | None = Field(
        default=None,
        alias="markupType",
        description="Markup type used to render field values.",
    )
    formatting: Formatting | None = Field(
        default=None, description="Numeric formatting settings for the field."
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: BarsSettings | None = Field(
        default=None, alias="barsSettings", description="In-cell bar settings."
    )
    sub_totals_settings: SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings", description="Subtotal settings."
    )
    background_settings: BackgroundSettings | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Conditional background settings.",
    )
    column_settings: ColumnSettings | None = Field(
        default=None, alias="columnSettings", description="Table column settings."
    )
    hint_settings: HintSettings | None = Field(
        default=None, alias="hintSettings", description="Field hint settings."
    )
    title: Literal["Measure Names"] = Field(
        ..., description="Title identifying the Measure Names pseudo-field."
    )
    type: Literal["PSEUDO"] = Field(..., description="Field type identifying a pseudo-field.")
    data_type: Literal["string"] = Field(
        ..., description="String data type of the Measure Names pseudo-field."
    )


class ThresholdsModel7(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class ThresholdsModel8(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str = Field(..., description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str = Field(..., description="Upper gradient threshold.")


class SettingsModel19(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str = Field(
        ..., alias="gradientType", description="Gradient type."
    )
    thresholds: ThresholdsModel7 | ThresholdsModel8 = Field(
        ..., description="Thresholds that define the gradient color scale."
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class ColorSettingsModel11(APIModel):
    """Bar color settings."""

    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: SettingsModel19 = Field(..., description="Gradient bar color settings.")


class SettingsModel20(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class ColorSettingsModel12(APIModel):
    """Bar color settings."""

    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: SettingsModel20 = Field(..., description="Single-color bar settings.")


class SettingsModel21(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class ColorSettingsModel13(APIModel):
    """Bar color settings."""

    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: SettingsModel21 = Field(..., description="Two-color bar settings.")


class ScaleModel7(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class SettingsModel22(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class ScaleModel8(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: SettingsModel22 = Field(..., description="Manual bar scale boundaries.")


class SettingsModel23(APIModel):
    """Background color configuration."""

    palette_state: PaletteState = Field(
        ..., alias="paletteState", description="Discrete palette settings."
    )
    gradient_state: GradientState = Field(
        ..., alias="gradientState", description="Continuous gradient settings."
    )
    is_continuous: bool = Field(
        ...,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WidthModel11(APIModel):
    """Table column width settings."""

    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WidthModel12(APIModel):
    """Table column width settings."""

    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str = Field(..., description="Column width percentage.")


class WidthModel13(APIModel):
    """Table column width settings."""

    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str = Field(..., description="Column width in pixels.")


class WizardFieldSchemaModel2(APIModel):
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    markup_type: Literal["none", "md", "html"] | str | None = Field(
        default=None,
        alias="markupType",
        description="Markup type used to render field values.",
    )
    formatting: Formatting | None = Field(
        default=None, description="Numeric formatting settings for the field."
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: BarsSettings | None = Field(
        default=None, alias="barsSettings", description="In-cell bar settings."
    )
    sub_totals_settings: SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings", description="Subtotal settings."
    )
    background_settings: BackgroundSettings | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Conditional background settings.",
    )
    column_settings: ColumnSettings | None = Field(
        default=None, alias="columnSettings", description="Table column settings."
    )
    hint_settings: HintSettings | None = Field(
        default=None, alias="hintSettings", description="Field hint settings."
    )
    title: Literal["Measure Values"] = Field(
        ..., description="Title identifying the Measure Values pseudo-field."
    )
    type: Literal["PSEUDO"] = Field(..., description="Field type identifying a pseudo-field.")
    data_type: Literal["float"] = Field(
        ..., description="Numeric data type of the Measure Values pseudo-field."
    )


class WizardFieldSchemaModel3(
    RootModel[
        WizardFieldSchema
        | WizardFieldSchemaModel
        | WizardFieldSchemaModel1
        | WizardFieldSchemaModel2
    ]
):
    root: (
        WizardFieldSchema
        | WizardFieldSchemaModel
        | WizardFieldSchemaModel1
        | WizardFieldSchemaModel2
    )


class WizardV1LineShapeSettingsSchema(APIModel):
    line_width: float | Literal["auto"] | None = Field(
        default=None,
        alias="lineWidth",
        description="Line width in pixels or automatic width.",
    )
    linecap: Literal["butt", "round", "square", "none"] | str | None = Field(
        default=None, description="Shape used at line endpoints."
    )
    linejoin: Literal["bevel", "round", "miter", "unset"] | str | None = Field(
        default=None, description="Shape used at line segment joins."
    )


class ThresholdsModel9(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class ThresholdsModel10(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str = Field(..., description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str = Field(..., description="Upper gradient threshold.")


class SettingsModel24(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str = Field(
        ..., alias="gradientType", description="Gradient type."
    )
    thresholds: ThresholdsModel9 | ThresholdsModel10 = Field(
        ..., description="Thresholds that define the gradient color scale."
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class ColorSettingsModel14(APIModel):
    """Bar color settings."""

    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: SettingsModel24 = Field(..., description="Gradient bar color settings.")


class SettingsModel25(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class ColorSettingsModel15(APIModel):
    """Bar color settings."""

    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: SettingsModel25 = Field(..., description="Single-color bar settings.")


class SettingsModel26(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class ColorSettingsModel16(APIModel):
    """Bar color settings."""

    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: SettingsModel26 = Field(..., description="Two-color bar settings.")


class ScaleModel9(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class SettingsModel27(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class ScaleModel10(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: SettingsModel27 = Field(..., description="Manual bar scale boundaries.")


class SettingsModel28(APIModel):
    """Background color configuration."""

    palette_state: PaletteState = Field(
        ..., alias="paletteState", description="Discrete palette settings."
    )
    gradient_state: GradientState = Field(
        ..., alias="gradientState", description="Continuous gradient settings."
    )
    is_continuous: bool = Field(
        ...,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WidthModel14(APIModel):
    """Table column width settings."""

    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WidthModel15(APIModel):
    """Table column width settings."""

    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str = Field(..., description="Column width percentage.")


class WidthModel16(APIModel):
    """Table column width settings."""

    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str = Field(..., description="Column width in pixels.")


class ThresholdsModel11(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class ThresholdsModel12(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str = Field(..., description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str = Field(..., description="Upper gradient threshold.")


class SettingsModel29(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str = Field(
        ..., alias="gradientType", description="Gradient type."
    )
    thresholds: ThresholdsModel11 | ThresholdsModel12 = Field(
        ..., description="Thresholds that define the gradient color scale."
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class ColorSettingsModel17(APIModel):
    """Bar color settings."""

    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: SettingsModel29 = Field(..., description="Gradient bar color settings.")


class SettingsModel30(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class ColorSettingsModel18(APIModel):
    """Bar color settings."""

    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: SettingsModel30 = Field(..., description="Single-color bar settings.")


class SettingsModel31(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class ColorSettingsModel19(APIModel):
    """Bar color settings."""

    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: SettingsModel31 = Field(..., description="Two-color bar settings.")


class ScaleModel11(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class SettingsModel32(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class ScaleModel12(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: SettingsModel32 = Field(..., description="Manual bar scale boundaries.")


class SettingsModel33(APIModel):
    """Background color configuration."""

    palette_state: PaletteState = Field(
        ..., alias="paletteState", description="Discrete palette settings."
    )
    gradient_state: GradientState = Field(
        ..., alias="gradientState", description="Continuous gradient settings."
    )
    is_continuous: bool = Field(
        ...,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WidthModel17(APIModel):
    """Table column width settings."""

    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WidthModel18(APIModel):
    """Table column width settings."""

    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str = Field(..., description="Column width percentage.")


class WidthModel19(APIModel):
    """Table column width settings."""

    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str = Field(..., description="Column width in pixels.")


class WizardLabelsItemSchema(APIModel):
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    markup_type: Literal["none", "md", "html"] | str | None = Field(
        default=None,
        alias="markupType",
        description="Markup type used to render field values.",
    )
    formatting: Formatting | None = Field(
        default=None, description="Numeric formatting settings for the field."
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: BarsSettings | None = Field(
        default=None, alias="barsSettings", description="In-cell bar settings."
    )
    sub_totals_settings: SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings", description="Subtotal settings."
    )
    background_settings: BackgroundSettings | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Conditional background settings.",
    )
    column_settings: ColumnSettings | None = Field(
        default=None, alias="columnSettings", description="Table column settings."
    )
    hint_settings: HintSettings | None = Field(
        default=None, alias="hintSettings", description="Field hint settings."
    )
    guid: str = Field(..., description="Hierarchy identifier.")
    title: str = Field(..., description="Hierarchy display title.")
    data_type: Literal["hierarchy"] = Field(
        ..., description="Data type identifying this field as a hierarchy."
    )
    fields: list[FieldModel] = Field(..., description="Fields included in the hierarchy.")


class ThresholdsModel13(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class ThresholdsModel14(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str = Field(..., description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str = Field(..., description="Upper gradient threshold.")


class SettingsModel34(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str = Field(
        ..., alias="gradientType", description="Gradient type."
    )
    thresholds: ThresholdsModel13 | ThresholdsModel14 = Field(
        ..., description="Thresholds that define the gradient color scale."
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class ColorSettingsModel20(APIModel):
    """Bar color settings."""

    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: SettingsModel34 = Field(..., description="Gradient bar color settings.")


class SettingsModel35(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class ColorSettingsModel21(APIModel):
    """Bar color settings."""

    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: SettingsModel35 = Field(..., description="Single-color bar settings.")


class SettingsModel36(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class ColorSettingsModel22(APIModel):
    """Bar color settings."""

    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: SettingsModel36 = Field(..., description="Two-color bar settings.")


class ScaleModel13(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class SettingsModel37(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class ScaleModel14(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: SettingsModel37 = Field(..., description="Manual bar scale boundaries.")


class SettingsModel38(APIModel):
    """Background color configuration."""

    palette_state: PaletteState = Field(
        ..., alias="paletteState", description="Discrete palette settings."
    )
    gradient_state: GradientState = Field(
        ..., alias="gradientState", description="Continuous gradient settings."
    )
    is_continuous: bool = Field(
        ...,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WidthModel20(APIModel):
    """Table column width settings."""

    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WidthModel21(APIModel):
    """Table column width settings."""

    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str = Field(..., description="Column width percentage.")


class WidthModel22(APIModel):
    """Table column width settings."""

    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str = Field(..., description="Column width in pixels.")


class WizardLabelsItemSchemaModel(APIModel):
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    markup_type: Literal["none", "md", "html"] | str | None = Field(
        default=None,
        alias="markupType",
        description="Markup type used to render field values.",
    )
    formatting: Formatting | None = Field(
        default=None, description="Numeric formatting settings for the field."
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: BarsSettings | None = Field(
        default=None, alias="barsSettings", description="In-cell bar settings."
    )
    sub_totals_settings: SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings", description="Subtotal settings."
    )
    background_settings: BackgroundSettings | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Conditional background settings.",
    )
    column_settings: ColumnSettings | None = Field(
        default=None, alias="columnSettings", description="Table column settings."
    )
    hint_settings: HintSettings | None = Field(
        default=None, alias="hintSettings", description="Field hint settings."
    )
    guid: str = Field(..., description="Field identifier.")
    dataset_id: str = Field(
        ...,
        alias="datasetId",
        description="Identifier of the dataset containing the field.",
    )


class ThresholdsModel15(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class ThresholdsModel16(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str = Field(..., description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str = Field(..., description="Upper gradient threshold.")


class SettingsModel39(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str = Field(
        ..., alias="gradientType", description="Gradient type."
    )
    thresholds: ThresholdsModel15 | ThresholdsModel16 = Field(
        ..., description="Thresholds that define the gradient color scale."
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class ColorSettingsModel23(APIModel):
    """Bar color settings."""

    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: SettingsModel39 = Field(..., description="Gradient bar color settings.")


class SettingsModel40(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class ColorSettingsModel24(APIModel):
    """Bar color settings."""

    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: SettingsModel40 = Field(..., description="Single-color bar settings.")


class SettingsModel41(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class ColorSettingsModel25(APIModel):
    """Bar color settings."""

    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: SettingsModel41 = Field(..., description="Two-color bar settings.")


class ScaleModel15(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class SettingsModel42(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class ScaleModel16(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: SettingsModel42 = Field(..., description="Manual bar scale boundaries.")


class SettingsModel43(APIModel):
    """Background color configuration."""

    palette_state: PaletteState = Field(
        ..., alias="paletteState", description="Discrete palette settings."
    )
    gradient_state: GradientState = Field(
        ..., alias="gradientState", description="Continuous gradient settings."
    )
    is_continuous: bool = Field(
        ...,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WidthModel23(APIModel):
    """Table column width settings."""

    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WidthModel24(APIModel):
    """Table column width settings."""

    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str = Field(..., description="Column width percentage.")


class WidthModel25(APIModel):
    """Table column width settings."""

    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str = Field(..., description="Column width in pixels.")


class WizardLabelsItemSchemaModel1(APIModel):
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    markup_type: Literal["none", "md", "html"] | str | None = Field(
        default=None,
        alias="markupType",
        description="Markup type used to render field values.",
    )
    formatting: Formatting | None = Field(
        default=None, description="Numeric formatting settings for the field."
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: BarsSettings | None = Field(
        default=None, alias="barsSettings", description="In-cell bar settings."
    )
    sub_totals_settings: SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings", description="Subtotal settings."
    )
    background_settings: BackgroundSettings | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Conditional background settings.",
    )
    column_settings: ColumnSettings | None = Field(
        default=None, alias="columnSettings", description="Table column settings."
    )
    hint_settings: HintSettings | None = Field(
        default=None, alias="hintSettings", description="Field hint settings."
    )
    title: Literal["Measure Names"] = Field(
        ..., description="Title identifying the Measure Names pseudo-field."
    )
    type: Literal["PSEUDO"] = Field(..., description="Field type identifying a pseudo-field.")
    data_type: Literal["string"] = Field(
        ..., description="String data type of the Measure Names pseudo-field."
    )


class ThresholdsModel17(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class ThresholdsModel18(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str = Field(..., description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str = Field(..., description="Upper gradient threshold.")


class SettingsModel44(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str = Field(
        ..., alias="gradientType", description="Gradient type."
    )
    thresholds: ThresholdsModel17 | ThresholdsModel18 = Field(
        ..., description="Thresholds that define the gradient color scale."
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class ColorSettingsModel26(APIModel):
    """Bar color settings."""

    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: SettingsModel44 = Field(..., description="Gradient bar color settings.")


class SettingsModel45(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class ColorSettingsModel27(APIModel):
    """Bar color settings."""

    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: SettingsModel45 = Field(..., description="Single-color bar settings.")


class SettingsModel46(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class ColorSettingsModel28(APIModel):
    """Bar color settings."""

    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: SettingsModel46 = Field(..., description="Two-color bar settings.")


class ScaleModel17(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class SettingsModel47(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class ScaleModel18(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: SettingsModel47 = Field(..., description="Manual bar scale boundaries.")


class SettingsModel48(APIModel):
    """Background color configuration."""

    palette_state: PaletteState = Field(
        ..., alias="paletteState", description="Discrete palette settings."
    )
    gradient_state: GradientState = Field(
        ..., alias="gradientState", description="Continuous gradient settings."
    )
    is_continuous: bool = Field(
        ...,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WidthModel26(APIModel):
    """Table column width settings."""

    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WidthModel27(APIModel):
    """Table column width settings."""

    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str = Field(..., description="Column width percentage.")


class WidthModel28(APIModel):
    """Table column width settings."""

    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str = Field(..., description="Column width in pixels.")


class WizardLabelsItemSchemaModel2(APIModel):
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    markup_type: Literal["none", "md", "html"] | str | None = Field(
        default=None,
        alias="markupType",
        description="Markup type used to render field values.",
    )
    formatting: Formatting | None = Field(
        default=None, description="Numeric formatting settings for the field."
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: BarsSettings | None = Field(
        default=None, alias="barsSettings", description="In-cell bar settings."
    )
    sub_totals_settings: SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings", description="Subtotal settings."
    )
    background_settings: BackgroundSettings | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Conditional background settings.",
    )
    column_settings: ColumnSettings | None = Field(
        default=None, alias="columnSettings", description="Table column settings."
    )
    hint_settings: HintSettings | None = Field(
        default=None, alias="hintSettings", description="Field hint settings."
    )
    title: Literal["Measure Values"] = Field(
        ..., description="Title identifying the Measure Values pseudo-field."
    )
    type: Literal["PSEUDO"] = Field(..., description="Field type identifying a pseudo-field.")
    data_type: Literal["float"] = Field(
        ..., description="Numeric data type of the Measure Values pseudo-field."
    )


class WizardLabelsItemSchemaModel3(APIModel):
    label_percentage_base: Literal["auto", "first", "previous"] | str | None = Field(
        default=None,
        alias="labelPercentageBase",
        description="Base used to calculate percentage labels.",
    )


class WizardLabelsItemSchemaModel4(
    WizardLabelsItemSchema,
    WizardLabelsItemSchemaModel3,
):
    pass


class WizardLabelsItemSchemaModel5(
    WizardLabelsItemSchemaModel,
    WizardLabelsItemSchemaModel3,
):
    pass


class WizardLabelsItemSchemaModel6(
    WizardLabelsItemSchemaModel1,
    WizardLabelsItemSchemaModel3,
):
    pass


class WizardLabelsItemSchemaModel7(
    WizardLabelsItemSchemaModel2,
    WizardLabelsItemSchemaModel3,
):
    pass


class WizardLabelsItemSchemaModel8(
    RootModel[
        WizardLabelsItemSchemaModel4
        | WizardLabelsItemSchemaModel5
        | WizardLabelsItemSchemaModel6
        | WizardLabelsItemSchemaModel7
    ]
):
    root: (
        WizardLabelsItemSchemaModel4
        | WizardLabelsItemSchemaModel5
        | WizardLabelsItemSchemaModel6
        | WizardLabelsItemSchemaModel7
    )


class ThresholdsModel19(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class ThresholdsModel20(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str = Field(..., description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str = Field(..., description="Upper gradient threshold.")


class SettingsModel49(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str = Field(
        ..., alias="gradientType", description="Gradient type."
    )
    thresholds: ThresholdsModel19 | ThresholdsModel20 = Field(
        ..., description="Thresholds that define the gradient color scale."
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class ColorSettingsModel29(APIModel):
    """Bar color settings."""

    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: SettingsModel49 = Field(..., description="Gradient bar color settings.")


class SettingsModel50(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class ColorSettingsModel30(APIModel):
    """Bar color settings."""

    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: SettingsModel50 = Field(..., description="Single-color bar settings.")


class SettingsModel51(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class ColorSettingsModel31(APIModel):
    """Bar color settings."""

    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: SettingsModel51 = Field(..., description="Two-color bar settings.")


class ScaleModel19(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class SettingsModel52(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class ScaleModel20(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: SettingsModel52 = Field(..., description="Manual bar scale boundaries.")


class SettingsModel53(APIModel):
    """Background color configuration."""

    palette_state: PaletteState = Field(
        ..., alias="paletteState", description="Discrete palette settings."
    )
    gradient_state: GradientState = Field(
        ..., alias="gradientState", description="Continuous gradient settings."
    )
    is_continuous: bool = Field(
        ...,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WidthModel29(APIModel):
    """Table column width settings."""

    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WidthModel30(APIModel):
    """Table column width settings."""

    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str = Field(..., description="Column width percentage.")


class WidthModel31(APIModel):
    """Table column width settings."""

    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str = Field(..., description="Column width in pixels.")


class WizardPseudoFieldSchema(APIModel):
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    markup_type: Literal["none", "md", "html"] | str | None = Field(
        default=None,
        alias="markupType",
        description="Markup type used to render field values.",
    )
    formatting: Formatting | None = Field(
        default=None, description="Numeric formatting settings for the field."
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: BarsSettings | None = Field(
        default=None, alias="barsSettings", description="In-cell bar settings."
    )
    sub_totals_settings: SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings", description="Subtotal settings."
    )
    background_settings: BackgroundSettings | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Conditional background settings.",
    )
    column_settings: ColumnSettings | None = Field(
        default=None, alias="columnSettings", description="Table column settings."
    )
    hint_settings: HintSettings | None = Field(
        default=None, alias="hintSettings", description="Field hint settings."
    )
    title: Literal["Measure Names"] = Field(
        ..., description="Title identifying the Measure Names pseudo-field."
    )
    type: Literal["PSEUDO"] = Field(..., description="Field type identifying a pseudo-field.")
    data_type: Literal["string"] = Field(
        ..., description="String data type of the Measure Names pseudo-field."
    )


class ThresholdsModel21(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class ThresholdsModel22(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str = Field(..., description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str = Field(..., description="Upper gradient threshold.")


class SettingsModel54(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str = Field(
        ..., alias="gradientType", description="Gradient type."
    )
    thresholds: ThresholdsModel21 | ThresholdsModel22 = Field(
        ..., description="Thresholds that define the gradient color scale."
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class ColorSettingsModel32(APIModel):
    """Bar color settings."""

    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: SettingsModel54 = Field(..., description="Gradient bar color settings.")


class SettingsModel55(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class ColorSettingsModel33(APIModel):
    """Bar color settings."""

    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: SettingsModel55 = Field(..., description="Single-color bar settings.")


class SettingsModel56(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class ColorSettingsModel34(APIModel):
    """Bar color settings."""

    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: SettingsModel56 = Field(..., description="Two-color bar settings.")


class ScaleModel21(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class SettingsModel57(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class ScaleModel22(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: SettingsModel57 = Field(..., description="Manual bar scale boundaries.")


class SettingsModel58(APIModel):
    """Background color configuration."""

    palette_state: PaletteState = Field(
        ..., alias="paletteState", description="Discrete palette settings."
    )
    gradient_state: GradientState = Field(
        ..., alias="gradientState", description="Continuous gradient settings."
    )
    is_continuous: bool = Field(
        ...,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WidthModel32(APIModel):
    """Table column width settings."""

    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WidthModel33(APIModel):
    """Table column width settings."""

    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str = Field(..., description="Column width percentage.")


class WidthModel34(APIModel):
    """Table column width settings."""

    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str = Field(..., description="Column width in pixels.")


class WizardPseudoFieldSchemaModel(APIModel):
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    markup_type: Literal["none", "md", "html"] | str | None = Field(
        default=None,
        alias="markupType",
        description="Markup type used to render field values.",
    )
    formatting: Formatting | None = Field(
        default=None, description="Numeric formatting settings for the field."
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: BarsSettings | None = Field(
        default=None, alias="barsSettings", description="In-cell bar settings."
    )
    sub_totals_settings: SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings", description="Subtotal settings."
    )
    background_settings: BackgroundSettings | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Conditional background settings.",
    )
    column_settings: ColumnSettings | None = Field(
        default=None, alias="columnSettings", description="Table column settings."
    )
    hint_settings: HintSettings | None = Field(
        default=None, alias="hintSettings", description="Field hint settings."
    )
    title: Literal["Measure Values"] = Field(
        ..., description="Title identifying the Measure Values pseudo-field."
    )
    type: Literal["PSEUDO"] = Field(..., description="Field type identifying a pseudo-field.")
    data_type: Literal["float"] = Field(
        ..., description="Numeric data type of the Measure Values pseudo-field."
    )


class WizardPseudoFieldSchemaModel1(
    RootModel[WizardPseudoFieldSchema | WizardPseudoFieldSchemaModel]
):
    root: WizardPseudoFieldSchema | WizardPseudoFieldSchemaModel


class WizardSortItemSchema(APIModel):
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    direction: Literal["ASC", "DESC"] | str = Field(..., description="Sort direction.")
    guid: str = Field(..., description="Identifier of the field used for sorting.")
    dataset_id: str = Field(
        ...,
        alias="datasetId",
        description="Identifier of the dataset containing the field.",
    )


class ThresholdsModel23(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class ThresholdsModel24(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str = Field(..., description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str = Field(..., description="Upper gradient threshold.")


class SettingsModel59(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str = Field(
        ..., alias="gradientType", description="Gradient type."
    )
    thresholds: ThresholdsModel23 | ThresholdsModel24 = Field(
        ..., description="Thresholds that define the gradient color scale."
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class ColorSettingsModel35(APIModel):
    """Bar color settings."""

    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: SettingsModel59 = Field(..., description="Gradient bar color settings.")


class SettingsModel60(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class ColorSettingsModel36(APIModel):
    """Bar color settings."""

    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: SettingsModel60 = Field(..., description="Single-color bar settings.")


class SettingsModel61(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class ColorSettingsModel37(APIModel):
    """Bar color settings."""

    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: SettingsModel61 = Field(..., description="Two-color bar settings.")


class ScaleModel23(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class SettingsModel62(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class ScaleModel24(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: SettingsModel62 = Field(..., description="Manual bar scale boundaries.")


class SettingsModel63(APIModel):
    """Background color configuration."""

    palette_state: PaletteState = Field(
        ..., alias="paletteState", description="Discrete palette settings."
    )
    gradient_state: GradientState = Field(
        ..., alias="gradientState", description="Continuous gradient settings."
    )
    is_continuous: bool = Field(
        ...,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WidthModel35(APIModel):
    """Table column width settings."""

    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WidthModel36(APIModel):
    """Table column width settings."""

    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str = Field(..., description="Column width percentage.")


class WidthModel37(APIModel):
    """Table column width settings."""

    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str = Field(..., description="Column width in pixels.")


class WizardSortItemSchemaModel(APIModel):
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    markup_type: Literal["none", "md", "html"] | str | None = Field(
        default=None,
        alias="markupType",
        description="Markup type used to render field values.",
    )
    formatting: Formatting | None = Field(
        default=None, description="Numeric formatting settings for the field."
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: BarsSettings | None = Field(
        default=None, alias="barsSettings", description="In-cell bar settings."
    )
    sub_totals_settings: SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings", description="Subtotal settings."
    )
    background_settings: BackgroundSettings | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Conditional background settings.",
    )
    column_settings: ColumnSettings | None = Field(
        default=None, alias="columnSettings", description="Table column settings."
    )
    hint_settings: HintSettings | None = Field(
        default=None, alias="hintSettings", description="Field hint settings."
    )
    title: Literal["Measure Names"] = Field(
        ..., description="Title identifying the Measure Names pseudo-field."
    )
    type: Literal["PSEUDO"] = Field(..., description="Field type identifying a pseudo-field.")
    data_type: Literal["string"] = Field(
        ..., description="String data type of the Measure Names pseudo-field."
    )


class ThresholdsModel25(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class ThresholdsModel26(APIModel):
    """Thresholds that define the gradient color scale."""

    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str = Field(..., description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str = Field(..., description="Upper gradient threshold.")


class SettingsModel64(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str = Field(
        ..., alias="gradientType", description="Gradient type."
    )
    thresholds: ThresholdsModel25 | ThresholdsModel26 = Field(
        ..., description="Thresholds that define the gradient color scale."
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class ColorSettingsModel38(APIModel):
    """Bar color settings."""

    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: SettingsModel64 = Field(..., description="Gradient bar color settings.")


class SettingsModel65(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class ColorSettingsModel39(APIModel):
    """Bar color settings."""

    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: SettingsModel65 = Field(..., description="Single-color bar settings.")


class SettingsModel66(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class ColorSettingsModel40(APIModel):
    """Bar color settings."""

    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: SettingsModel66 = Field(..., description="Two-color bar settings.")


class ScaleModel25(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class SettingsModel67(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class ScaleModel26(APIModel):
    """Scale used to calculate bar lengths."""

    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: SettingsModel67 = Field(..., description="Manual bar scale boundaries.")


class SettingsModel68(APIModel):
    """Background color configuration."""

    palette_state: PaletteState = Field(
        ..., alias="paletteState", description="Discrete palette settings."
    )
    gradient_state: GradientState = Field(
        ..., alias="gradientState", description="Continuous gradient settings."
    )
    is_continuous: bool = Field(
        ...,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WidthModel38(APIModel):
    """Table column width settings."""

    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WidthModel39(APIModel):
    """Table column width settings."""

    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str = Field(..., description="Column width percentage.")


class WidthModel40(APIModel):
    """Table column width settings."""

    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str = Field(..., description="Column width in pixels.")


class WizardSortItemSchemaModel1(APIModel):
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    markup_type: Literal["none", "md", "html"] | str | None = Field(
        default=None,
        alias="markupType",
        description="Markup type used to render field values.",
    )
    formatting: Formatting | None = Field(
        default=None, description="Numeric formatting settings for the field."
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: BarsSettings | None = Field(
        default=None, alias="barsSettings", description="In-cell bar settings."
    )
    sub_totals_settings: SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings", description="Subtotal settings."
    )
    background_settings: BackgroundSettings | None = Field(
        default=None,
        alias="backgroundSettings",
        description="Conditional background settings.",
    )
    column_settings: ColumnSettings | None = Field(
        default=None, alias="columnSettings", description="Table column settings."
    )
    hint_settings: HintSettings | None = Field(
        default=None, alias="hintSettings", description="Field hint settings."
    )
    title: Literal["Measure Values"] = Field(
        ..., description="Title identifying the Measure Values pseudo-field."
    )
    type: Literal["PSEUDO"] = Field(..., description="Field type identifying a pseudo-field.")
    data_type: Literal["float"] = Field(
        ..., description="Numeric data type of the Measure Values pseudo-field."
    )


class WizardSortItemSchemaModel2(APIModel):
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    direction: Literal["ASC", "DESC"] | str = Field(..., description="Sort direction.")


class WizardSortItemSchemaModel3(WizardSortItemSchemaModel, WizardSortItemSchemaModel2):
    pass


class WizardSortItemSchemaModel4(
    WizardSortItemSchemaModel1,
    WizardSortItemSchemaModel2,
):
    pass


class WizardSortItemSchemaModel5(
    RootModel[WizardSortItemSchemaModel3 | WizardSortItemSchemaModel4]
):
    root: WizardSortItemSchemaModel3 | WizardSortItemSchemaModel4


class WizardSortItemSchemaModel6(RootModel[WizardSortItemSchema | WizardSortItemSchemaModel5]):
    root: WizardSortItemSchema | WizardSortItemSchemaModel5


class LayerSettings(APIModel):
    """Geographic layer configuration."""

    id: str = Field(..., description="Unique layer identifier.")
    name: str = Field(..., description="Layer display name.")
    alpha: float | None = Field(
        default=None, description="Layer opacity as a percentage from 0 to 100."
    )


class Points(APIModel):
    """Point coordinate configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ..., description="Fields containing point coordinates."
    )


class SettingsModel69(APIModel):
    """Map point size settings."""

    radius: float | None = Field(default=None, description="Radius of map points in pixels.")


class Size(APIModel):
    """Point size configuration."""

    items: list[WizardFieldSchemaModel3] | None = Field(
        default=None, description="Fields used to determine map point sizes."
    )
    settings: SettingsModel69 | None = Field(default=None, description="Map point size settings.")


class SettingsModel70(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchemaModel3] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: SettingsModel70 | None = Field(default=None, description="Color settings.")


class Labels(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel8] | None = Field(
        default=None, description="Fields whose values are displayed as point labels."
    )


class SettingsModel71(APIModel):
    """Tooltip display settings."""

    color: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether to display series colors in the tooltip."
    )
    field_title: Literal["on", "off"] | str | None = Field(
        default=None,
        alias="fieldTitle",
        description="Whether to display field titles in the tooltip.",
    )


class Tooltip(APIModel):
    """Tooltip configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ..., description="Fields displayed in point tooltips."
    )
    settings: SettingsModel71 | None = Field(default=None, description="Tooltip display settings.")


class Filters(APIModel):
    """Filter configuration."""

    items: list[WizardV1FiltersItemSchema] | None = Field(
        default=None, description="Filters applied to the layer."
    )


class WizardV1GeolayerLayerSchema(APIModel):
    type: Literal["geopoint"] = Field(..., description="Geopoint layer type.")
    layer_settings: LayerSettings = Field(
        ..., alias="layerSettings", description="Geographic layer configuration."
    )
    points: Points = Field(..., description="Point coordinate configuration.")
    size: Size | None = Field(default=None, description="Point size configuration.")
    colors: Colors | None = Field(default=None, description="Color configuration.")
    labels: Labels | None = Field(default=None, description="Data label configuration.")
    tooltip: Tooltip | None = Field(default=None, description="Tooltip configuration.")
    filters: Filters | None = Field(default=None, description="Filter configuration.")


class SettingsModel72(APIModel):
    """Map point size settings."""

    radius: float | None = Field(default=None, description="Radius of map points in pixels.")


class SettingsModel73(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class SettingsModel74(APIModel):
    """Tooltip display settings."""

    color: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether to display series colors in the tooltip."
    )
    field_title: Literal["on", "off"] | str | None = Field(
        default=None,
        alias="fieldTitle",
        description="Whether to display field titles in the tooltip.",
    )


class WizardV1GeolayerLayerSchemaModel(APIModel):
    layer_settings: LayerSettings = Field(
        ..., alias="layerSettings", description="Geographic layer configuration."
    )
    points: Points = Field(..., description="Point coordinate configuration.")
    size: Size | None = Field(default=None, description="Point size configuration.")
    colors: Colors | None = Field(default=None, description="Color configuration.")
    labels: Labels | None = Field(default=None, description="Data label configuration.")
    tooltip: Tooltip | None = Field(default=None, description="Tooltip configuration.")
    filters: Filters | None = Field(default=None, description="Filter configuration.")
    type: Literal["geopoint-with-cluster"] = Field(
        ..., description="Clustered geopoint layer type."
    )


class SettingsModel75(APIModel):
    """Polyline display settings."""

    polyline_points: Literal["on", "off"] | str | None = Field(
        default=None,
        alias="polylinePoints",
        description="Whether vertices are displayed on polylines.",
    )


class Polylines(APIModel):
    """Polyline configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ..., description="Fields containing polyline coordinates."
    )
    settings: SettingsModel75 | None = Field(default=None, description="Polyline display settings.")


class Measures(APIModel):
    """Measure configuration."""

    items: list[WizardFieldSchemaModel3] | None = Field(
        default=None, description="Measures displayed in polyline tooltips."
    )


class Grouping(APIModel):
    """Grouping configuration."""

    items: list[WizardFieldSchemaModel3] | None = Field(
        default=None, description="Fields used to group polyline points."
    )


class SettingsModel76(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel6] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1GeolayerLayerSchemaModel1(APIModel):
    type: Literal["polyline"] = Field(..., description="Geopolyline layer type.")
    layer_settings: LayerSettings = Field(
        ..., alias="layerSettings", description="Geographic layer configuration."
    )
    polylines: Polylines = Field(..., description="Polyline configuration.")
    measures: Measures | None = Field(default=None, description="Measure configuration.")
    grouping: Grouping | None = Field(default=None, description="Grouping configuration.")
    colors: Colors | None = Field(default=None, description="Color configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")
    filters: Filters | None = Field(default=None, description="Filter configuration.")


class Polygons(APIModel):
    """Polygon configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ..., description="Fields containing polygon geometry."
    )


class SettingsModel77(APIModel):
    """Tooltip display settings."""

    color: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether to display series colors in the tooltip."
    )
    field_title: Literal["on", "off"] | str | None = Field(
        default=None,
        alias="fieldTitle",
        description="Whether to display field titles in the tooltip.",
    )


class TooltipModel(APIModel):
    """Tooltip configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ..., description="Fields displayed in polygon tooltips."
    )
    settings: SettingsModel77 | None = Field(default=None, description="Tooltip display settings.")


class WizardV1GeolayerLayerSchemaModel2(APIModel):
    type: Literal["geopolygon"] = Field(..., description="Geopolygon layer type.")
    layer_settings: LayerSettings = Field(
        ..., alias="layerSettings", description="Geographic layer configuration."
    )
    polygons: Polygons = Field(..., description="Polygon configuration.")
    colors: Colors | None = Field(default=None, description="Color configuration.")
    tooltip: TooltipModel | None = Field(default=None, description="Tooltip configuration.")
    filters: Filters | None = Field(default=None, description="Filter configuration.")


class PointsModel(APIModel):
    """Point coordinate configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ..., description="Fields containing heatmap point coordinates."
    )


class SettingsModel78(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class WizardV1GeolayerLayerSchemaModel3(APIModel):
    type: Literal["heatmap"] = Field(..., description="Geo heatmap layer type.")
    layer_settings: LayerSettings = Field(
        ..., alias="layerSettings", description="Geographic layer configuration."
    )
    points: PointsModel = Field(..., description="Point coordinate configuration.")
    colors: Colors | None = Field(default=None, description="Color configuration.")
    filters: Filters | None = Field(default=None, description="Filter configuration.")


class WizardV1GeolayerLayerSchemaModel4(
    RootModel[
        WizardV1GeolayerLayerSchema
        | WizardV1GeolayerLayerSchemaModel
        | WizardV1GeolayerLayerSchemaModel1
        | WizardV1GeolayerLayerSchemaModel2
        | WizardV1GeolayerLayerSchemaModel3
    ]
):
    root: (
        WizardV1GeolayerLayerSchema
        | WizardV1GeolayerLayerSchemaModel
        | WizardV1GeolayerLayerSchemaModel1
        | WizardV1GeolayerLayerSchemaModel2
        | WizardV1GeolayerLayerSchemaModel3
    )


class LayerSettingsModel(APIModel):
    """Layer configuration."""

    id: str = Field(..., description="Unique layer identifier.")
    name: str = Field(..., description="Layer display name.")


class AxisLabelFormatting(APIModel):
    """Numeric axis label formatting."""

    format: Literal["number", "percent"] | str | None = Field(
        default=None, description="Number formatting mode."
    )
    show_rank_delimiter: bool | None = Field(
        default=None,
        alias="showRankDelimiter",
        description="Whether to separate digit groups in numbers.",
    )
    prefix: str | None = Field(
        default=None, description="Text displayed before the formatted value."
    )
    postfix: str | None = Field(
        default=None, description="Text displayed after the formatted value."
    )
    unit: Literal["auto", "k", "m", "b", "t"] | str | None = Field(
        default=None, description="Unit used to scale the numeric value."
    )
    precision: float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class SettingsModel79(APIModel):
    """X-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    holidays: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether holidays are highlighted on the axis."
    )
    axis_mode_map: dict[str, Literal["discrete", "continuous"] | str] | None = Field(
        default=None,
        alias="axisModeMap",
        description="Maps field GUIDs to discrete or continuous axis modes.",
    )


class X(APIModel):
    """X-axis configuration."""

    items: list[WizardFieldSchemaModel3] = Field(..., description="Fields placed on the X-axis.")
    settings: SettingsModel79 | None = Field(default=None, description="X-axis settings.")


class SettingsModel80(APIModel):
    """Primary Y-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    scale: Literal["auto", "manual"] | str | None = Field(
        default=None, description="Axis boundary calculation mode."
    )
    scale_value: Literal["min-max", "data-min-max", "0-max"] | str | list[Any] | None = Field(
        default=None,
        alias="scaleValue",
        description="Automatic scale mode or manual minimum and maximum values.",
    )
    nulls: Literal["ignore", "connect", "as-0", "use-previous"] | str | None = Field(
        default=None, description="How null values are displayed."
    )


class Y(APIModel):
    """Primary Y-axis configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ...,
        description="Fields placed on the primary Y-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: SettingsModel80 | None = Field(default=None, description="Primary Y-axis settings.")


class SettingsModel81(APIModel):
    """Secondary Y-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    scale: Literal["auto", "manual"] | str | None = Field(
        default=None, description="Axis boundary calculation mode."
    )
    scale_value: Literal["min-max", "data-min-max", "0-max"] | str | list[Any] | None = Field(
        default=None,
        alias="scaleValue",
        description="Automatic scale mode or manual minimum and maximum values.",
    )
    nulls: Literal["ignore", "connect", "as-0", "use-previous"] | str | None = Field(
        default=None, description="How null values are displayed."
    )


class Y2(APIModel):
    """Secondary Y-axis configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ...,
        description="Fields placed on the secondary Y-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: SettingsModel81 | None = Field(default=None, description="Secondary Y-axis settings.")


class SettingsModel82(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class CommonLineSettings(APIModel):
    """Line shape settings shared by all series."""

    line_width: float | Literal["auto"] | None = Field(
        default=None,
        alias="lineWidth",
        description="Line width in pixels or automatic width.",
    )
    linecap: Literal["butt", "round", "square", "none"] | str | None = Field(
        default=None, description="Shape used at line endpoints."
    )
    linejoin: Literal["bevel", "round", "miter", "unset"] | str | None = Field(
        default=None, description="Shape used at line segment joins."
    )


class SettingsModel83(APIModel):
    """Line shape settings."""

    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used to assign shapes.",
    )
    mounted_shapes: dict[str, str] | None = Field(
        default=None,
        alias="mountedShapes",
        description="Mapping of series or field values to line dash styles.",
    )
    line_settings: dict[str, WizardV1LineShapeSettingsSchema] | None = Field(
        default=None, alias="lineSettings", description="Line shape settings by series."
    )
    common_line_settings: CommonLineSettings | None = Field(
        default=None,
        alias="commonLineSettings",
        description="Line shape settings shared by all series.",
    )


class Shapes(APIModel):
    """Line shape configuration."""

    items: list[WizardFieldSchemaModel3] | None = Field(
        default=None, description="Fields used for line encoding."
    )
    settings: SettingsModel83 | None = Field(default=None, description="Line shape settings.")


class SettingsModel84(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )


class LabelsModel(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel8] | None = Field(
        default=None, description="Fields whose values are displayed as data labels."
    )
    settings: SettingsModel84 | None = Field(default=None, description="Data label settings.")


class WizardV1CombinedChartLayerSchema(APIModel):
    type: Literal["line"] = Field(..., description="Line layer type.")
    layer_settings: LayerSettingsModel = Field(
        ..., alias="layerSettings", description="Layer configuration."
    )
    x: X = Field(..., description="X-axis configuration.")
    y: Y | None = Field(default=None, description="Primary Y-axis configuration.")
    y2: Y2 | None = Field(default=None, description="Secondary Y-axis configuration.")
    colors: Colors | None = Field(default=None, description="Color configuration.")
    shapes: Shapes | None = Field(default=None, description="Line shape configuration.")
    labels: LabelsModel | None = Field(default=None, description="Data label configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")


class SettingsModel85(APIModel):
    """X-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    holidays: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether holidays are highlighted on the axis."
    )
    axis_mode_map: dict[str, Literal["discrete", "continuous"] | str] | None = Field(
        default=None,
        alias="axisModeMap",
        description="Maps field GUIDs to discrete or continuous axis modes.",
    )


class SettingsModel86(APIModel):
    """Y-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    scale: Literal["auto", "manual"] | str | None = Field(
        default=None, description="Axis boundary calculation mode."
    )
    scale_value: Literal["min-max", "data-min-max", "0-max"] | str | list[Any] | None = Field(
        default=None,
        alias="scaleValue",
        description="Automatic scale mode or manual minimum and maximum values.",
    )
    nulls: Literal["ignore", "connect", "as-0", "use-previous"] | str | None = Field(
        default=None, description="How null values are displayed."
    )


class YModel(APIModel):
    """Y-axis configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ...,
        description="Fields placed on the Y-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: SettingsModel86 | None = Field(default=None, description="Y-axis settings.")


class SettingsModel87(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class SettingsModel88(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )
    labels_position: Literal["outside", "inside"] | str | None = Field(
        default=None,
        alias="labelsPosition",
        description="Position of data labels relative to columns.",
    )


class LabelsModel1(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel8] | None = Field(
        default=None, description="Fields whose values are displayed as data labels."
    )
    settings: SettingsModel88 | None = Field(default=None, description="Data label settings.")


class WizardV1CombinedChartLayerSchemaModel(APIModel):
    type: Literal["column"] = Field(..., description="Column layer type.")
    layer_settings: LayerSettingsModel = Field(
        ..., alias="layerSettings", description="Layer configuration."
    )
    x: X = Field(..., description="X-axis configuration.")
    y: YModel | None = Field(default=None, description="Y-axis configuration.")
    colors: Colors | None = Field(default=None, description="Color configuration.")
    labels: LabelsModel1 | None = Field(default=None, description="Data label configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")


class SettingsModel89(APIModel):
    """X-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    holidays: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether holidays are highlighted on the axis."
    )
    axis_mode_map: dict[str, Literal["discrete", "continuous"] | str] | None = Field(
        default=None,
        alias="axisModeMap",
        description="Maps field GUIDs to discrete or continuous axis modes.",
    )


class SettingsModel90(APIModel):
    """Y-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    scale: Literal["auto", "manual"] | str | None = Field(
        default=None, description="Axis boundary calculation mode."
    )
    scale_value: Literal["min-max", "data-min-max", "0-max"] | str | list[Any] | None = Field(
        default=None,
        alias="scaleValue",
        description="Automatic scale mode or manual minimum and maximum values.",
    )
    nulls: Literal["ignore", "connect", "as-0", "use-previous"] | str | None = Field(
        default=None, description="How null values are displayed."
    )


class SettingsModel91(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class SettingsModel92(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )


class WizardV1CombinedChartLayerSchemaModel1(APIModel):
    type: Literal["area"] = Field(..., description="Area layer type.")
    layer_settings: LayerSettingsModel = Field(
        ..., alias="layerSettings", description="Layer configuration."
    )
    x: X = Field(..., description="X-axis configuration.")
    y: YModel | None = Field(default=None, description="Y-axis configuration.")
    colors: Colors | None = Field(default=None, description="Color configuration.")
    labels: LabelsModel | None = Field(default=None, description="Data label configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")


class WizardV1CombinedChartLayerSchemaModel2(
    RootModel[
        WizardV1CombinedChartLayerSchema
        | WizardV1CombinedChartLayerSchemaModel
        | WizardV1CombinedChartLayerSchemaModel1
    ]
):
    root: (
        WizardV1CombinedChartLayerSchema
        | WizardV1CombinedChartLayerSchemaModel
        | WizardV1CombinedChartLayerSchemaModel1
    )


class FieldModel1(APIModel):
    """Field properties changed by the operation."""

    guid: str = Field(..., description="Unique field identifier.")
    dataset_id: str | None = Field(
        default=None,
        alias="datasetId",
        description="Identifier of the dataset containing the field.",
    )
    title: str | None = Field(default=None, description="Field display title.")
    type: Literal["DIMENSION", "MEASURE", "PSEUDO", "PARAMETER"] | str | None = Field(
        default=None, description="Field role in the chart."
    )
    calc_mode: Literal["formula", "direct", "parameter"] | str | None = Field(
        default=None, description="Field calculation mode."
    )
    formula: str | None = Field(default=None, description="Formula used to calculate the field.")
    aggregation: str | None = Field(default=None, description="Aggregation applied to the field.")
    cast: str | None = Field(default=None, description="Data type conversion applied to the field.")
    source: str | None = Field(default=None, description="Source expression or source field name.")
    data_type: (
        Literal[
            "date",
            "genericdatetime",
            "datetimetz",
            "integer",
            "uinteger",
            "string",
            "float",
            "boolean",
            "geopoint",
            "geopolygon",
            "markup",
            "heatmap",
            "array_int",
            "array_float",
            "array_str",
            "unsupported",
            "hierarchy",
            "tree_str",
            "tree_int",
            "tree_float",
        ]
        | str
        | None
    ) = Field(default=None, description="Field data type.")
    aggregation_locked: bool | None = Field(
        default=None, description="Whether the field aggregation cannot be changed."
    )
    autoaggregated: bool | None = Field(
        default=None, description="Whether the field is aggregated automatically."
    )
    grouping: str | None = Field(default=None, description="Date or numeric grouping mode.")
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    original_title: str | None = Field(
        default=None,
        alias="originalTitle",
        description="Original field title before local changes.",
    )
    avatar_id: str | None = Field(
        default=None,
        description="Identifier of the dataset source containing the field.",
    )
    local: bool | None = Field(
        default=None, description="Whether the field exists only in this chart."
    )
    quick_formula: bool | None = Field(
        default=None,
        alias="quickFormula",
        description="Whether the field was created with a quick formula.",
    )
    original_formula: str | None = Field(
        default=None,
        alias="originalFormula",
        description="Formula before local transformations.",
    )
    original_source: str | None = Field(
        default=None,
        alias="originalSource",
        description="Source before local transformations.",
    )
    original_date_cast: (
        Literal[
            "date",
            "genericdatetime",
            "datetimetz",
            "integer",
            "uinteger",
            "string",
            "float",
            "boolean",
            "geopoint",
            "geopolygon",
            "markup",
            "heatmap",
            "array_int",
            "array_float",
            "array_str",
            "unsupported",
            "hierarchy",
            "tree_str",
            "tree_int",
            "tree_float",
        ]
        | str
        | None
    ) = Field(
        default=None,
        alias="originalDateCast",
        description="Original date data type before local conversion.",
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    default_value: str | float | bool | None = Field(
        default=None, description="Value of a parameter added in the chart."
    )


class Update(APIModel):
    action: (
        Literal["add_field", "add", "update_field", "update", "delete", "delete_field"] | str
    ) = Field(..., description="Operation applied to the local field.")
    field: FieldModel1 = Field(..., description="Field properties changed by the operation.")
    debug_info: str | None = Field(
        default=None,
        description="Internal marker describing how the field update was produced.",
    )


class FieldModel2(APIModel):
    """Field participating in the dataset link."""

    title: str = Field(..., description="Linked field title.")
    guid: str = Field(..., description="Linked field identifier.")


class Dataset(APIModel):
    """Dataset containing the linked field."""

    id: str = Field(..., description="Linked dataset identifier.")
    real_name: str = Field(..., alias="realName", description="Linked dataset display name.")


class Fields(APIModel):
    field: FieldModel2 = Field(..., description="Field participating in the dataset link.")
    dataset: Dataset = Field(..., description="Dataset containing the linked field.")


class Link(APIModel):
    id: str = Field(..., description="Dataset link identifier.")
    fields: dict[str, Fields] = Field(
        ..., description="Linked field information keyed by dataset identifier."
    )


class FieldModel3(APIModel):
    guid: str = Field(..., description="Identifier of a field in the hierarchy.")
    dataset_id: str = Field(
        ...,
        alias="datasetId",
        description="Identifier of the dataset containing the field.",
    )


class Hierarchy(APIModel):
    guid: str = Field(..., description="Hierarchy identifier.")
    title: str = Field(..., description="Hierarchy display title.")
    fields: list[FieldModel3] = Field(..., description="Ordered fields included in the hierarchy.")


class Sources(APIModel):
    """Data sources, chart-local field updates, dataset links, hierarchies, and filters used by the chart."""

    datasets_ids: list[str] = Field(
        ...,
        alias="datasetsIds",
        description="Datasets used by the chart to retrieve data.",
    )
    updates: list[Update] | None = Field(
        default=None,
        description="Operations that add, update, or delete chart-local fields.",
    )
    links: list[Link] | None = Field(
        default=None,
        description="Fields used to link datasets in multi-dataset charts.",
    )
    hierarchies: list[Hierarchy] | None = Field(
        default=None,
        description="Sets of fields used for interactive drill-down in the chart.",
    )
    filters: list[WizardV1FiltersItemSchema] | None = Field(
        default=None, description="Filters applied to chart data."
    )


class PeriodSettings(APIModel):
    """Size and unit of the initial navigator window."""

    type: (
        Literal[
            "date",
            "genericdatetime",
            "datetimetz",
            "integer",
            "uinteger",
            "string",
            "float",
            "boolean",
            "geopoint",
            "geopolygon",
            "markup",
            "heatmap",
            "array_int",
            "array_float",
            "array_str",
            "unsupported",
            "hierarchy",
            "tree_str",
            "tree_int",
            "tree_float",
        ]
        | str
    ) = Field(..., description="Data type of the navigator axis field.")
    value: str = Field(..., description="Initial navigator window size.")
    period: Literal["month", "year", "day", "hour", "week", "quarter"] | str = Field(
        ..., description="Unit of the navigator window size."
    )


class NavigatorSettings(APIModel):
    """Chart navigator settings."""

    navigator_mode: Literal["show", "hide"] | str = Field(
        ...,
        alias="navigatorMode",
        description="Whether the chart navigator is displayed.",
    )
    selected_lines: list[str] = Field(
        ...,
        alias="selectedLines",
        description="Series names shown in the navigator; values are not field GUIDs.",
    )
    lines_mode: Literal["all", "selected"] | str = Field(
        ...,
        alias="linesMode",
        description="Which chart series are displayed in the navigator.",
    )
    period_settings: PeriodSettings = Field(
        ...,
        alias="periodSettings",
        description="Size and unit of the initial navigator window.",
    )


class ChartSettings(APIModel):
    """Chart configuration."""

    title: str | None = Field(default=None, description="Chart title.")
    title_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="titleMode",
        description="Whether the chart title is displayed.",
    )
    legend_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="legendMode",
        description="Whether the chart legend is displayed.",
    )
    tooltip: Literal["show", "hide"] | str | None = Field(
        default=None, description="Whether chart tooltips are displayed."
    )
    tooltip_sum: Literal["on", "off"] | str | None = Field(
        default=None,
        alias="tooltipSum",
        description="Whether tooltips include a total value.",
    )
    feed: str | None = Field(default=None, description="Comment feed identifier.")
    navigator_settings: NavigatorSettings | None = Field(
        default=None, alias="navigatorSettings", description="Chart navigator settings."
    )


class SettingsModel93(APIModel):
    """X-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    holidays: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether holidays are highlighted on the axis."
    )
    axis_mode_map: dict[str, Literal["discrete", "continuous"] | str] | None = Field(
        default=None,
        alias="axisModeMap",
        description="Maps field GUIDs to discrete or continuous axis modes.",
    )


class SettingsModel94(APIModel):
    """Primary Y-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    scale: Literal["auto", "manual"] | str | None = Field(
        default=None, description="Axis boundary calculation mode."
    )
    scale_value: Literal["min-max", "data-min-max", "0-max"] | str | list[Any] | None = Field(
        default=None,
        alias="scaleValue",
        description="Automatic scale mode or manual minimum and maximum values.",
    )
    nulls: Literal["ignore", "connect", "as-0", "use-previous"] | str | None = Field(
        default=None, description="How null values are displayed."
    )


class YModel1(APIModel):
    """Primary Y-axis configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ...,
        description="Fields placed on the primary Y-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: SettingsModel94 | None = Field(default=None, description="Primary Y-axis settings.")


class SettingsModel95(APIModel):
    """Secondary Y-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    scale: Literal["auto", "manual"] | str | None = Field(
        default=None, description="Axis boundary calculation mode."
    )
    scale_value: Literal["min-max", "data-min-max", "0-max"] | str | list[Any] | None = Field(
        default=None,
        alias="scaleValue",
        description="Automatic scale mode or manual minimum and maximum values.",
    )
    nulls: Literal["ignore", "connect", "as-0", "use-previous"] | str | None = Field(
        default=None, description="How null values are displayed."
    )


class SettingsModel96(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class SettingsModel97(APIModel):
    """Line shape settings."""

    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used to assign shapes.",
    )
    mounted_shapes: dict[str, str] | None = Field(
        default=None,
        alias="mountedShapes",
        description="Mapping of series or field values to line dash styles.",
    )
    line_settings: dict[str, WizardV1LineShapeSettingsSchema] | None = Field(
        default=None, alias="lineSettings", description="Line shape settings by series."
    )
    common_line_settings: CommonLineSettings | None = Field(
        default=None,
        alias="commonLineSettings",
        description="Line shape settings shared by all series.",
    )


class SettingsModel98(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )


class Segments(APIModel):
    """Segmentation configuration."""

    items: list[WizardFieldSchemaModel3] | None = Field(
        default=None, description="Fields used to split the chart into segments."
    )


class Visualization(APIModel):
    """Chart visualization configuration."""

    type: Literal["line"] = Field(..., description="Line visualization type.")
    chart_settings: ChartSettings | None = Field(
        default=None, alias="chartSettings", description="Chart configuration."
    )
    x: X = Field(..., description="X-axis configuration.")
    y: YModel1 | None = Field(default=None, description="Primary Y-axis configuration.")
    y2: Y2 | None = Field(default=None, description="Secondary Y-axis configuration.")
    colors: Colors | None = Field(default=None, description="Color configuration.")
    shapes: Shapes | None = Field(default=None, description="Line shape configuration.")
    labels: LabelsModel | None = Field(default=None, description="Data label configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")
    segments: Segments | None = Field(default=None, description="Segmentation configuration.")


class SettingsModel99(APIModel):
    """X-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    holidays: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether holidays are highlighted on the axis."
    )
    axis_mode_map: dict[str, Literal["discrete", "continuous"] | str] | None = Field(
        default=None,
        alias="axisModeMap",
        description="Maps field GUIDs to discrete or continuous axis modes.",
    )


class SettingsModel100(APIModel):
    """Y-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    scale: Literal["auto", "manual"] | str | None = Field(
        default=None, description="Axis boundary calculation mode."
    )
    scale_value: Literal["min-max", "data-min-max", "0-max"] | str | list[Any] | None = Field(
        default=None,
        alias="scaleValue",
        description="Automatic scale mode or manual minimum and maximum values.",
    )
    nulls: Literal["ignore", "connect", "as-0", "use-previous"] | str | None = Field(
        default=None, description="How null values are displayed."
    )


class YModel2(APIModel):
    """Y-axis configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ...,
        description="Fields placed on the Y-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: SettingsModel100 | None = Field(default=None, description="Y-axis settings.")


class SettingsModel101(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class SettingsModel102(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )
    labels_position: Literal["outside", "inside"] | str | None = Field(
        default=None,
        alias="labelsPosition",
        description="Position of data labels relative to columns.",
    )


class LabelsModel2(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel8] | None = Field(
        default=None, description="Fields whose values are displayed as data labels."
    )
    settings: SettingsModel102 | None = Field(default=None, description="Data label settings.")


class VisualizationModel(APIModel):
    """Chart visualization configuration."""

    type: Literal["column"] = Field(..., description="Column visualization type.")
    chart_settings: ChartSettings | None = Field(
        default=None, alias="chartSettings", description="Chart configuration."
    )
    x: X = Field(..., description="X-axis configuration.")
    y: YModel2 | None = Field(default=None, description="Y-axis configuration.")
    colors: Colors | None = Field(default=None, description="Color configuration.")
    labels: LabelsModel2 | None = Field(default=None, description="Data label configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")
    segments: Segments | None = Field(default=None, description="Segmentation configuration.")


class SettingsModel103(APIModel):
    """X-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    holidays: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether holidays are highlighted on the axis."
    )
    axis_mode_map: dict[str, Literal["discrete", "continuous"] | str] | None = Field(
        default=None,
        alias="axisModeMap",
        description="Maps field GUIDs to discrete or continuous axis modes.",
    )


class SettingsModel104(APIModel):
    """Y-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    scale: Literal["auto", "manual"] | str | None = Field(
        default=None, description="Axis boundary calculation mode."
    )
    scale_value: Literal["min-max", "data-min-max", "0-max"] | str | list[Any] | None = Field(
        default=None,
        alias="scaleValue",
        description="Automatic scale mode or manual minimum and maximum values.",
    )
    nulls: Literal["ignore", "connect", "as-0", "use-previous"] | str | None = Field(
        default=None, description="How null values are displayed."
    )


class SettingsModel105(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class SettingsModel106(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )


class VisualizationModel1(APIModel):
    """Chart visualization configuration."""

    chart_settings: ChartSettings | None = Field(
        default=None, alias="chartSettings", description="Chart configuration."
    )
    x: X = Field(..., description="X-axis configuration.")
    y: YModel2 | None = Field(default=None, description="Y-axis configuration.")
    colors: Colors | None = Field(default=None, description="Color configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")
    segments: Segments | None = Field(default=None, description="Segmentation configuration.")
    type: Literal["column100p"] = Field(..., description="Normalized column visualization type.")
    labels: LabelsModel | None = Field(default=None, description="Data label configuration.")


class ChartSettingsModel(APIModel):
    """Chart configuration."""

    title: str | None = Field(default=None, description="Chart title.")
    title_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="titleMode",
        description="Whether the chart title is displayed.",
    )
    legend_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="legendMode",
        description="Whether the chart legend is displayed.",
    )
    tooltip: Literal["show", "hide"] | str | None = Field(
        default=None, description="Whether chart tooltips are displayed."
    )
    tooltip_sum: Literal["on", "off"] | str | None = Field(
        default=None,
        alias="tooltipSum",
        description="Whether tooltips include a total value.",
    )
    feed: str | None = Field(default=None, description="Comment feed identifier.")
    navigator_settings: NavigatorSettings | None = Field(
        default=None, alias="navigatorSettings", description="Chart navigator settings."
    )
    stacking: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether area series are stacked."
    )


class SettingsModel107(APIModel):
    """X-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    holidays: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether holidays are highlighted on the axis."
    )
    axis_mode_map: dict[str, Literal["discrete", "continuous"] | str] | None = Field(
        default=None,
        alias="axisModeMap",
        description="Maps field GUIDs to discrete or continuous axis modes.",
    )


class SettingsModel108(APIModel):
    """Y-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    scale: Literal["auto", "manual"] | str | None = Field(
        default=None, description="Axis boundary calculation mode."
    )
    scale_value: Literal["min-max", "data-min-max", "0-max"] | str | list[Any] | None = Field(
        default=None,
        alias="scaleValue",
        description="Automatic scale mode or manual minimum and maximum values.",
    )
    nulls: Literal["ignore", "connect", "as-0", "use-previous"] | str | None = Field(
        default=None, description="How null values are displayed."
    )


class SettingsModel109(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class SettingsModel110(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )


class VisualizationModel2(APIModel):
    """Chart visualization configuration."""

    type: Literal["area"] = Field(..., description="Area visualization type.")
    chart_settings: ChartSettingsModel | None = Field(
        default=None, alias="chartSettings", description="Chart configuration."
    )
    x: X = Field(..., description="X-axis configuration.")
    y: YModel2 | None = Field(default=None, description="Y-axis configuration.")
    colors: Colors | None = Field(default=None, description="Color configuration.")
    labels: LabelsModel | None = Field(default=None, description="Data label configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")
    segments: Segments | None = Field(default=None, description="Segmentation configuration.")


class SettingsModel111(APIModel):
    """X-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    holidays: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether holidays are highlighted on the axis."
    )
    axis_mode_map: dict[str, Literal["discrete", "continuous"] | str] | None = Field(
        default=None,
        alias="axisModeMap",
        description="Maps field GUIDs to discrete or continuous axis modes.",
    )


class SettingsModel112(APIModel):
    """Y-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    scale: Literal["auto", "manual"] | str | None = Field(
        default=None, description="Axis boundary calculation mode."
    )
    scale_value: Literal["min-max", "data-min-max", "0-max"] | str | list[Any] | None = Field(
        default=None,
        alias="scaleValue",
        description="Automatic scale mode or manual minimum and maximum values.",
    )
    nulls: Literal["ignore", "connect", "as-0", "use-previous"] | str | None = Field(
        default=None, description="How null values are displayed."
    )


class SettingsModel113(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class SettingsModel114(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )


class ChartSettingsModel1(APIModel):
    """Chart configuration."""

    title: str | None = Field(default=None, description="Chart title.")
    title_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="titleMode",
        description="Whether the chart title is displayed.",
    )
    legend_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="legendMode",
        description="Whether the chart legend is displayed.",
    )
    tooltip: Literal["show", "hide"] | str | None = Field(
        default=None, description="Whether chart tooltips are displayed."
    )
    tooltip_sum: Literal["on", "off"] | str | None = Field(
        default=None,
        alias="tooltipSum",
        description="Whether tooltips include a total value.",
    )
    feed: str | None = Field(default=None, description="Comment feed identifier.")
    navigator_settings: NavigatorSettings | None = Field(
        default=None, alias="navigatorSettings", description="Chart navigator settings."
    )


class VisualizationModel3(APIModel):
    """Chart visualization configuration."""

    x: X = Field(..., description="X-axis configuration.")
    y: YModel2 | None = Field(default=None, description="Y-axis configuration.")
    colors: Colors | None = Field(default=None, description="Color configuration.")
    labels: LabelsModel | None = Field(default=None, description="Data label configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")
    segments: Segments | None = Field(default=None, description="Segmentation configuration.")
    type: Literal["area100p"] = Field(..., description="Normalized area visualization type.")
    chart_settings: ChartSettingsModel1 | None = Field(
        default=None, alias="chartSettings", description="Chart configuration."
    )


class ChartSettingsModel2(APIModel):
    """Chart configuration."""

    title: str | None = Field(default=None, description="Chart title.")
    title_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="titleMode",
        description="Whether the chart title is displayed.",
    )
    legend_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="legendMode",
        description="Whether the chart legend is displayed.",
    )
    tooltip: Literal["show", "hide"] | str | None = Field(
        default=None, description="Whether chart tooltips are displayed."
    )
    tooltip_sum: Literal["on", "off"] | str | None = Field(
        default=None,
        alias="tooltipSum",
        description="Whether tooltips include a total value.",
    )
    feed: str | None = Field(default=None, description="Comment feed identifier.")


class SettingsModel115(APIModel):
    """X-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    holidays: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether holidays are highlighted on the axis."
    )
    scale: Literal["auto", "manual"] | str | None = Field(
        default=None, description="Axis boundary calculation mode."
    )
    scale_value: Literal["min-max", "data-min-max", "0-max"] | str | list[Any] | None = Field(
        default=None,
        alias="scaleValue",
        description="Automatic scale mode or manual minimum and maximum values.",
    )
    nulls: Literal["ignore", "connect", "as-0", "use-previous"] | str | None = Field(
        default=None, description="How null values are displayed."
    )


class XModel(APIModel):
    """X-axis configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ...,
        description="Fields placed on the X-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: SettingsModel115 | None = Field(default=None, description="X-axis settings.")


class SettingsModel116(APIModel):
    """Y-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    axis_mode_map: dict[str, Literal["discrete", "continuous"] | str] | None = Field(
        default=None,
        alias="axisModeMap",
        description="Maps field GUIDs to discrete or continuous axis modes.",
    )


class YModel3(APIModel):
    """Y-axis configuration."""

    items: list[WizardFieldSchemaModel3] = Field(..., description="Fields placed on the Y-axis.")
    settings: SettingsModel116 | None = Field(default=None, description="Y-axis settings.")


class SettingsModel117(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class SettingsModel118(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )
    labels_position: Literal["outside", "inside"] | str | None = Field(
        default=None,
        alias="labelsPosition",
        description="Position of data labels relative to bars.",
    )


class LabelsModel3(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel8] | None = Field(
        default=None, description="Fields whose values are displayed as data labels."
    )
    settings: SettingsModel118 | None = Field(default=None, description="Data label settings.")


class VisualizationModel4(APIModel):
    """Chart visualization configuration."""

    type: Literal["bar"] = Field(..., description="Bar visualization type.")
    chart_settings: ChartSettingsModel2 | None = Field(
        default=None, alias="chartSettings", description="Chart configuration."
    )
    x: XModel | None = Field(default=None, description="X-axis configuration.")
    y: YModel3 = Field(..., description="Y-axis configuration.")
    colors: Colors | None = Field(default=None, description="Color configuration.")
    labels: LabelsModel3 | None = Field(default=None, description="Data label configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")


class SettingsModel119(APIModel):
    """X-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    holidays: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether holidays are highlighted on the axis."
    )
    scale: Literal["auto", "manual"] | str | None = Field(
        default=None, description="Axis boundary calculation mode."
    )
    scale_value: Literal["min-max", "data-min-max", "0-max"] | str | list[Any] | None = Field(
        default=None,
        alias="scaleValue",
        description="Automatic scale mode or manual minimum and maximum values.",
    )
    nulls: Literal["ignore", "connect", "as-0", "use-previous"] | str | None = Field(
        default=None, description="How null values are displayed."
    )


class SettingsModel120(APIModel):
    """Y-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    axis_mode_map: dict[str, Literal["discrete", "continuous"] | str] | None = Field(
        default=None,
        alias="axisModeMap",
        description="Maps field GUIDs to discrete or continuous axis modes.",
    )


class SettingsModel121(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class SettingsModel122(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )


class VisualizationModel5(APIModel):
    """Chart visualization configuration."""

    chart_settings: ChartSettingsModel2 | None = Field(
        default=None, alias="chartSettings", description="Chart configuration."
    )
    x: XModel | None = Field(default=None, description="X-axis configuration.")
    y: YModel3 = Field(..., description="Y-axis configuration.")
    colors: Colors | None = Field(default=None, description="Color configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")
    type: Literal["bar100p"] = Field(..., description="Normalized bar visualization type.")
    labels: LabelsModel | None = Field(default=None, description="Data label configuration.")


class ChartSettingsModel3(APIModel):
    """Chart configuration."""

    title: str | None = Field(default=None, description="Chart title.")
    title_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="titleMode",
        description="Whether the chart title is displayed.",
    )
    legend_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="legendMode",
        description="Whether the chart legend is displayed.",
    )
    tooltip: Literal["show", "hide"] | str | None = Field(
        default=None, description="Whether chart tooltips are displayed."
    )
    bar_gap: Literal["auto", "s", "m", "l", "none"] | str | None = Field(
        default=None, alias="barGap", description="Gap between funnel segments."
    )
    shape: Literal["auto", "rectangle", "trapezoid"] | str | None = Field(
        default=None, description="Funnel segment shape."
    )
    tooltip_percentage_base: Literal["auto", "first", "previous"] | str | None = Field(
        default=None,
        alias="tooltipPercentageBase",
        description="Base used to calculate tooltip percentages.",
    )


class Dimensions(APIModel):
    """Dimension configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ..., description="Dimensions used to create funnel stages."
    )


class MeasuresModel(APIModel):
    """Measure configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ...,
        description="Measures used to size funnel stages. Measures only: a dimension placed here needs an aggregation.",
    )


class SettingsModel123(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class ColorsModel(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ..., description="Fields used to assign stage colors."
    )
    settings: SettingsModel123 | None = Field(default=None, description="Color settings.")


class SettingsModel124(APIModel):
    """Data label settings."""

    position: Literal["outside", "inside"] | str | None = Field(
        default=None, description="Position of labels relative to funnel stages."
    )
    align: Literal["auto", "left", "center", "right"] | str | None = Field(
        default=None, description="Data label alignment."
    )
    reserve_space: Literal["auto", "on", "off"] | str | None = Field(
        default=None,
        alias="reserveSpace",
        description="Mode for reserving chart space for data labels.",
    )
    separator: Literal["auto", "space", "line-break"] | str | None = Field(
        default=None, description="Separator between label parts."
    )
    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )


class LabelsModel4(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel8] | None = Field(
        default=None, description="Fields whose values are displayed as stage labels."
    )
    settings: SettingsModel124 | None = Field(default=None, description="Data label settings.")


class VisualizationModel6(APIModel):
    """Chart visualization configuration."""

    type: Literal["funnel"] = Field(..., description="Funnel visualization type.")
    chart_settings: ChartSettingsModel3 | None = Field(
        default=None, alias="chartSettings", description="Chart configuration."
    )
    dimensions: Dimensions = Field(..., description="Dimension configuration.")
    measures: MeasuresModel = Field(..., description="Measure configuration.")
    colors: ColorsModel | None = Field(default=None, description="Color configuration.")
    labels: LabelsModel4 | None = Field(default=None, description="Data label configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")


class ChartSettingsModel4(APIModel):
    """Chart configuration."""

    title: str | None = Field(default=None, description="Chart title.")
    title_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="titleMode",
        description="Whether the chart title is displayed.",
    )
    legend_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="legendMode",
        description="Whether the chart legend is displayed.",
    )
    tooltip: Literal["show", "hide"] | str | None = Field(
        default=None, description="Whether chart tooltips are displayed."
    )
    feed: str | None = Field(default=None, description="Comment feed identifier.")


class SettingsModel125(APIModel):
    """X-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    holidays: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether holidays are highlighted on the axis."
    )
    scale: Literal["auto", "manual"] | str | None = Field(
        default=None, description="Axis boundary calculation mode."
    )
    scale_value: Literal["min-max", "data-min-max", "0-max"] | str | list[Any] | None = Field(
        default=None,
        alias="scaleValue",
        description="Automatic scale mode or manual minimum and maximum values.",
    )
    axis_mode_map: dict[str, Literal["discrete", "continuous"] | str] | None = Field(
        default=None,
        alias="axisModeMap",
        description="Maps field GUIDs to discrete or continuous axis modes.",
    )


class XModel1(APIModel):
    """X-axis configuration."""

    items: list[WizardFieldSchemaModel3] = Field(..., description="Fields placed on the X-axis.")
    settings: SettingsModel125 | None = Field(default=None, description="X-axis settings.")


class SettingsModel126(APIModel):
    """Y-axis settings."""

    title: Literal["auto", "manual", "off"] | str | None = Field(
        default=None, description="Axis title display mode."
    )
    title_value: str | None = Field(
        default=None, alias="titleValue", description="Custom axis title."
    )
    type: Literal["linear", "logarithmic"] | str | None = Field(
        default=None, description="Axis scale type."
    )
    grid: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether axis grid lines are displayed."
    )
    grid_step: Literal["auto", "manual"] | str | None = Field(
        default=None, alias="gridStep", description="Grid step calculation mode."
    )
    grid_step_value: float | None = Field(
        default=None,
        alias="gridStepValue",
        description="Manual grid-line spacing in pixels.",
    )
    hide_labels: Literal["yes", "no"] | str | None = Field(
        default=None, alias="hideLabels", description="Whether axis labels are hidden."
    )
    labels_view: Literal["auto", "horizontal", "vertical", "angle"] | str | None = Field(
        default=None, alias="labelsView", description="Axis label orientation."
    )
    axis_label_formatting: AxisLabelFormatting | None = Field(
        default=None,
        alias="axisLabelFormatting",
        description="Numeric axis label formatting.",
    )
    axis_label_date_format: str | None = Field(
        default=None,
        alias="axisLabelDateFormat",
        description="Date or datetime axis label format.",
    )
    axis_format_mode: Literal["auto", "by-field", "manual"] | str | None = Field(
        default=None, alias="axisFormatMode", description="Axis label formatting mode."
    )
    axis_visibility: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="axisVisibility",
        description="Whether the axis is displayed.",
    )
    scale: Literal["auto", "manual"] | str | None = Field(
        default=None, description="Axis boundary calculation mode."
    )
    scale_value: Literal["min-max", "data-min-max", "0-max"] | str | list[Any] | None = Field(
        default=None,
        alias="scaleValue",
        description="Automatic scale mode or manual minimum and maximum values.",
    )
    axis_mode_map: dict[str, Literal["discrete", "continuous"] | str] | None = Field(
        default=None,
        alias="axisModeMap",
        description="Maps field GUIDs to discrete or continuous axis modes.",
    )


class YModel4(APIModel):
    """Y-axis configuration."""

    items: list[WizardFieldSchemaModel3] | None = Field(
        default=None, description="Fields placed on the Y-axis."
    )
    settings: SettingsModel126 | None = Field(default=None, description="Y-axis settings.")


class PointsModel1(APIModel):
    """Point grouping configuration."""

    items: list[WizardFieldSchemaModel3] | None = Field(
        default=None,
        description="Fields used to group points and add tooltip information.",
    )


class SettingsModel127(APIModel):
    """Point size settings."""

    radius: float | None = Field(default=None, description="Default point radius in pixels.")
    min_radius: float | None = Field(
        default=None, alias="minRadius", description="Minimum point radius in pixels."
    )
    max_radius: float | None = Field(
        default=None, alias="maxRadius", description="Maximum point radius in pixels."
    )


class SizeModel(APIModel):
    """Point size configuration."""

    items: list[WizardFieldSchemaModel3] | None = Field(
        default=None,
        description="Fields used to determine point sizes. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: SettingsModel127 | None = Field(default=None, description="Point size settings.")


class SettingsModel128(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class ColorsModel1(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchemaModel3] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: SettingsModel128 | None = Field(default=None, description="Color settings.")


class SettingsModel129(APIModel):
    """Marker shape settings."""

    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used to assign shapes.",
    )
    mounted_shapes: dict[str, str] | None = Field(
        default=None,
        alias="mountedShapes",
        description="Mapping of field values to marker shapes.",
    )


class ShapesModel(APIModel):
    """Marker shape configuration."""

    items: list[WizardFieldSchemaModel3] | None = Field(
        default=None, description="Fields used for shape encoding."
    )
    settings: SettingsModel129 | None = Field(default=None, description="Marker shape settings.")


class VisualizationModel7(APIModel):
    """Chart visualization configuration."""

    type: Literal["scatter"] = Field(..., description="Scatter visualization type.")
    chart_settings: ChartSettingsModel4 | None = Field(
        default=None, alias="chartSettings", description="Chart configuration."
    )
    x: XModel1 = Field(..., description="X-axis configuration.")
    y: YModel4 | None = Field(default=None, description="Y-axis configuration.")
    points: PointsModel1 | None = Field(default=None, description="Point grouping configuration.")
    size: SizeModel | None = Field(default=None, description="Point size configuration.")
    colors: ColorsModel1 | None = Field(default=None, description="Color configuration.")
    shapes: ShapesModel | None = Field(default=None, description="Marker shape configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")


class ChartSettingsModel5(APIModel):
    """Chart configuration."""

    title: str | None = Field(default=None, description="Chart title.")
    title_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="titleMode",
        description="Whether the chart title is displayed.",
    )
    legend_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="legendMode",
        description="Whether the chart legend is displayed.",
    )
    tooltip: Literal["show", "hide"] | str | None = Field(
        default=None, description="Whether chart tooltips are displayed."
    )


class DimensionsModel(APIModel):
    """Dimension configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ..., description="Dimensions used to create pie slices."
    )


class SettingsModel130(APIModel):
    """Color settings."""

    thresholds_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="thresholdsMode",
        description="Mode used to calculate gradient thresholds.",
    )
    left_threshold: str | None = Field(
        default=None, alias="leftThreshold", description="Lower gradient threshold."
    )
    middle_threshold: str | None = Field(
        default=None, alias="middleThreshold", description="Middle gradient threshold."
    )
    right_threshold: str | None = Field(
        default=None, alias="rightThreshold", description="Upper gradient threshold."
    )
    gradient_palette: str | None = Field(
        default=None,
        alias="gradientPalette",
        description="Gradient palette identifier.",
    )
    gradient_mode: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientMode", description="Gradient type."
    )
    polygon_borders: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="polygonBorders",
        description="Whether polygon borders are displayed.",
    )
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")
    field_guid: str | None = Field(
        default=None,
        alias="fieldGuid",
        description="Identifier of the field used for coloring.",
    )
    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    colored_by_measure: bool | None = Field(
        default=None,
        alias="coloredByMeasure",
        description="Whether colors are determined by a measure.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_mode: Literal["palette", "gradient"] | str | None = Field(
        default=None, alias="colorMode", description="Color assignment mode."
    )
    null_mode: Literal["ignore", "as-0"] | str | None = Field(
        default=None, alias="nullMode", description="How null values are colored."
    )


class MeasuresModel1(APIModel):
    """Measure configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ...,
        description="Measures used to determine slice sizes. Measures only: a dimension placed here needs an aggregation.",
    )


class LabelsModel5(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel8] | None = Field(
        default=None, description="Fields whose values are displayed as slice labels."
    )


class VisualizationModel8(APIModel):
    """Chart visualization configuration."""

    type: Literal["pie"] = Field(..., description="Pie visualization type.")
    chart_settings: ChartSettingsModel5 | None = Field(
        default=None, alias="chartSettings", description="Chart configuration."
    )
    dimensions: DimensionsModel | None = Field(default=None, description="Dimension configuration.")
    colors: ColorsModel1 | None = Field(default=None, description="Color configuration.")
    measures: MeasuresModel1 = Field(..., description="Measure configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")
    labels: LabelsModel5 | None = Field(default=None, description="Data label configuration.")


class ChartSettingsModel6(APIModel):
    """Chart configuration."""

    title: str | None = Field(default=None, description="Chart title.")
    title_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="titleMode",
        description="Whether the chart title is displayed.",
    )
    legend_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="legendMode",
        description="Whether the chart legend is displayed.",
    )
    tooltip: Literal["show", "hide"] | str | None = Field(
        default=None, description="Whether chart tooltips are displayed."
    )
    totals: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether the donut center displays a total."
    )


class VisualizationModel9(APIModel):
    """Chart visualization configuration."""

    dimensions: DimensionsModel | None = Field(default=None, description="Dimension configuration.")
    colors: ColorsModel1 | None = Field(default=None, description="Color configuration.")
    measures: MeasuresModel1 = Field(..., description="Measure configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")
    labels: LabelsModel5 | None = Field(default=None, description="Data label configuration.")
    type: Literal["donut"] = Field(..., description="Donut visualization type.")
    chart_settings: ChartSettingsModel6 | None = Field(
        default=None, alias="chartSettings", description="Chart configuration."
    )


class ChartSettingsModel7(APIModel):
    """Chart configuration."""

    metric_font_color_palette: str | None = Field(
        default=None,
        alias="metricFontColorPalette",
        description="Color palette used for the metric value.",
    )
    metric_font_size: Literal["s", "m", "l", "xl"] | str | None = Field(
        default=None,
        alias="metricFontSize",
        description="Font size of the metric value.",
    )
    metric_font_color: str | None = Field(
        default=None,
        alias="metricFontColor",
        description="Custom color of the metric value.",
    )
    metric_font_color_index: float | None = Field(
        default=None,
        alias="metricFontColorIndex",
        description="Metric value color index in the palette.",
    )
    title_mode: Literal["by-field", "manual", "hide"] | str | None = Field(
        default=None, alias="titleMode", description="Metric title display mode."
    )
    title: str | None = Field(default=None, description="Metric title.")


class MeasuresModel2(APIModel):
    """Measure configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ...,
        description="Measures displayed by the metric. Measures only: a dimension placed here needs an aggregation.",
    )


class ColorsModel2(APIModel):
    """Color configuration."""

    settings: SettingsModel130 | None = Field(default=None, description="Color settings.")


class VisualizationModel10(APIModel):
    """Chart visualization configuration."""

    type: Literal["metric"] = Field(..., description="Metric visualization type.")
    is_markup: bool | None = Field(
        default=None,
        alias="isMarkup",
        description="Whether the metric value uses the markup data type.",
    )
    chart_settings: ChartSettingsModel7 | None = Field(
        default=None, alias="chartSettings", description="Chart configuration."
    )
    measures: MeasuresModel2 = Field(..., description="Measure configuration.")
    colors: ColorsModel2 | None = Field(default=None, description="Color configuration.")


class ChartSettingsModel8(APIModel):
    """Chart configuration."""

    title: str | None = Field(default=None, description="Chart title.")
    title_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="titleMode",
        description="Whether the chart title is displayed.",
    )
    tooltip: Literal["show", "hide"] | str | None = Field(
        default=None, description="Whether chart tooltips are displayed."
    )


class DimensionsModel1(APIModel):
    """Dimension configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ..., description="Dimensions used to group treemap nodes."
    )


class MeasuresModel3(APIModel):
    """Measure configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ...,
        description="Measures used to size treemap nodes. Measures only: a dimension placed here needs an aggregation.",
    )


class ColorsModel3(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ..., description="Fields used to assign node colors."
    )
    settings: SettingsModel130 | None = Field(default=None, description="Color settings.")


class VisualizationModel11(APIModel):
    """Chart visualization configuration."""

    type: Literal["treemap"] = Field(..., description="Treemap visualization type.")
    chart_settings: ChartSettingsModel8 | None = Field(
        default=None, alias="chartSettings", description="Chart configuration."
    )
    dimensions: DimensionsModel1 = Field(..., description="Dimension configuration.")
    measures: MeasuresModel3 = Field(..., description="Measure configuration.")
    colors: ColorsModel3 | None = Field(default=None, description="Color configuration.")


class ChartSettingsModel9(APIModel):
    """Chart configuration."""

    title: str | None = Field(default=None, description="Chart title.")
    title_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="titleMode",
        description="Whether the chart title is displayed.",
    )
    size: Literal["l", "m", "s"] | str | None = Field(
        default=None, description="Table row density."
    )
    pagination: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether table pagination is enabled."
    )
    limit: float | None = Field(
        default=None, description="Maximum number of rows displayed per page."
    )
    grouping: Literal["on", "disabled", "off"] | str | None = Field(
        default=None, description="Table row grouping mode."
    )
    totals: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether a total row is displayed."
    )
    pinned_columns: float | None = Field(
        default=None,
        alias="pinnedColumns",
        description="Number of columns pinned to the left side.",
    )
    preserve_white_space: bool | None = Field(
        default=None,
        alias="preserveWhiteSpace",
        description="Whether whitespace in table values is preserved.",
    )


class Columns(APIModel):
    """Column configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ..., description="Fields displayed as table columns."
    )


class ColorsModel4(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ..., description="Fields used for conditional coloring."
    )
    settings: SettingsModel130 | None = Field(default=None, description="Color settings.")


class VisualizationModel12(APIModel):
    """Chart visualization configuration."""

    type: Literal["flatTable"] = Field(..., description="Flat table visualization type.")
    chart_settings: ChartSettingsModel9 | None = Field(
        default=None, alias="chartSettings", description="Chart configuration."
    )
    columns: Columns = Field(..., description="Column configuration.")
    colors: ColorsModel4 | None = Field(default=None, description="Color configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")


class ChartSettingsModel10(APIModel):
    """Chart configuration."""

    title: str | None = Field(default=None, description="Chart title.")
    title_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="titleMode",
        description="Whether the chart title is displayed.",
    )
    size: Literal["l", "m", "s"] | str | None = Field(
        default=None, description="Table row density."
    )
    pagination: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether table pagination is enabled."
    )
    limit: float | None = Field(
        default=None, description="Maximum number of rows displayed per page."
    )
    pivot_fallback: Literal["on", "off"] | str | None = Field(
        default=None,
        alias="pivotFallback",
        description="Whether to use the legacy pivot-table renderer.",
    )
    pivot_inline_sort: Literal["on", "off"] | str | None = Field(
        default=None,
        alias="pivotInlineSort",
        description="Whether sorting the pivot table by rows is enabled.",
    )
    pinned_columns: float | None = Field(
        default=None,
        alias="pinnedColumns",
        description="Number of columns pinned to the left side.",
    )
    preserve_white_space: bool | None = Field(
        default=None,
        alias="preserveWhiteSpace",
        description="Whether whitespace in table values is preserved.",
    )


class ColumnsModel(APIModel):
    """Column configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ..., description="Dimensions displayed as pivot columns."
    )


class Rows(APIModel):
    """Row configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ..., description="Dimensions displayed as pivot rows."
    )


class MeasuresModel4(APIModel):
    """Measure configuration."""

    items: list[WizardFieldSchemaModel3] = Field(
        ...,
        description="Measures displayed in pivot cells. Measures only: a dimension placed here needs an aggregation.",
    )


class VisualizationModel13(APIModel):
    """Chart visualization configuration."""

    type: Literal["pivotTable"] = Field(..., description="Pivot table visualization type.")
    chart_settings: ChartSettingsModel10 | None = Field(
        default=None, alias="chartSettings", description="Chart configuration."
    )
    columns: ColumnsModel = Field(..., description="Column configuration.")
    rows: Rows = Field(..., description="Row configuration.")
    measures: MeasuresModel4 = Field(..., description="Measure configuration.")
    colors: ColorsModel4 | None = Field(default=None, description="Color configuration.")
    sort: Sort | None = Field(default=None, description="Sorting configuration.")


class ChartSettingsModel11(APIModel):
    """Map configuration."""

    title: str | None = Field(default=None, description="Chart title.")
    title_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="titleMode",
        description="Whether the chart title is displayed.",
    )
    legend_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="legendMode",
        description="Whether the map legend is displayed.",
    )
    map_center_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="mapCenterMode",
        description="Mode used to determine the initial map center.",
    )
    map_center_value: str | None = Field(
        default=None,
        alias="mapCenterValue",
        description='Map center in "latitude,longitude" format.',
    )
    zoom_mode: Literal["auto", "manual"] | str | None = Field(
        default=None,
        alias="zoomMode",
        description="Mode used to determine the initial map zoom.",
    )
    zoom_value: float | None = Field(
        default=None,
        alias="zoomValue",
        description="Initial map zoom level from 1 to 21.",
    )


class VisualizationModel14(APIModel):
    """Chart visualization configuration."""

    type: Literal["geolayer"] = Field(..., description="Geolayer visualization type.")
    chart_settings: ChartSettingsModel11 | None = Field(
        default=None, alias="chartSettings", description="Map configuration."
    )
    layers: list[WizardV1GeolayerLayerSchemaModel4] = Field(
        ..., description="Layers included in the map."
    )
    selected_layer_id: str | None = Field(
        default=None,
        alias="selectedLayerId",
        description="Identifier of the currently selected layer.",
    )


class ChartSettingsModel12(APIModel):
    """Chart configuration."""

    title: str | None = Field(default=None, description="Chart title.")
    title_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="titleMode",
        description="Whether the chart title is displayed.",
    )
    legend_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="legendMode",
        description="Whether the chart legend is displayed.",
    )
    tooltip: Literal["show", "hide"] | str | None = Field(
        default=None, description="Whether chart tooltips are displayed."
    )
    feed: str | None = Field(default=None, description="Comment feed identifier.")


class VisualizationModel15(APIModel):
    """Chart visualization configuration."""

    type: Literal["combined-chart"] = Field(..., description="Combined chart visualization type.")
    chart_settings: ChartSettingsModel12 | None = Field(
        default=None, alias="chartSettings", description="Chart configuration."
    )
    layers: list[WizardV1CombinedChartLayerSchemaModel2] = Field(
        ..., description="Layers included in the combined chart."
    )
    selected_layer_id: str | None = Field(
        default=None,
        alias="selectedLayerId",
        description="Identifier of the currently selected layer.",
    )


class WizardV1ConfigSchema(APIModel):
    sources: Sources = Field(
        ...,
        description="Data sources, chart-local field updates, dataset links, hierarchies, and filters used by the chart.",
    )
    visualization: (
        Visualization
        | VisualizationModel
        | VisualizationModel1
        | VisualizationModel2
        | VisualizationModel3
        | VisualizationModel4
        | VisualizationModel5
        | VisualizationModel6
        | VisualizationModel7
        | VisualizationModel8
        | VisualizationModel9
        | VisualizationModel10
        | VisualizationModel11
        | VisualizationModel12
        | VisualizationModel13
        | VisualizationModel14
        | VisualizationModel15
    ) = Field(..., description="Chart visualization configuration.")


class Annotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class WizardV1(APIModel):
    version: Literal[1] = Field(..., description="Entry API version.")
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    key: str | None = Field(..., description="Key identifier of the entry.")
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp.")
    created_by: str = Field(..., alias="createdBy", description="Creator of the entry.")
    updated_at: str = Field(..., alias="updatedAt", description="Last update timestamp.")
    updated_by: str = Field(..., alias="updatedBy", description="Last updater of the entry.")
    rev_id: str = Field(..., alias="revId", description="Version ID for the Wizard chart.")
    saved_id: str = Field(..., alias="savedId", description="Saved version ID.")
    published_id: str | None = Field(..., alias="publishedId", description="Published version ID.")
    tenant_id: str = Field(..., alias="tenantId", description="Tenant ID.")
    hidden: bool = Field(..., description="Indicates if the entry is hidden.")
    public: bool = Field(..., description="Indicates if the entry is public.")
    workbook_id: str | None = Field(
        ...,
        alias="workbookId",
        description="ID of the workbook the Wizard chart belongs to.",
    )
    scope: Literal["widget"] = Field(
        ..., description="Type of the entry. For charts takes value: widget"
    )
    type: (
        Literal[
            "graph_wizard_node",
            "table_wizard_node",
            "ymap_wizard_node",
            "metric_wizard_node",
            "markup_wizard_node",
            "timeseries_wizard_node",
            "d3_wizard_node",
        ]
        | str
        | None
    ) = None
    meta: dict[str, Any] | None = Field(..., description="Metadata associated with the entry.")
    links: dict[str, Any] | None = Field(default=None, description="Link information.")
    annotation: Annotation | None = Field(default=None, description="Annotation information.")
    data: WizardV1ConfigSchema


class Permissions(APIModel):
    """Permissions for the chart."""

    execute: bool = Field(..., description="Indicates if there are permissions to execute.")
    read: bool = Field(..., description="Indicates if there are permissions to read.")
    edit: bool = Field(..., description="Indicates if there are permissions to edit.")
    admin: bool = Field(..., description="Indicates if there are permissions for admin.")


class GetWizardChartV1Result(APIModel):
    entry: WizardV1
    is_favorite: bool | None = Field(
        default=None,
        alias="isFavorite",
        description="Indicates if the chart is marked as favorite.",
    )
    permissions: Permissions | None = Field(default=None, description="Permissions for the chart.")


class GetWizardChartV1Args(RequestBody):
    chart_id: str = Field(..., alias="chartId", description="ID of the Wizard chart to return.")
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook the Wizard chart belongs to.",
    )
    rev_id: str | None = Field(
        default=None, alias="revId", description="Version ID for the Wizard chart."
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


class DeleteWizardChartArgs(RequestBody):
    chart_id: str = Field(..., alias="chartId")


class UpdateWizardV1Result(APIModel):
    entry: WizardV1


class UpdateWizardV1Args(RequestBody):
    chart_id: str = Field(..., alias="chartId")
    annotation: shared.EntryAnnotationArg | None = None
    mode: shared.EntryUpdateMode
    rev_id: str | None = Field(default=None, alias="revId")
    data: WizardV1ConfigSchema


class CreateWizardChartV1Result(APIModel):
    entry: WizardV1


class CreateWizardChartV1Args(EntryLocationIdentifiers):
    data: WizardV1ConfigSchema
    annotation: shared.EntryAnnotationArg | None = None


class DeleteWizardChartResponse(APIModel):
    pass
