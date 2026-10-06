# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody

from . import shared
from .shared import EntryLocationIdentifiers, OtherKind


class WizardV1LineShapeSettingsSchema(APIModel):
    line_width: int | float | Literal["auto"] | None = Field(
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


class WizardLabelsItemSchema(APIModel):
    label_percentage_base: Literal["auto", "first", "previous"] | str | None = Field(
        default=None,
        alias="labelPercentageBase",
        description="Base used to calculate percentage labels.",
    )


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
    direction: Literal["ASC", "DESC"] | str | None = Field(
        default=None, description="Sort direction."
    )


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


class OtherKindByTitle(APIModel):
    """A kind the specification does not describe: kept as it came."""

    title: str | None = Field(default=None, description="The kind.")


class OtherKindByColorType(APIModel):
    """A kind the specification does not describe: kept as it came."""

    color_type: str | None = Field(default=None, alias="colorType", description="The kind.")


class OtherKindByMode(APIModel):
    """A kind the specification does not describe: kept as it came."""

    mode: str | None = Field(default=None, description="The kind.")


class DeleteWizardChartResponse(APIModel):
    pass


class WizardV1FiltersItemSchemaFilterOperation(APIModel):
    """Operation used to compare field values."""

    code: str | None = Field(default=None, description="Filter operation code.")


class WizardFieldSchemaVariant1Formatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardFieldSchemaVariant1BarsSettingsColorSettingsVariant1SettingsThresholdsVariant1(
    APIModel
):
    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class WizardFieldSchemaVariant1BarsSettingsColorSettingsVariant1SettingsThresholdsVariant2(
    APIModel
):
    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str | None = Field(default=None, description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str | None = Field(default=None, description="Upper gradient threshold.")


class WizardFieldSchemaVariant1BarsSettingsColorSettingsVariant2Settings(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: int | float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class WizardFieldSchemaVariant1BarsSettingsColorSettingsVariant3Settings(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: int | float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: int | float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class WizardFieldSchemaVariant1BarsSettingsScaleVariant1(APIModel):
    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class WizardFieldSchemaVariant1BarsSettingsScaleVariant2Settings(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class WizardFieldSchemaVariant1SubTotalsSettings(APIModel):
    """Subtotal settings."""

    enabled: bool | None = Field(
        default=None, description="Whether to display subtotals for the field."
    )


class WizardFieldSchemaVariant1BackgroundSettingsSettingsPaletteState(APIModel):
    """Discrete palette settings."""

    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")


class WizardFieldSchemaVariant1BackgroundSettingsSettingsGradientState(APIModel):
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


class WizardFieldSchemaVariant1ColumnSettingsWidthVariant1(APIModel):
    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WizardFieldSchemaVariant1ColumnSettingsWidthVariant2(APIModel):
    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str | None = Field(default=None, description="Column width percentage.")


class WizardFieldSchemaVariant1ColumnSettingsWidthVariant3(APIModel):
    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str | None = Field(default=None, description="Column width in pixels.")


class WizardFieldSchemaVariant1HintSettings(APIModel):
    """Field hint settings."""

    enabled: bool | None = Field(default=None, description="Whether the field hint is enabled.")
    text: str | None = Field(default=None, description="Hint text displayed for the field.")


class WizardFieldSchemaVariant1FieldsItemFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardFieldSchemaVariant1FieldsItemBarsSettingsColorSettingsVariant1SettingsThresholdsVariant1(
    APIModel
):
    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class WizardFieldSchemaVariant1FieldsItemBarsSettingsColorSettingsVariant1SettingsThresholdsVariant2(
    APIModel
):
    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str | None = Field(default=None, description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str | None = Field(default=None, description="Upper gradient threshold.")


class WizardFieldSchemaVariant1FieldsItemBarsSettingsColorSettingsVariant2Settings(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: int | float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class WizardFieldSchemaVariant1FieldsItemBarsSettingsColorSettingsVariant3Settings(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: int | float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: int | float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class WizardFieldSchemaVariant1FieldsItemBarsSettingsScaleVariant1(APIModel):
    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class WizardFieldSchemaVariant1FieldsItemBarsSettingsScaleVariant2Settings(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class WizardFieldSchemaVariant1FieldsItemSubTotalsSettings(APIModel):
    """Subtotal settings."""

    enabled: bool | None = Field(
        default=None, description="Whether to display subtotals for the field."
    )


class WizardFieldSchemaVariant1FieldsItemBackgroundSettingsSettingsPaletteState(APIModel):
    """Discrete palette settings."""

    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")


class WizardFieldSchemaVariant1FieldsItemBackgroundSettingsSettingsGradientState(APIModel):
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


class WizardFieldSchemaVariant1FieldsItemColumnSettingsWidthVariant1(APIModel):
    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WizardFieldSchemaVariant1FieldsItemColumnSettingsWidthVariant2(APIModel):
    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str | None = Field(default=None, description="Column width percentage.")


class WizardFieldSchemaVariant1FieldsItemColumnSettingsWidthVariant3(APIModel):
    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str | None = Field(default=None, description="Column width in pixels.")


class WizardFieldSchemaVariant1FieldsItemHintSettings(APIModel):
    """Field hint settings."""

    enabled: bool | None = Field(default=None, description="Whether the field hint is enabled.")
    text: str | None = Field(default=None, description="Hint text displayed for the field.")


class WizardFieldSchemaVariant2Formatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardFieldSchemaVariant2BarsSettingsColorSettingsVariant1SettingsThresholdsVariant1(
    APIModel
):
    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class WizardFieldSchemaVariant2BarsSettingsColorSettingsVariant1SettingsThresholdsVariant2(
    APIModel
):
    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str | None = Field(default=None, description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str | None = Field(default=None, description="Upper gradient threshold.")


class WizardFieldSchemaVariant2BarsSettingsColorSettingsVariant2Settings(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: int | float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class WizardFieldSchemaVariant2BarsSettingsColorSettingsVariant3Settings(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: int | float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: int | float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class WizardFieldSchemaVariant2BarsSettingsScaleVariant1(APIModel):
    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class WizardFieldSchemaVariant2BarsSettingsScaleVariant2Settings(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class WizardFieldSchemaVariant2SubTotalsSettings(APIModel):
    """Subtotal settings."""

    enabled: bool | None = Field(
        default=None, description="Whether to display subtotals for the field."
    )


class WizardFieldSchemaVariant2BackgroundSettingsSettingsPaletteState(APIModel):
    """Discrete palette settings."""

    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")


class WizardFieldSchemaVariant2BackgroundSettingsSettingsGradientState(APIModel):
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


class WizardFieldSchemaVariant2ColumnSettingsWidthVariant1(APIModel):
    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WizardFieldSchemaVariant2ColumnSettingsWidthVariant2(APIModel):
    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str | None = Field(default=None, description="Column width percentage.")


class WizardFieldSchemaVariant2ColumnSettingsWidthVariant3(APIModel):
    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str | None = Field(default=None, description="Column width in pixels.")


class WizardFieldSchemaVariant2HintSettings(APIModel):
    """Field hint settings."""

    enabled: bool | None = Field(default=None, description="Whether the field hint is enabled.")
    text: str | None = Field(default=None, description="Hint text displayed for the field.")


class WizardFieldSchemaVariant3Formatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardFieldSchemaVariant3BarsSettingsColorSettingsVariant1SettingsThresholdsVariant1(
    APIModel
):
    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class WizardFieldSchemaVariant3BarsSettingsColorSettingsVariant1SettingsThresholdsVariant2(
    APIModel
):
    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str | None = Field(default=None, description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str | None = Field(default=None, description="Upper gradient threshold.")


class WizardFieldSchemaVariant3BarsSettingsColorSettingsVariant2Settings(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: int | float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class WizardFieldSchemaVariant3BarsSettingsColorSettingsVariant3Settings(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: int | float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: int | float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class WizardFieldSchemaVariant3BarsSettingsScaleVariant1(APIModel):
    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class WizardFieldSchemaVariant3BarsSettingsScaleVariant2Settings(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class WizardFieldSchemaVariant3SubTotalsSettings(APIModel):
    """Subtotal settings."""

    enabled: bool | None = Field(
        default=None, description="Whether to display subtotals for the field."
    )


class WizardFieldSchemaVariant3BackgroundSettingsSettingsPaletteState(APIModel):
    """Discrete palette settings."""

    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")


class WizardFieldSchemaVariant3BackgroundSettingsSettingsGradientState(APIModel):
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


class WizardFieldSchemaVariant3ColumnSettingsWidthVariant1(APIModel):
    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WizardFieldSchemaVariant3ColumnSettingsWidthVariant2(APIModel):
    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str | None = Field(default=None, description="Column width percentage.")


class WizardFieldSchemaVariant3ColumnSettingsWidthVariant3(APIModel):
    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str | None = Field(default=None, description="Column width in pixels.")


class WizardFieldSchemaVariant3HintSettings(APIModel):
    """Field hint settings."""

    enabled: bool | None = Field(default=None, description="Whether the field hint is enabled.")
    text: str | None = Field(default=None, description="Hint text displayed for the field.")


class WizardFieldSchemaVariant4Formatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardFieldSchemaVariant4BarsSettingsColorSettingsVariant1SettingsThresholdsVariant1(
    APIModel
):
    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class WizardFieldSchemaVariant4BarsSettingsColorSettingsVariant1SettingsThresholdsVariant2(
    APIModel
):
    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str | None = Field(default=None, description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str | None = Field(default=None, description="Upper gradient threshold.")


class WizardFieldSchemaVariant4BarsSettingsColorSettingsVariant2Settings(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: int | float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class WizardFieldSchemaVariant4BarsSettingsColorSettingsVariant3Settings(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: int | float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: int | float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class WizardFieldSchemaVariant4BarsSettingsScaleVariant1(APIModel):
    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class WizardFieldSchemaVariant4BarsSettingsScaleVariant2Settings(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class WizardFieldSchemaVariant4SubTotalsSettings(APIModel):
    """Subtotal settings."""

    enabled: bool | None = Field(
        default=None, description="Whether to display subtotals for the field."
    )


class WizardFieldSchemaVariant4BackgroundSettingsSettingsPaletteState(APIModel):
    """Discrete palette settings."""

    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")


class WizardFieldSchemaVariant4BackgroundSettingsSettingsGradientState(APIModel):
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


class WizardFieldSchemaVariant4ColumnSettingsWidthVariant1(APIModel):
    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WizardFieldSchemaVariant4ColumnSettingsWidthVariant2(APIModel):
    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str | None = Field(default=None, description="Column width percentage.")


class WizardFieldSchemaVariant4ColumnSettingsWidthVariant3(APIModel):
    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str | None = Field(default=None, description="Column width in pixels.")


class WizardFieldSchemaVariant4HintSettings(APIModel):
    """Field hint settings."""

    enabled: bool | None = Field(default=None, description="Whether the field hint is enabled.")
    text: str | None = Field(default=None, description="Hint text displayed for the field.")


class WizardPseudoFieldSchemaVariant1Formatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardPseudoFieldSchemaVariant1BarsSettingsColorSettingsVariant1SettingsThresholdsVariant1(
    APIModel
):
    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class WizardPseudoFieldSchemaVariant1BarsSettingsColorSettingsVariant1SettingsThresholdsVariant2(
    APIModel
):
    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str | None = Field(default=None, description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str | None = Field(default=None, description="Upper gradient threshold.")


class WizardPseudoFieldSchemaVariant1BarsSettingsColorSettingsVariant2Settings(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: int | float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class WizardPseudoFieldSchemaVariant1BarsSettingsColorSettingsVariant3Settings(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: int | float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: int | float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class WizardPseudoFieldSchemaVariant1BarsSettingsScaleVariant1(APIModel):
    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class WizardPseudoFieldSchemaVariant1BarsSettingsScaleVariant2Settings(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class WizardPseudoFieldSchemaVariant1SubTotalsSettings(APIModel):
    """Subtotal settings."""

    enabled: bool | None = Field(
        default=None, description="Whether to display subtotals for the field."
    )


class WizardPseudoFieldSchemaVariant1BackgroundSettingsSettingsPaletteState(APIModel):
    """Discrete palette settings."""

    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")


class WizardPseudoFieldSchemaVariant1BackgroundSettingsSettingsGradientState(APIModel):
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


class WizardPseudoFieldSchemaVariant1ColumnSettingsWidthVariant1(APIModel):
    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WizardPseudoFieldSchemaVariant1ColumnSettingsWidthVariant2(APIModel):
    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str | None = Field(default=None, description="Column width percentage.")


class WizardPseudoFieldSchemaVariant1ColumnSettingsWidthVariant3(APIModel):
    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str | None = Field(default=None, description="Column width in pixels.")


class WizardPseudoFieldSchemaVariant1HintSettings(APIModel):
    """Field hint settings."""

    enabled: bool | None = Field(default=None, description="Whether the field hint is enabled.")
    text: str | None = Field(default=None, description="Hint text displayed for the field.")


class WizardPseudoFieldSchemaVariant2Formatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardPseudoFieldSchemaVariant2BarsSettingsColorSettingsVariant1SettingsThresholdsVariant1(
    APIModel
):
    mode: Literal["auto"] = Field(..., description="Calculate gradient thresholds automatically.")


class WizardPseudoFieldSchemaVariant2BarsSettingsColorSettingsVariant1SettingsThresholdsVariant2(
    APIModel
):
    mode: Literal["manual"] = Field(..., description="Use manually specified gradient thresholds.")
    min: str | None = Field(default=None, description="Lower gradient threshold.")
    mid: str | None = Field(default=None, description="Middle gradient threshold.")
    max: str | None = Field(default=None, description="Upper gradient threshold.")


class WizardPseudoFieldSchemaVariant2BarsSettingsColorSettingsVariant2Settings(APIModel):
    """Single-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    color_index: int | float | None = Field(
        default=None,
        alias="colorIndex",
        description="Selected color index in the palette.",
    )
    color: str | None = Field(default=None, description="Custom bar color.")


class WizardPseudoFieldSchemaVariant2BarsSettingsColorSettingsVariant3Settings(APIModel):
    """Two-color bar settings."""

    palette: str | None = Field(default=None, description="Color palette identifier.")
    negative_color_index: int | float | None = Field(
        default=None,
        alias="negativeColorIndex",
        description="Palette color index for negative values.",
    )
    negative_color: str | None = Field(
        default=None,
        alias="negativeColor",
        description="Custom color for negative values.",
    )
    positive_color_index: int | float | None = Field(
        default=None,
        alias="positiveColorIndex",
        description="Palette color index for positive values.",
    )
    positive_color: str | None = Field(
        default=None,
        alias="positiveColor",
        description="Custom color for positive values.",
    )


class WizardPseudoFieldSchemaVariant2BarsSettingsScaleVariant1(APIModel):
    mode: Literal["auto"] = Field(..., description="Calculate the bar scale automatically.")


class WizardPseudoFieldSchemaVariant2BarsSettingsScaleVariant2Settings(APIModel):
    """Manual bar scale boundaries."""

    min: str | None = Field(default=None, description="Manual minimum scale value.")
    max: str | None = Field(default=None, description="Manual maximum scale value.")


class WizardPseudoFieldSchemaVariant2SubTotalsSettings(APIModel):
    """Subtotal settings."""

    enabled: bool | None = Field(
        default=None, description="Whether to display subtotals for the field."
    )


class WizardPseudoFieldSchemaVariant2BackgroundSettingsSettingsPaletteState(APIModel):
    """Discrete palette settings."""

    mounted_colors: dict[str, str] | None = Field(
        default=None,
        alias="mountedColors",
        description="Mapping of field values to colors.",
    )
    palette: str | None = Field(default=None, description="Color palette identifier.")


class WizardPseudoFieldSchemaVariant2BackgroundSettingsSettingsGradientState(APIModel):
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


class WizardPseudoFieldSchemaVariant2ColumnSettingsWidthVariant1(APIModel):
    mode: Literal["auto"] = Field(..., description="Calculate the column width automatically.")


class WizardPseudoFieldSchemaVariant2ColumnSettingsWidthVariant2(APIModel):
    mode: Literal["percent"] = Field(..., description="Set the column width as a percentage.")
    value: str | None = Field(default=None, description="Column width percentage.")


class WizardPseudoFieldSchemaVariant2ColumnSettingsWidthVariant3(APIModel):
    mode: Literal["pixel"] = Field(..., description="Set the column width in pixels.")
    value: str | None = Field(default=None, description="Column width in pixels.")


class WizardPseudoFieldSchemaVariant2HintSettings(APIModel):
    """Field hint settings."""

    enabled: bool | None = Field(default=None, description="Whether the field hint is enabled.")
    text: str | None = Field(default=None, description="Hint text displayed for the field.")


class WizardSortItemSchemaVariant1(APIModel):
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    direction: Literal["ASC", "DESC"] | str | None = Field(
        default=None, description="Sort direction."
    )
    guid: str | None = Field(default=None, description="Identifier of the field used for sorting.")
    dataset_id: str | None = Field(
        default=None,
        alias="datasetId",
        description="Identifier of the dataset containing the field.",
    )


class WizardV1GeolayerLayerSchemaVariant1LayerSettings(APIModel):
    """Geographic layer configuration."""

    id: str | None = Field(default=None, description="Unique layer identifier.")
    name: str | None = Field(default=None, description="Layer display name.")
    alpha: int | float | None = Field(
        default=None, description="Layer opacity as a percentage from 0 to 100."
    )


class WizardV1GeolayerLayerSchemaVariant1SizeSettings(APIModel):
    """Map point size settings."""

    radius: int | float | None = Field(default=None, description="Radius of map points in pixels.")


class WizardV1GeolayerLayerSchemaVariant1ColorsSettings(APIModel):
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


class WizardV1GeolayerLayerSchemaVariant1TooltipSettings(APIModel):
    """Tooltip display settings."""

    color: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether to display series colors in the tooltip."
    )
    field_title: Literal["on", "off"] | str | None = Field(
        default=None,
        alias="fieldTitle",
        description="Whether to display field titles in the tooltip.",
    )


class WizardV1GeolayerLayerSchemaVariant2LayerSettings(APIModel):
    """Geographic layer configuration."""

    id: str | None = Field(default=None, description="Unique layer identifier.")
    name: str | None = Field(default=None, description="Layer display name.")
    alpha: int | float | None = Field(
        default=None, description="Layer opacity as a percentage from 0 to 100."
    )


class WizardV1GeolayerLayerSchemaVariant2SizeSettings(APIModel):
    """Map point size settings."""

    radius: int | float | None = Field(default=None, description="Radius of map points in pixels.")


class WizardV1GeolayerLayerSchemaVariant2ColorsSettings(APIModel):
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


class WizardV1GeolayerLayerSchemaVariant2TooltipSettings(APIModel):
    """Tooltip display settings."""

    color: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether to display series colors in the tooltip."
    )
    field_title: Literal["on", "off"] | str | None = Field(
        default=None,
        alias="fieldTitle",
        description="Whether to display field titles in the tooltip.",
    )


class WizardV1GeolayerLayerSchemaVariant3LayerSettings(APIModel):
    """Geographic layer configuration."""

    id: str | None = Field(default=None, description="Unique layer identifier.")
    name: str | None = Field(default=None, description="Layer display name.")
    alpha: int | float | None = Field(
        default=None, description="Layer opacity as a percentage from 0 to 100."
    )


class WizardV1GeolayerLayerSchemaVariant3PolylinesSettings(APIModel):
    """Polyline display settings."""

    polyline_points: Literal["on", "off"] | str | None = Field(
        default=None,
        alias="polylinePoints",
        description="Whether vertices are displayed on polylines.",
    )


class WizardV1GeolayerLayerSchemaVariant3ColorsSettings(APIModel):
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


class WizardV1GeolayerLayerSchemaVariant4LayerSettings(APIModel):
    """Geographic layer configuration."""

    id: str | None = Field(default=None, description="Unique layer identifier.")
    name: str | None = Field(default=None, description="Layer display name.")
    alpha: int | float | None = Field(
        default=None, description="Layer opacity as a percentage from 0 to 100."
    )


class WizardV1GeolayerLayerSchemaVariant4ColorsSettings(APIModel):
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


class WizardV1GeolayerLayerSchemaVariant4TooltipSettings(APIModel):
    """Tooltip display settings."""

    color: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether to display series colors in the tooltip."
    )
    field_title: Literal["on", "off"] | str | None = Field(
        default=None,
        alias="fieldTitle",
        description="Whether to display field titles in the tooltip.",
    )


class WizardV1GeolayerLayerSchemaVariant5LayerSettings(APIModel):
    """Geographic layer configuration."""

    id: str | None = Field(default=None, description="Unique layer identifier.")
    name: str | None = Field(default=None, description="Layer display name.")
    alpha: int | float | None = Field(
        default=None, description="Layer opacity as a percentage from 0 to 100."
    )


class WizardV1GeolayerLayerSchemaVariant5ColorsSettings(APIModel):
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


class WizardV1CombinedChartLayerSchemaVariant1LayerSettings(APIModel):
    """Layer configuration."""

    id: str | None = Field(default=None, description="Unique layer identifier.")
    name: str | None = Field(default=None, description="Layer display name.")


class WizardV1CombinedChartLayerSchemaVariant1XSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1CombinedChartLayerSchemaVariant1YSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1CombinedChartLayerSchemaVariant1Y2SettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1CombinedChartLayerSchemaVariant1ColorsSettings(APIModel):
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


class WizardV1CombinedChartLayerSchemaVariant1ShapesSettingsCommonLineSettings(APIModel):
    """Line shape settings shared by all series."""

    line_width: int | float | Literal["auto"] | None = Field(
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


class WizardV1CombinedChartLayerSchemaVariant1LabelsSettings(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )


class WizardV1CombinedChartLayerSchemaVariant2LayerSettings(APIModel):
    """Layer configuration."""

    id: str | None = Field(default=None, description="Unique layer identifier.")
    name: str | None = Field(default=None, description="Layer display name.")


class WizardV1CombinedChartLayerSchemaVariant2XSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1CombinedChartLayerSchemaVariant2YSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1CombinedChartLayerSchemaVariant2ColorsSettings(APIModel):
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


class WizardV1CombinedChartLayerSchemaVariant2LabelsSettings(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )
    labels_position: Literal["outside", "inside"] | str | None = Field(
        default=None,
        alias="labelsPosition",
        description="Position of data labels relative to columns.",
    )


class WizardV1CombinedChartLayerSchemaVariant3LayerSettings(APIModel):
    """Layer configuration."""

    id: str | None = Field(default=None, description="Unique layer identifier.")
    name: str | None = Field(default=None, description="Layer display name.")


class WizardV1CombinedChartLayerSchemaVariant3XSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1CombinedChartLayerSchemaVariant3YSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1CombinedChartLayerSchemaVariant3ColorsSettings(APIModel):
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


class WizardV1CombinedChartLayerSchemaVariant3LabelsSettings(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )


class WizardV1ConfigSchemaSourcesUpdatesItemField(APIModel):
    """Field properties changed by the operation."""

    guid: str | None = Field(default=None, description="Unique field identifier.")
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
    default_value: str | int | float | bool | None = Field(
        default=None, description="Value of a parameter added in the chart."
    )


class WizardV1ConfigSchemaSourcesLinksItemFieldsValueField(APIModel):
    """Field participating in the dataset link."""

    title: str | None = Field(default=None, description="Linked field title.")
    guid: str | None = Field(default=None, description="Linked field identifier.")


class WizardV1ConfigSchemaSourcesLinksItemFieldsValueDataset(APIModel):
    """Dataset containing the linked field."""

    id: str | None = Field(default=None, description="Linked dataset identifier.")
    real_name: str | None = Field(
        default=None, alias="realName", description="Linked dataset display name."
    )


class WizardV1ConfigSchemaSourcesHierarchiesItemFieldsItem(APIModel):
    guid: str | None = Field(default=None, description="Identifier of a field in the hierarchy.")
    dataset_id: str | None = Field(
        default=None,
        alias="datasetId",
        description="Identifier of the dataset containing the field.",
    )


class WizardV1ConfigSchemaVisualizationVariant1ChartSettingsNavigatorSettingsPeriodSettings(
    APIModel
):
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
        | None
    ) = Field(default=None, description="Data type of the navigator axis field.")
    value: str | None = Field(default=None, description="Initial navigator window size.")
    period: Literal["month", "year", "day", "hour", "week", "quarter"] | str | None = Field(
        default=None, description="Unit of the navigator window size."
    )


class WizardV1ConfigSchemaVisualizationVariant1XSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant1YSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant1Y2SettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant1ColorsSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant1ShapesSettingsCommonLineSettings(APIModel):
    """Line shape settings shared by all series."""

    line_width: int | float | Literal["auto"] | None = Field(
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


class WizardV1ConfigSchemaVisualizationVariant1LabelsSettings(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )


class WizardV1ConfigSchemaVisualizationVariant2ChartSettingsNavigatorSettingsPeriodSettings(
    APIModel
):
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
        | None
    ) = Field(default=None, description="Data type of the navigator axis field.")
    value: str | None = Field(default=None, description="Initial navigator window size.")
    period: Literal["month", "year", "day", "hour", "week", "quarter"] | str | None = Field(
        default=None, description="Unit of the navigator window size."
    )


class WizardV1ConfigSchemaVisualizationVariant2XSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant2YSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant2ColorsSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant2LabelsSettings(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )
    labels_position: Literal["outside", "inside"] | str | None = Field(
        default=None,
        alias="labelsPosition",
        description="Position of data labels relative to columns.",
    )


class WizardV1ConfigSchemaVisualizationVariant3ChartSettingsNavigatorSettingsPeriodSettings(
    APIModel
):
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
        | None
    ) = Field(default=None, description="Data type of the navigator axis field.")
    value: str | None = Field(default=None, description="Initial navigator window size.")
    period: Literal["month", "year", "day", "hour", "week", "quarter"] | str | None = Field(
        default=None, description="Unit of the navigator window size."
    )


class WizardV1ConfigSchemaVisualizationVariant3XSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant3YSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant3ColorsSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant3LabelsSettings(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )


class WizardV1ConfigSchemaVisualizationVariant4ChartSettingsNavigatorSettingsPeriodSettings(
    APIModel
):
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
        | None
    ) = Field(default=None, description="Data type of the navigator axis field.")
    value: str | None = Field(default=None, description="Initial navigator window size.")
    period: Literal["month", "year", "day", "hour", "week", "quarter"] | str | None = Field(
        default=None, description="Unit of the navigator window size."
    )


class WizardV1ConfigSchemaVisualizationVariant4XSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant4YSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant4ColorsSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant4LabelsSettings(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )


class WizardV1ConfigSchemaVisualizationVariant5XSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant5YSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant5ColorsSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant5LabelsSettings(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )


class WizardV1ConfigSchemaVisualizationVariant5ChartSettingsNavigatorSettingsPeriodSettings(
    APIModel
):
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
        | None
    ) = Field(default=None, description="Data type of the navigator axis field.")
    value: str | None = Field(default=None, description="Initial navigator window size.")
    period: Literal["month", "year", "day", "hour", "week", "quarter"] | str | None = Field(
        default=None, description="Unit of the navigator window size."
    )


class WizardV1ConfigSchemaVisualizationVariant6ChartSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant6XSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant6YSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant6ColorsSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant6LabelsSettings(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )
    labels_position: Literal["outside", "inside"] | str | None = Field(
        default=None,
        alias="labelsPosition",
        description="Position of data labels relative to bars.",
    )


class WizardV1ConfigSchemaVisualizationVariant7ChartSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant7XSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant7YSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant7ColorsSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant7LabelsSettings(APIModel):
    """Data label settings."""

    overlap: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether data labels may overlap."
    )


class WizardV1ConfigSchemaVisualizationVariant8ChartSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant8ColorsSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant8LabelsSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant9ChartSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant9XSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant9YSettingsAxisLabelFormatting(APIModel):
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
    precision: int | float | None = Field(
        default=None, description="Number of decimal places to display."
    )
    label_mode: Literal["absolute", "percent"] | str | None = Field(
        default=None,
        alias="labelMode",
        description="How the formatted label is displayed.",
    )


class WizardV1ConfigSchemaVisualizationVariant9SizeSettings(APIModel):
    """Point size settings."""

    radius: int | float | None = Field(default=None, description="Default point radius in pixels.")
    min_radius: int | float | None = Field(
        default=None, alias="minRadius", description="Minimum point radius in pixels."
    )
    max_radius: int | float | None = Field(
        default=None, alias="maxRadius", description="Maximum point radius in pixels."
    )


class WizardV1ConfigSchemaVisualizationVariant9ColorsSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant9ShapesSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant10ChartSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant10ColorsSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant11ColorsSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant11ChartSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant12ChartSettings(APIModel):
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
    metric_font_color_index: int | float | None = Field(
        default=None,
        alias="metricFontColorIndex",
        description="Metric value color index in the palette.",
    )
    title_mode: Literal["by-field", "manual", "hide"] | str | None = Field(
        default=None, alias="titleMode", description="Metric title display mode."
    )
    title: str | None = Field(default=None, description="Metric title.")


class WizardV1ConfigSchemaVisualizationVariant12ColorsSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant13ChartSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant13ColorsSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant14ChartSettings(APIModel):
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
    limit: int | float | None = Field(
        default=None, description="Maximum number of rows displayed per page."
    )
    grouping: Literal["on", "disabled", "off"] | str | None = Field(
        default=None, description="Table row grouping mode."
    )
    totals: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether a total row is displayed."
    )
    pinned_columns: int | float | None = Field(
        default=None,
        alias="pinnedColumns",
        description="Number of columns pinned to the left side.",
    )
    preserve_white_space: bool | None = Field(
        default=None,
        alias="preserveWhiteSpace",
        description="Whether whitespace in table values is preserved.",
    )


class WizardV1ConfigSchemaVisualizationVariant14ColorsSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant15ChartSettings(APIModel):
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
    limit: int | float | None = Field(
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
    pinned_columns: int | float | None = Field(
        default=None,
        alias="pinnedColumns",
        description="Number of columns pinned to the left side.",
    )
    preserve_white_space: bool | None = Field(
        default=None,
        alias="preserveWhiteSpace",
        description="Whether whitespace in table values is preserved.",
    )


class WizardV1ConfigSchemaVisualizationVariant15ColorsSettings(APIModel):
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


class WizardV1ConfigSchemaVisualizationVariant16ChartSettings(APIModel):
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
    zoom_value: int | float | None = Field(
        default=None,
        alias="zoomValue",
        description="Initial map zoom level from 1 to 21.",
    )


class WizardV1ConfigSchemaVisualizationVariant17ChartSettings(APIModel):
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


class WizardV1Annotation(APIModel):
    """Annotation information."""

    description: str | None = Field(default=None, description="Description of the entry.")


class GetWizardChartV1ResultPermissions(APIModel):
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


class WizardLabelsItemSchemaModel(OtherKind, WizardLabelsItemSchema):
    pass


class WizardSortItemSchemaModel(OtherKindByTitle, WizardSortItemSchema):
    pass


class WizardV1FiltersItemSchemaFilter(APIModel):
    """Filter applied to the field."""

    operation: WizardV1FiltersItemSchemaFilterOperation | None = None
    value: str | list[str] | None = Field(
        default=None, description="Value or values used by the filter operation."
    )


class WizardFieldSchemaVariant1BarsSettingsColorSettingsVariant1Settings(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientType", description="Gradient type."
    )
    thresholds: (
        WizardFieldSchemaVariant1BarsSettingsColorSettingsVariant1SettingsThresholdsVariant1
        | WizardFieldSchemaVariant1BarsSettingsColorSettingsVariant1SettingsThresholdsVariant2
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Thresholds that define the gradient color scale.")
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class WizardFieldSchemaVariant1BarsSettingsColorSettingsVariant2(APIModel):
    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: WizardFieldSchemaVariant1BarsSettingsColorSettingsVariant2Settings | None = None


class WizardFieldSchemaVariant1BarsSettingsColorSettingsVariant3(APIModel):
    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: WizardFieldSchemaVariant1BarsSettingsColorSettingsVariant3Settings | None = None


class WizardFieldSchemaVariant1BarsSettingsScaleVariant2(APIModel):
    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: WizardFieldSchemaVariant1BarsSettingsScaleVariant2Settings | None = None


class WizardFieldSchemaVariant1BackgroundSettingsSettings(APIModel):
    """Background color configuration."""

    palette_state: WizardFieldSchemaVariant1BackgroundSettingsSettingsPaletteState | None = Field(
        default=None, alias="paletteState"
    )
    gradient_state: WizardFieldSchemaVariant1BackgroundSettingsSettingsGradientState | None = Field(
        default=None, alias="gradientState"
    )
    is_continuous: bool | None = Field(
        default=None,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WizardFieldSchemaVariant1ColumnSettings(APIModel):
    """Table column settings."""

    width: (
        WizardFieldSchemaVariant1ColumnSettingsWidthVariant1
        | WizardFieldSchemaVariant1ColumnSettingsWidthVariant2
        | WizardFieldSchemaVariant1ColumnSettingsWidthVariant3
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Table column width settings.")
    horizontal_alignment: Literal["auto", "start", "center", "end"] | str | None = Field(
        default=None,
        alias="horizontalAlignment",
        description="Horizontal alignment of values in the column.",
    )


class WizardFieldSchemaVariant1FieldsItemBarsSettingsColorSettingsVariant1Settings(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientType", description="Gradient type."
    )
    thresholds: (
        WizardFieldSchemaVariant1FieldsItemBarsSettingsColorSettingsVariant1SettingsThresholdsVariant1
        | WizardFieldSchemaVariant1FieldsItemBarsSettingsColorSettingsVariant1SettingsThresholdsVariant2
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Thresholds that define the gradient color scale.")
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class WizardFieldSchemaVariant1FieldsItemBarsSettingsColorSettingsVariant2(APIModel):
    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: (
        WizardFieldSchemaVariant1FieldsItemBarsSettingsColorSettingsVariant2Settings | None
    ) = None


class WizardFieldSchemaVariant1FieldsItemBarsSettingsColorSettingsVariant3(APIModel):
    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: (
        WizardFieldSchemaVariant1FieldsItemBarsSettingsColorSettingsVariant3Settings | None
    ) = None


class WizardFieldSchemaVariant1FieldsItemBarsSettingsScaleVariant2(APIModel):
    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: WizardFieldSchemaVariant1FieldsItemBarsSettingsScaleVariant2Settings | None = None


class WizardFieldSchemaVariant1FieldsItemBackgroundSettingsSettings(APIModel):
    """Background color configuration."""

    palette_state: (
        WizardFieldSchemaVariant1FieldsItemBackgroundSettingsSettingsPaletteState | None
    ) = Field(default=None, alias="paletteState")
    gradient_state: (
        WizardFieldSchemaVariant1FieldsItemBackgroundSettingsSettingsGradientState | None
    ) = Field(default=None, alias="gradientState")
    is_continuous: bool | None = Field(
        default=None,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WizardFieldSchemaVariant1FieldsItemColumnSettings(APIModel):
    """Table column settings."""

    width: (
        WizardFieldSchemaVariant1FieldsItemColumnSettingsWidthVariant1
        | WizardFieldSchemaVariant1FieldsItemColumnSettingsWidthVariant2
        | WizardFieldSchemaVariant1FieldsItemColumnSettingsWidthVariant3
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Table column width settings.")
    horizontal_alignment: Literal["auto", "start", "center", "end"] | str | None = Field(
        default=None,
        alias="horizontalAlignment",
        description="Horizontal alignment of values in the column.",
    )


class WizardFieldSchemaVariant2BarsSettingsColorSettingsVariant1Settings(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientType", description="Gradient type."
    )
    thresholds: (
        WizardFieldSchemaVariant2BarsSettingsColorSettingsVariant1SettingsThresholdsVariant1
        | WizardFieldSchemaVariant2BarsSettingsColorSettingsVariant1SettingsThresholdsVariant2
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Thresholds that define the gradient color scale.")
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class WizardFieldSchemaVariant2BarsSettingsColorSettingsVariant2(APIModel):
    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: WizardFieldSchemaVariant2BarsSettingsColorSettingsVariant2Settings | None = None


class WizardFieldSchemaVariant2BarsSettingsColorSettingsVariant3(APIModel):
    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: WizardFieldSchemaVariant2BarsSettingsColorSettingsVariant3Settings | None = None


class WizardFieldSchemaVariant2BarsSettingsScaleVariant2(APIModel):
    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: WizardFieldSchemaVariant2BarsSettingsScaleVariant2Settings | None = None


class WizardFieldSchemaVariant2BackgroundSettingsSettings(APIModel):
    """Background color configuration."""

    palette_state: WizardFieldSchemaVariant2BackgroundSettingsSettingsPaletteState | None = Field(
        default=None, alias="paletteState"
    )
    gradient_state: WizardFieldSchemaVariant2BackgroundSettingsSettingsGradientState | None = Field(
        default=None, alias="gradientState"
    )
    is_continuous: bool | None = Field(
        default=None,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WizardFieldSchemaVariant2ColumnSettings(APIModel):
    """Table column settings."""

    width: (
        WizardFieldSchemaVariant2ColumnSettingsWidthVariant1
        | WizardFieldSchemaVariant2ColumnSettingsWidthVariant2
        | WizardFieldSchemaVariant2ColumnSettingsWidthVariant3
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Table column width settings.")
    horizontal_alignment: Literal["auto", "start", "center", "end"] | str | None = Field(
        default=None,
        alias="horizontalAlignment",
        description="Horizontal alignment of values in the column.",
    )


class WizardFieldSchemaVariant3BarsSettingsColorSettingsVariant1Settings(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientType", description="Gradient type."
    )
    thresholds: (
        WizardFieldSchemaVariant3BarsSettingsColorSettingsVariant1SettingsThresholdsVariant1
        | WizardFieldSchemaVariant3BarsSettingsColorSettingsVariant1SettingsThresholdsVariant2
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Thresholds that define the gradient color scale.")
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class WizardFieldSchemaVariant3BarsSettingsColorSettingsVariant2(APIModel):
    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: WizardFieldSchemaVariant3BarsSettingsColorSettingsVariant2Settings | None = None


class WizardFieldSchemaVariant3BarsSettingsColorSettingsVariant3(APIModel):
    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: WizardFieldSchemaVariant3BarsSettingsColorSettingsVariant3Settings | None = None


class WizardFieldSchemaVariant3BarsSettingsScaleVariant2(APIModel):
    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: WizardFieldSchemaVariant3BarsSettingsScaleVariant2Settings | None = None


class WizardFieldSchemaVariant3BackgroundSettingsSettings(APIModel):
    """Background color configuration."""

    palette_state: WizardFieldSchemaVariant3BackgroundSettingsSettingsPaletteState | None = Field(
        default=None, alias="paletteState"
    )
    gradient_state: WizardFieldSchemaVariant3BackgroundSettingsSettingsGradientState | None = Field(
        default=None, alias="gradientState"
    )
    is_continuous: bool | None = Field(
        default=None,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WizardFieldSchemaVariant3ColumnSettings(APIModel):
    """Table column settings."""

    width: (
        WizardFieldSchemaVariant3ColumnSettingsWidthVariant1
        | WizardFieldSchemaVariant3ColumnSettingsWidthVariant2
        | WizardFieldSchemaVariant3ColumnSettingsWidthVariant3
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Table column width settings.")
    horizontal_alignment: Literal["auto", "start", "center", "end"] | str | None = Field(
        default=None,
        alias="horizontalAlignment",
        description="Horizontal alignment of values in the column.",
    )


class WizardFieldSchemaVariant4BarsSettingsColorSettingsVariant1Settings(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientType", description="Gradient type."
    )
    thresholds: (
        WizardFieldSchemaVariant4BarsSettingsColorSettingsVariant1SettingsThresholdsVariant1
        | WizardFieldSchemaVariant4BarsSettingsColorSettingsVariant1SettingsThresholdsVariant2
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Thresholds that define the gradient color scale.")
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class WizardFieldSchemaVariant4BarsSettingsColorSettingsVariant2(APIModel):
    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: WizardFieldSchemaVariant4BarsSettingsColorSettingsVariant2Settings | None = None


class WizardFieldSchemaVariant4BarsSettingsColorSettingsVariant3(APIModel):
    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: WizardFieldSchemaVariant4BarsSettingsColorSettingsVariant3Settings | None = None


class WizardFieldSchemaVariant4BarsSettingsScaleVariant2(APIModel):
    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: WizardFieldSchemaVariant4BarsSettingsScaleVariant2Settings | None = None


class WizardFieldSchemaVariant4BackgroundSettingsSettings(APIModel):
    """Background color configuration."""

    palette_state: WizardFieldSchemaVariant4BackgroundSettingsSettingsPaletteState | None = Field(
        default=None, alias="paletteState"
    )
    gradient_state: WizardFieldSchemaVariant4BackgroundSettingsSettingsGradientState | None = Field(
        default=None, alias="gradientState"
    )
    is_continuous: bool | None = Field(
        default=None,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WizardFieldSchemaVariant4ColumnSettings(APIModel):
    """Table column settings."""

    width: (
        WizardFieldSchemaVariant4ColumnSettingsWidthVariant1
        | WizardFieldSchemaVariant4ColumnSettingsWidthVariant2
        | WizardFieldSchemaVariant4ColumnSettingsWidthVariant3
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Table column width settings.")
    horizontal_alignment: Literal["auto", "start", "center", "end"] | str | None = Field(
        default=None,
        alias="horizontalAlignment",
        description="Horizontal alignment of values in the column.",
    )


class WizardPseudoFieldSchemaVariant1BarsSettingsColorSettingsVariant1Settings(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientType", description="Gradient type."
    )
    thresholds: (
        WizardPseudoFieldSchemaVariant1BarsSettingsColorSettingsVariant1SettingsThresholdsVariant1
        | WizardPseudoFieldSchemaVariant1BarsSettingsColorSettingsVariant1SettingsThresholdsVariant2
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Thresholds that define the gradient color scale.")
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class WizardPseudoFieldSchemaVariant1BarsSettingsColorSettingsVariant2(APIModel):
    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: WizardPseudoFieldSchemaVariant1BarsSettingsColorSettingsVariant2Settings | None = None


class WizardPseudoFieldSchemaVariant1BarsSettingsColorSettingsVariant3(APIModel):
    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: WizardPseudoFieldSchemaVariant1BarsSettingsColorSettingsVariant3Settings | None = None


class WizardPseudoFieldSchemaVariant1BarsSettingsScaleVariant2(APIModel):
    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: WizardPseudoFieldSchemaVariant1BarsSettingsScaleVariant2Settings | None = None


class WizardPseudoFieldSchemaVariant1BackgroundSettingsSettings(APIModel):
    """Background color configuration."""

    palette_state: WizardPseudoFieldSchemaVariant1BackgroundSettingsSettingsPaletteState | None = (
        Field(default=None, alias="paletteState")
    )
    gradient_state: (
        WizardPseudoFieldSchemaVariant1BackgroundSettingsSettingsGradientState | None
    ) = Field(default=None, alias="gradientState")
    is_continuous: bool | None = Field(
        default=None,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WizardPseudoFieldSchemaVariant1ColumnSettings(APIModel):
    """Table column settings."""

    width: (
        WizardPseudoFieldSchemaVariant1ColumnSettingsWidthVariant1
        | WizardPseudoFieldSchemaVariant1ColumnSettingsWidthVariant2
        | WizardPseudoFieldSchemaVariant1ColumnSettingsWidthVariant3
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Table column width settings.")
    horizontal_alignment: Literal["auto", "start", "center", "end"] | str | None = Field(
        default=None,
        alias="horizontalAlignment",
        description="Horizontal alignment of values in the column.",
    )


class WizardPseudoFieldSchemaVariant2BarsSettingsColorSettingsVariant1Settings(APIModel):
    """Gradient bar color settings."""

    gradient_type: Literal["2-point", "3-point"] | str | None = Field(
        default=None, alias="gradientType", description="Gradient type."
    )
    thresholds: (
        WizardPseudoFieldSchemaVariant2BarsSettingsColorSettingsVariant1SettingsThresholdsVariant1
        | WizardPseudoFieldSchemaVariant2BarsSettingsColorSettingsVariant1SettingsThresholdsVariant2
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Thresholds that define the gradient color scale.")
    palette: str | None = Field(default=None, description="Color palette identifier.")
    reversed: bool | None = Field(default=None, description="Whether to reverse the color palette.")


class WizardPseudoFieldSchemaVariant2BarsSettingsColorSettingsVariant2(APIModel):
    color_type: Literal["one-color"] = Field(
        ..., alias="colorType", description="Use one color for all bars."
    )
    settings: WizardPseudoFieldSchemaVariant2BarsSettingsColorSettingsVariant2Settings | None = None


class WizardPseudoFieldSchemaVariant2BarsSettingsColorSettingsVariant3(APIModel):
    color_type: Literal["two-color"] = Field(
        ...,
        alias="colorType",
        description="Use separate colors for negative and positive bars.",
    )
    settings: WizardPseudoFieldSchemaVariant2BarsSettingsColorSettingsVariant3Settings | None = None


class WizardPseudoFieldSchemaVariant2BarsSettingsScaleVariant2(APIModel):
    mode: Literal["manual"] = Field(..., description="Use a manually specified bar scale.")
    settings: WizardPseudoFieldSchemaVariant2BarsSettingsScaleVariant2Settings | None = None


class WizardPseudoFieldSchemaVariant2BackgroundSettingsSettings(APIModel):
    """Background color configuration."""

    palette_state: WizardPseudoFieldSchemaVariant2BackgroundSettingsSettingsPaletteState | None = (
        Field(default=None, alias="paletteState")
    )
    gradient_state: (
        WizardPseudoFieldSchemaVariant2BackgroundSettingsSettingsGradientState | None
    ) = Field(default=None, alias="gradientState")
    is_continuous: bool | None = Field(
        default=None,
        alias="isContinuous",
        description="Whether to use continuous instead of discrete coloring.",
    )


class WizardPseudoFieldSchemaVariant2ColumnSettings(APIModel):
    """Table column settings."""

    width: (
        WizardPseudoFieldSchemaVariant2ColumnSettingsWidthVariant1
        | WizardPseudoFieldSchemaVariant2ColumnSettingsWidthVariant2
        | WizardPseudoFieldSchemaVariant2ColumnSettingsWidthVariant3
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Table column width settings.")
    horizontal_alignment: Literal["auto", "start", "center", "end"] | str | None = Field(
        default=None,
        alias="horizontalAlignment",
        description="Horizontal alignment of values in the column.",
    )


class WizardV1CombinedChartLayerSchemaVariant1XSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1CombinedChartLayerSchemaVariant1XSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1CombinedChartLayerSchemaVariant1YSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1CombinedChartLayerSchemaVariant1YSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1CombinedChartLayerSchemaVariant1Y2Settings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1CombinedChartLayerSchemaVariant1Y2SettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1CombinedChartLayerSchemaVariant1ShapesSettings(APIModel):
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
    common_line_settings: (
        WizardV1CombinedChartLayerSchemaVariant1ShapesSettingsCommonLineSettings | None
    ) = Field(default=None, alias="commonLineSettings")


class WizardV1CombinedChartLayerSchemaVariant2XSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1CombinedChartLayerSchemaVariant2XSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1CombinedChartLayerSchemaVariant2YSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1CombinedChartLayerSchemaVariant2YSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1CombinedChartLayerSchemaVariant3XSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1CombinedChartLayerSchemaVariant3XSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1CombinedChartLayerSchemaVariant3YSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1CombinedChartLayerSchemaVariant3YSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaSourcesUpdatesItem(APIModel):
    action: (
        Literal["add_field", "add", "update_field", "update", "delete", "delete_field"] | str | None
    ) = Field(default=None, description="Operation applied to the local field.")
    field: WizardV1ConfigSchemaSourcesUpdatesItemField | None = None
    debug_info: str | None = Field(
        default=None,
        description="Internal marker describing how the field update was produced.",
    )


class WizardV1ConfigSchemaSourcesLinksItemFieldsValue(APIModel):
    field: WizardV1ConfigSchemaSourcesLinksItemFieldsValueField | None = None
    dataset: WizardV1ConfigSchemaSourcesLinksItemFieldsValueDataset | None = None


class WizardV1ConfigSchemaSourcesHierarchiesItem(APIModel):
    guid: str | None = Field(default=None, description="Hierarchy identifier.")
    title: str | None = Field(default=None, description="Hierarchy display title.")
    fields: list[WizardV1ConfigSchemaSourcesHierarchiesItemFieldsItem] | None = Field(
        default=None, description="Ordered fields included in the hierarchy."
    )


class WizardV1ConfigSchemaVisualizationVariant1ChartSettingsNavigatorSettings(APIModel):
    """Chart navigator settings."""

    navigator_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="navigatorMode",
        description="Whether the chart navigator is displayed.",
    )
    selected_lines: list[str] | None = Field(
        default=None,
        alias="selectedLines",
        description="Series names shown in the navigator; values are not field GUIDs.",
    )
    lines_mode: Literal["all", "selected"] | str | None = Field(
        default=None,
        alias="linesMode",
        description="Which chart series are displayed in the navigator.",
    )
    period_settings: (
        WizardV1ConfigSchemaVisualizationVariant1ChartSettingsNavigatorSettingsPeriodSettings | None
    ) = Field(default=None, alias="periodSettings")


class WizardV1ConfigSchemaVisualizationVariant1XSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant1XSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant1YSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant1YSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant1Y2Settings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant1Y2SettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant1ShapesSettings(APIModel):
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
    common_line_settings: (
        WizardV1ConfigSchemaVisualizationVariant1ShapesSettingsCommonLineSettings | None
    ) = Field(default=None, alias="commonLineSettings")


class WizardV1ConfigSchemaVisualizationVariant2ChartSettingsNavigatorSettings(APIModel):
    """Chart navigator settings."""

    navigator_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="navigatorMode",
        description="Whether the chart navigator is displayed.",
    )
    selected_lines: list[str] | None = Field(
        default=None,
        alias="selectedLines",
        description="Series names shown in the navigator; values are not field GUIDs.",
    )
    lines_mode: Literal["all", "selected"] | str | None = Field(
        default=None,
        alias="linesMode",
        description="Which chart series are displayed in the navigator.",
    )
    period_settings: (
        WizardV1ConfigSchemaVisualizationVariant2ChartSettingsNavigatorSettingsPeriodSettings | None
    ) = Field(default=None, alias="periodSettings")


class WizardV1ConfigSchemaVisualizationVariant2XSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant2XSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant2YSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant2YSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant3ChartSettingsNavigatorSettings(APIModel):
    """Chart navigator settings."""

    navigator_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="navigatorMode",
        description="Whether the chart navigator is displayed.",
    )
    selected_lines: list[str] | None = Field(
        default=None,
        alias="selectedLines",
        description="Series names shown in the navigator; values are not field GUIDs.",
    )
    lines_mode: Literal["all", "selected"] | str | None = Field(
        default=None,
        alias="linesMode",
        description="Which chart series are displayed in the navigator.",
    )
    period_settings: (
        WizardV1ConfigSchemaVisualizationVariant3ChartSettingsNavigatorSettingsPeriodSettings | None
    ) = Field(default=None, alias="periodSettings")


class WizardV1ConfigSchemaVisualizationVariant3XSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant3XSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant3YSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant3YSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant4ChartSettingsNavigatorSettings(APIModel):
    """Chart navigator settings."""

    navigator_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="navigatorMode",
        description="Whether the chart navigator is displayed.",
    )
    selected_lines: list[str] | None = Field(
        default=None,
        alias="selectedLines",
        description="Series names shown in the navigator; values are not field GUIDs.",
    )
    lines_mode: Literal["all", "selected"] | str | None = Field(
        default=None,
        alias="linesMode",
        description="Which chart series are displayed in the navigator.",
    )
    period_settings: (
        WizardV1ConfigSchemaVisualizationVariant4ChartSettingsNavigatorSettingsPeriodSettings | None
    ) = Field(default=None, alias="periodSettings")


class WizardV1ConfigSchemaVisualizationVariant4XSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant4XSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant4YSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant4YSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant5XSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant5XSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant5YSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant5YSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant5ChartSettingsNavigatorSettings(APIModel):
    """Chart navigator settings."""

    navigator_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="navigatorMode",
        description="Whether the chart navigator is displayed.",
    )
    selected_lines: list[str] | None = Field(
        default=None,
        alias="selectedLines",
        description="Series names shown in the navigator; values are not field GUIDs.",
    )
    lines_mode: Literal["all", "selected"] | str | None = Field(
        default=None,
        alias="linesMode",
        description="Which chart series are displayed in the navigator.",
    )
    period_settings: (
        WizardV1ConfigSchemaVisualizationVariant5ChartSettingsNavigatorSettingsPeriodSettings | None
    ) = Field(default=None, alias="periodSettings")


class WizardV1ConfigSchemaVisualizationVariant6XSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant6XSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant6YSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant6YSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant7XSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant7XSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant7YSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant7YSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant9XSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant9XSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant9YSettings(APIModel):
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
    grid_step_value: int | float | None = Field(
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
    axis_label_formatting: (
        WizardV1ConfigSchemaVisualizationVariant9YSettingsAxisLabelFormatting | None
    ) = Field(default=None, alias="axisLabelFormatting")
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


class WizardV1ConfigSchemaVisualizationVariant12Colors(APIModel):
    """Color configuration."""

    settings: WizardV1ConfigSchemaVisualizationVariant12ColorsSettings | None = None


class WizardV1FiltersItemSchema(APIModel):
    guid: str | None = Field(
        default=None, description="Identifier of the field used for filtering."
    )
    dataset_id: str | None = Field(
        default=None,
        alias="datasetId",
        description="Identifier of the dataset containing the field.",
    )
    fake_title: str | None = Field(
        default=None,
        alias="fakeTitle",
        description="Chart-local display title override for the field.",
    )
    filter: WizardV1FiltersItemSchemaFilter | None = None


class WizardFieldSchemaVariant1BarsSettingsColorSettingsVariant1(APIModel):
    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: WizardFieldSchemaVariant1BarsSettingsColorSettingsVariant1Settings | None = None


class WizardFieldSchemaVariant1BackgroundSettings(APIModel):
    """Conditional background settings."""

    enabled: bool | None = Field(
        default=None, description="Whether conditional background coloring is enabled."
    )
    color_field_guid: str | None = Field(
        default=None,
        alias="colorFieldGuid",
        description="Identifier of the field used to color the background.",
    )
    settings_id: str | None = Field(
        default=None,
        alias="settingsId",
        description="Identifier of the background color settings.",
    )
    settings: WizardFieldSchemaVariant1BackgroundSettingsSettings | None = None


class WizardFieldSchemaVariant1FieldsItemBarsSettingsColorSettingsVariant1(APIModel):
    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: (
        WizardFieldSchemaVariant1FieldsItemBarsSettingsColorSettingsVariant1Settings | None
    ) = None


class WizardFieldSchemaVariant1FieldsItemBackgroundSettings(APIModel):
    """Conditional background settings."""

    enabled: bool | None = Field(
        default=None, description="Whether conditional background coloring is enabled."
    )
    color_field_guid: str | None = Field(
        default=None,
        alias="colorFieldGuid",
        description="Identifier of the field used to color the background.",
    )
    settings_id: str | None = Field(
        default=None,
        alias="settingsId",
        description="Identifier of the background color settings.",
    )
    settings: WizardFieldSchemaVariant1FieldsItemBackgroundSettingsSettings | None = None


class WizardFieldSchemaVariant2BarsSettingsColorSettingsVariant1(APIModel):
    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: WizardFieldSchemaVariant2BarsSettingsColorSettingsVariant1Settings | None = None


class WizardFieldSchemaVariant2BackgroundSettings(APIModel):
    """Conditional background settings."""

    enabled: bool | None = Field(
        default=None, description="Whether conditional background coloring is enabled."
    )
    color_field_guid: str | None = Field(
        default=None,
        alias="colorFieldGuid",
        description="Identifier of the field used to color the background.",
    )
    settings_id: str | None = Field(
        default=None,
        alias="settingsId",
        description="Identifier of the background color settings.",
    )
    settings: WizardFieldSchemaVariant2BackgroundSettingsSettings | None = None


class WizardFieldSchemaVariant3BarsSettingsColorSettingsVariant1(APIModel):
    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: WizardFieldSchemaVariant3BarsSettingsColorSettingsVariant1Settings | None = None


class WizardFieldSchemaVariant3BackgroundSettings(APIModel):
    """Conditional background settings."""

    enabled: bool | None = Field(
        default=None, description="Whether conditional background coloring is enabled."
    )
    color_field_guid: str | None = Field(
        default=None,
        alias="colorFieldGuid",
        description="Identifier of the field used to color the background.",
    )
    settings_id: str | None = Field(
        default=None,
        alias="settingsId",
        description="Identifier of the background color settings.",
    )
    settings: WizardFieldSchemaVariant3BackgroundSettingsSettings | None = None


class WizardFieldSchemaVariant4BarsSettingsColorSettingsVariant1(APIModel):
    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: WizardFieldSchemaVariant4BarsSettingsColorSettingsVariant1Settings | None = None


class WizardFieldSchemaVariant4BackgroundSettings(APIModel):
    """Conditional background settings."""

    enabled: bool | None = Field(
        default=None, description="Whether conditional background coloring is enabled."
    )
    color_field_guid: str | None = Field(
        default=None,
        alias="colorFieldGuid",
        description="Identifier of the field used to color the background.",
    )
    settings_id: str | None = Field(
        default=None,
        alias="settingsId",
        description="Identifier of the background color settings.",
    )
    settings: WizardFieldSchemaVariant4BackgroundSettingsSettings | None = None


class WizardPseudoFieldSchemaVariant1BarsSettingsColorSettingsVariant1(APIModel):
    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: WizardPseudoFieldSchemaVariant1BarsSettingsColorSettingsVariant1Settings | None = None


class WizardPseudoFieldSchemaVariant1BackgroundSettings(APIModel):
    """Conditional background settings."""

    enabled: bool | None = Field(
        default=None, description="Whether conditional background coloring is enabled."
    )
    color_field_guid: str | None = Field(
        default=None,
        alias="colorFieldGuid",
        description="Identifier of the field used to color the background.",
    )
    settings_id: str | None = Field(
        default=None,
        alias="settingsId",
        description="Identifier of the background color settings.",
    )
    settings: WizardPseudoFieldSchemaVariant1BackgroundSettingsSettings | None = None


class WizardPseudoFieldSchemaVariant2BarsSettingsColorSettingsVariant1(APIModel):
    color_type: Literal["gradient"] = Field(
        ..., alias="colorType", description="Use a gradient to color bars."
    )
    settings: WizardPseudoFieldSchemaVariant2BarsSettingsColorSettingsVariant1Settings | None = None


class WizardPseudoFieldSchemaVariant2BackgroundSettings(APIModel):
    """Conditional background settings."""

    enabled: bool | None = Field(
        default=None, description="Whether conditional background coloring is enabled."
    )
    color_field_guid: str | None = Field(
        default=None,
        alias="colorFieldGuid",
        description="Identifier of the field used to color the background.",
    )
    settings_id: str | None = Field(
        default=None,
        alias="settingsId",
        description="Identifier of the background color settings.",
    )
    settings: WizardPseudoFieldSchemaVariant2BackgroundSettingsSettings | None = None


class WizardV1GeolayerLayerSchemaVariant1Filters(APIModel):
    """Filter configuration."""

    items: list[WizardV1FiltersItemSchema] | None = Field(
        default=None, description="Filters applied to the layer."
    )


class WizardV1GeolayerLayerSchemaVariant2Filters(APIModel):
    """Filter configuration."""

    items: list[WizardV1FiltersItemSchema] | None = Field(
        default=None, description="Filters applied to the layer."
    )


class WizardV1GeolayerLayerSchemaVariant3Filters(APIModel):
    """Filter configuration."""

    items: list[WizardV1FiltersItemSchema] | None = Field(
        default=None, description="Filters applied to the layer."
    )


class WizardV1GeolayerLayerSchemaVariant4Filters(APIModel):
    """Filter configuration."""

    items: list[WizardV1FiltersItemSchema] | None = Field(
        default=None, description="Filters applied to the layer."
    )


class WizardV1GeolayerLayerSchemaVariant5Filters(APIModel):
    """Filter configuration."""

    items: list[WizardV1FiltersItemSchema] | None = Field(
        default=None, description="Filters applied to the layer."
    )


class WizardV1ConfigSchemaSourcesLinksItem(APIModel):
    id: str | None = Field(default=None, description="Dataset link identifier.")
    fields: dict[str, WizardV1ConfigSchemaSourcesLinksItemFieldsValue] | None = Field(
        default=None,
        description="Linked field information keyed by dataset identifier.",
    )


class WizardV1ConfigSchemaVisualizationVariant1ChartSettings(APIModel):
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
    navigator_settings: (
        WizardV1ConfigSchemaVisualizationVariant1ChartSettingsNavigatorSettings | None
    ) = Field(default=None, alias="navigatorSettings")


class WizardV1ConfigSchemaVisualizationVariant2ChartSettings(APIModel):
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
    navigator_settings: (
        WizardV1ConfigSchemaVisualizationVariant2ChartSettingsNavigatorSettings | None
    ) = Field(default=None, alias="navigatorSettings")


class WizardV1ConfigSchemaVisualizationVariant3ChartSettings(APIModel):
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
    navigator_settings: (
        WizardV1ConfigSchemaVisualizationVariant3ChartSettingsNavigatorSettings | None
    ) = Field(default=None, alias="navigatorSettings")


class WizardV1ConfigSchemaVisualizationVariant4ChartSettings(APIModel):
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
    navigator_settings: (
        WizardV1ConfigSchemaVisualizationVariant4ChartSettingsNavigatorSettings | None
    ) = Field(default=None, alias="navigatorSettings")
    stacking: Literal["on", "off"] | str | None = Field(
        default=None, description="Whether area series are stacked."
    )


class WizardV1ConfigSchemaVisualizationVariant5ChartSettings(APIModel):
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
    navigator_settings: (
        WizardV1ConfigSchemaVisualizationVariant5ChartSettingsNavigatorSettings | None
    ) = Field(default=None, alias="navigatorSettings")


class WizardFieldSchemaVariant1BarsSettings(APIModel):
    """In-cell bar settings."""

    enabled: bool | None = Field(
        default=None, description="Whether to display bars in table cells."
    )
    color_settings: (
        WizardFieldSchemaVariant1BarsSettingsColorSettingsVariant1
        | WizardFieldSchemaVariant1BarsSettingsColorSettingsVariant2
        | WizardFieldSchemaVariant1BarsSettingsColorSettingsVariant3
        | OtherKindByColorType
        | None
    ) = Field(default=None, alias="colorSettings", description="Bar color settings.")
    show_labels: bool | None = Field(
        default=None,
        alias="showLabels",
        description="Whether to display values over bars.",
    )
    align: Literal["left", "right", "default"] | str | None = Field(
        default=None, description="Bar alignment within table cells."
    )
    scale: (
        WizardFieldSchemaVariant1BarsSettingsScaleVariant1
        | WizardFieldSchemaVariant1BarsSettingsScaleVariant2
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Scale used to calculate bar lengths.")
    show_bars_in_totals: bool | None = Field(
        default=None,
        alias="showBarsInTotals",
        description="Whether to display bars in total rows.",
    )


class WizardFieldSchemaVariant1FieldsItemBarsSettings(APIModel):
    """In-cell bar settings."""

    enabled: bool | None = Field(
        default=None, description="Whether to display bars in table cells."
    )
    color_settings: (
        WizardFieldSchemaVariant1FieldsItemBarsSettingsColorSettingsVariant1
        | WizardFieldSchemaVariant1FieldsItemBarsSettingsColorSettingsVariant2
        | WizardFieldSchemaVariant1FieldsItemBarsSettingsColorSettingsVariant3
        | OtherKindByColorType
        | None
    ) = Field(default=None, alias="colorSettings", description="Bar color settings.")
    show_labels: bool | None = Field(
        default=None,
        alias="showLabels",
        description="Whether to display values over bars.",
    )
    align: Literal["left", "right", "default"] | str | None = Field(
        default=None, description="Bar alignment within table cells."
    )
    scale: (
        WizardFieldSchemaVariant1FieldsItemBarsSettingsScaleVariant1
        | WizardFieldSchemaVariant1FieldsItemBarsSettingsScaleVariant2
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Scale used to calculate bar lengths.")
    show_bars_in_totals: bool | None = Field(
        default=None,
        alias="showBarsInTotals",
        description="Whether to display bars in total rows.",
    )


class WizardFieldSchemaVariant2BarsSettings(APIModel):
    """In-cell bar settings."""

    enabled: bool | None = Field(
        default=None, description="Whether to display bars in table cells."
    )
    color_settings: (
        WizardFieldSchemaVariant2BarsSettingsColorSettingsVariant1
        | WizardFieldSchemaVariant2BarsSettingsColorSettingsVariant2
        | WizardFieldSchemaVariant2BarsSettingsColorSettingsVariant3
        | OtherKindByColorType
        | None
    ) = Field(default=None, alias="colorSettings", description="Bar color settings.")
    show_labels: bool | None = Field(
        default=None,
        alias="showLabels",
        description="Whether to display values over bars.",
    )
    align: Literal["left", "right", "default"] | str | None = Field(
        default=None, description="Bar alignment within table cells."
    )
    scale: (
        WizardFieldSchemaVariant2BarsSettingsScaleVariant1
        | WizardFieldSchemaVariant2BarsSettingsScaleVariant2
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Scale used to calculate bar lengths.")
    show_bars_in_totals: bool | None = Field(
        default=None,
        alias="showBarsInTotals",
        description="Whether to display bars in total rows.",
    )


class WizardFieldSchemaVariant3BarsSettings(APIModel):
    """In-cell bar settings."""

    enabled: bool | None = Field(
        default=None, description="Whether to display bars in table cells."
    )
    color_settings: (
        WizardFieldSchemaVariant3BarsSettingsColorSettingsVariant1
        | WizardFieldSchemaVariant3BarsSettingsColorSettingsVariant2
        | WizardFieldSchemaVariant3BarsSettingsColorSettingsVariant3
        | OtherKindByColorType
        | None
    ) = Field(default=None, alias="colorSettings", description="Bar color settings.")
    show_labels: bool | None = Field(
        default=None,
        alias="showLabels",
        description="Whether to display values over bars.",
    )
    align: Literal["left", "right", "default"] | str | None = Field(
        default=None, description="Bar alignment within table cells."
    )
    scale: (
        WizardFieldSchemaVariant3BarsSettingsScaleVariant1
        | WizardFieldSchemaVariant3BarsSettingsScaleVariant2
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Scale used to calculate bar lengths.")
    show_bars_in_totals: bool | None = Field(
        default=None,
        alias="showBarsInTotals",
        description="Whether to display bars in total rows.",
    )


class WizardFieldSchemaVariant4BarsSettings(APIModel):
    """In-cell bar settings."""

    enabled: bool | None = Field(
        default=None, description="Whether to display bars in table cells."
    )
    color_settings: (
        WizardFieldSchemaVariant4BarsSettingsColorSettingsVariant1
        | WizardFieldSchemaVariant4BarsSettingsColorSettingsVariant2
        | WizardFieldSchemaVariant4BarsSettingsColorSettingsVariant3
        | OtherKindByColorType
        | None
    ) = Field(default=None, alias="colorSettings", description="Bar color settings.")
    show_labels: bool | None = Field(
        default=None,
        alias="showLabels",
        description="Whether to display values over bars.",
    )
    align: Literal["left", "right", "default"] | str | None = Field(
        default=None, description="Bar alignment within table cells."
    )
    scale: (
        WizardFieldSchemaVariant4BarsSettingsScaleVariant1
        | WizardFieldSchemaVariant4BarsSettingsScaleVariant2
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Scale used to calculate bar lengths.")
    show_bars_in_totals: bool | None = Field(
        default=None,
        alias="showBarsInTotals",
        description="Whether to display bars in total rows.",
    )


class WizardPseudoFieldSchemaVariant1BarsSettings(APIModel):
    """In-cell bar settings."""

    enabled: bool | None = Field(
        default=None, description="Whether to display bars in table cells."
    )
    color_settings: (
        WizardPseudoFieldSchemaVariant1BarsSettingsColorSettingsVariant1
        | WizardPseudoFieldSchemaVariant1BarsSettingsColorSettingsVariant2
        | WizardPseudoFieldSchemaVariant1BarsSettingsColorSettingsVariant3
        | OtherKindByColorType
        | None
    ) = Field(default=None, alias="colorSettings", description="Bar color settings.")
    show_labels: bool | None = Field(
        default=None,
        alias="showLabels",
        description="Whether to display values over bars.",
    )
    align: Literal["left", "right", "default"] | str | None = Field(
        default=None, description="Bar alignment within table cells."
    )
    scale: (
        WizardPseudoFieldSchemaVariant1BarsSettingsScaleVariant1
        | WizardPseudoFieldSchemaVariant1BarsSettingsScaleVariant2
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Scale used to calculate bar lengths.")
    show_bars_in_totals: bool | None = Field(
        default=None,
        alias="showBarsInTotals",
        description="Whether to display bars in total rows.",
    )


class WizardPseudoFieldSchemaVariant2BarsSettings(APIModel):
    """In-cell bar settings."""

    enabled: bool | None = Field(
        default=None, description="Whether to display bars in table cells."
    )
    color_settings: (
        WizardPseudoFieldSchemaVariant2BarsSettingsColorSettingsVariant1
        | WizardPseudoFieldSchemaVariant2BarsSettingsColorSettingsVariant2
        | WizardPseudoFieldSchemaVariant2BarsSettingsColorSettingsVariant3
        | OtherKindByColorType
        | None
    ) = Field(default=None, alias="colorSettings", description="Bar color settings.")
    show_labels: bool | None = Field(
        default=None,
        alias="showLabels",
        description="Whether to display values over bars.",
    )
    align: Literal["left", "right", "default"] | str | None = Field(
        default=None, description="Bar alignment within table cells."
    )
    scale: (
        WizardPseudoFieldSchemaVariant2BarsSettingsScaleVariant1
        | WizardPseudoFieldSchemaVariant2BarsSettingsScaleVariant2
        | OtherKindByMode
        | None
    ) = Field(default=None, description="Scale used to calculate bar lengths.")
    show_bars_in_totals: bool | None = Field(
        default=None,
        alias="showBarsInTotals",
        description="Whether to display bars in total rows.",
    )


class WizardV1ConfigSchemaSources(APIModel):
    """Data sources, chart-local field updates, dataset links, hierarchies, and filters used by the chart."""

    datasets_ids: list[str] | None = Field(
        default=None,
        alias="datasetsIds",
        description="Datasets used by the chart to retrieve data.",
    )
    updates: list[WizardV1ConfigSchemaSourcesUpdatesItem] | None = Field(
        default=None,
        description="Operations that add, update, or delete chart-local fields.",
    )
    links: list[WizardV1ConfigSchemaSourcesLinksItem] | None = Field(
        default=None,
        description="Fields used to link datasets in multi-dataset charts.",
    )
    hierarchies: list[WizardV1ConfigSchemaSourcesHierarchiesItem] | None = Field(
        default=None,
        description="Sets of fields used for interactive drill-down in the chart.",
    )
    filters: list[WizardV1FiltersItemSchema] | None = Field(
        default=None, description="Filters applied to chart data."
    )


class WizardFieldSchemaVariant1FieldsItem(APIModel):
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
    formatting: WizardFieldSchemaVariant1FieldsItemFormatting | None = None
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: WizardFieldSchemaVariant1FieldsItemBarsSettings | None = Field(
        default=None, alias="barsSettings"
    )
    sub_totals_settings: WizardFieldSchemaVariant1FieldsItemSubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings"
    )
    background_settings: WizardFieldSchemaVariant1FieldsItemBackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    column_settings: WizardFieldSchemaVariant1FieldsItemColumnSettings | None = Field(
        default=None, alias="columnSettings"
    )
    hint_settings: WizardFieldSchemaVariant1FieldsItemHintSettings | None = Field(
        default=None, alias="hintSettings"
    )
    guid: str | None = Field(default=None, description="Field identifier.")
    dataset_id: str | None = Field(
        default=None,
        alias="datasetId",
        description="Identifier of the dataset containing the field.",
    )


class WizardFieldSchemaVariant2(APIModel):
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
    formatting: WizardFieldSchemaVariant2Formatting | None = None
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: WizardFieldSchemaVariant2BarsSettings | None = Field(
        default=None, alias="barsSettings"
    )
    sub_totals_settings: WizardFieldSchemaVariant2SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings"
    )
    background_settings: WizardFieldSchemaVariant2BackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    column_settings: WizardFieldSchemaVariant2ColumnSettings | None = Field(
        default=None, alias="columnSettings"
    )
    hint_settings: WizardFieldSchemaVariant2HintSettings | None = Field(
        default=None, alias="hintSettings"
    )
    guid: str | None = Field(default=None, description="Field identifier.")
    dataset_id: str | None = Field(
        default=None,
        alias="datasetId",
        description="Identifier of the dataset containing the field.",
    )


class WizardFieldSchemaVariant3(APIModel):
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
    formatting: WizardFieldSchemaVariant3Formatting | None = None
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: WizardFieldSchemaVariant3BarsSettings | None = Field(
        default=None, alias="barsSettings"
    )
    sub_totals_settings: WizardFieldSchemaVariant3SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings"
    )
    background_settings: WizardFieldSchemaVariant3BackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    column_settings: WizardFieldSchemaVariant3ColumnSettings | None = Field(
        default=None, alias="columnSettings"
    )
    hint_settings: WizardFieldSchemaVariant3HintSettings | None = Field(
        default=None, alias="hintSettings"
    )
    title: Literal["Measure Names"] = Field(
        ..., description="Title identifying the Measure Names pseudo-field."
    )
    type: Literal["PSEUDO"] = Field(..., description="Field type identifying a pseudo-field.")
    data_type: Literal["string"] = Field(
        ..., description="String data type of the Measure Names pseudo-field."
    )


class WizardFieldSchemaVariant4(APIModel):
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
    formatting: WizardFieldSchemaVariant4Formatting | None = None
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: WizardFieldSchemaVariant4BarsSettings | None = Field(
        default=None, alias="barsSettings"
    )
    sub_totals_settings: WizardFieldSchemaVariant4SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings"
    )
    background_settings: WizardFieldSchemaVariant4BackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    column_settings: WizardFieldSchemaVariant4ColumnSettings | None = Field(
        default=None, alias="columnSettings"
    )
    hint_settings: WizardFieldSchemaVariant4HintSettings | None = Field(
        default=None, alias="hintSettings"
    )
    title: Literal["Measure Values"] = Field(
        ..., description="Title identifying the Measure Values pseudo-field."
    )
    type: Literal["PSEUDO"] = Field(..., description="Field type identifying a pseudo-field.")
    data_type: Literal["float"] = Field(
        ..., description="Numeric data type of the Measure Values pseudo-field."
    )


class WizardPseudoFieldSchemaVariant1(APIModel):
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
    formatting: WizardPseudoFieldSchemaVariant1Formatting | None = None
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: WizardPseudoFieldSchemaVariant1BarsSettings | None = Field(
        default=None, alias="barsSettings"
    )
    sub_totals_settings: WizardPseudoFieldSchemaVariant1SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings"
    )
    background_settings: WizardPseudoFieldSchemaVariant1BackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    column_settings: WizardPseudoFieldSchemaVariant1ColumnSettings | None = Field(
        default=None, alias="columnSettings"
    )
    hint_settings: WizardPseudoFieldSchemaVariant1HintSettings | None = Field(
        default=None, alias="hintSettings"
    )
    title: Literal["Measure Names"] = Field(
        ..., description="Title identifying the Measure Names pseudo-field."
    )
    type: Literal["PSEUDO"] = Field(..., description="Field type identifying a pseudo-field.")
    data_type: Literal["string"] = Field(
        ..., description="String data type of the Measure Names pseudo-field."
    )


class WizardPseudoFieldSchemaVariant2(APIModel):
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
    formatting: WizardPseudoFieldSchemaVariant2Formatting | None = None
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: WizardPseudoFieldSchemaVariant2BarsSettings | None = Field(
        default=None, alias="barsSettings"
    )
    sub_totals_settings: WizardPseudoFieldSchemaVariant2SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings"
    )
    background_settings: WizardPseudoFieldSchemaVariant2BackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    column_settings: WizardPseudoFieldSchemaVariant2ColumnSettings | None = Field(
        default=None, alias="columnSettings"
    )
    hint_settings: WizardPseudoFieldSchemaVariant2HintSettings | None = Field(
        default=None, alias="hintSettings"
    )
    title: Literal["Measure Values"] = Field(
        ..., description="Title identifying the Measure Values pseudo-field."
    )
    type: Literal["PSEUDO"] = Field(..., description="Field type identifying a pseudo-field.")
    data_type: Literal["float"] = Field(
        ..., description="Numeric data type of the Measure Values pseudo-field."
    )


class WizardLabelsItemSchemaModel1(WizardFieldSchemaVariant2, WizardLabelsItemSchema):
    pass


class WizardLabelsItemSchemaModel2(WizardFieldSchemaVariant3, WizardLabelsItemSchema):
    pass


class WizardLabelsItemSchemaModel3(WizardFieldSchemaVariant4, WizardLabelsItemSchema):
    pass


class WizardPseudoFieldSchema(
    RootModel[WizardPseudoFieldSchemaVariant1 | WizardPseudoFieldSchemaVariant2 | OtherKindByTitle]
):
    root: WizardPseudoFieldSchemaVariant1 | WizardPseudoFieldSchemaVariant2 | OtherKindByTitle


class WizardSortItemSchemaModel1(WizardPseudoFieldSchemaVariant1, WizardSortItemSchema):
    pass


class WizardSortItemSchemaModel2(WizardPseudoFieldSchemaVariant2, WizardSortItemSchema):
    pass


class WizardSortItemSchemaModel3(
    RootModel[WizardSortItemSchemaModel1 | WizardSortItemSchemaModel2 | WizardSortItemSchemaModel]
):
    root: WizardSortItemSchemaModel1 | WizardSortItemSchemaModel2 | WizardSortItemSchemaModel


class WizardSortItemSchemaModel4(
    RootModel[WizardSortItemSchemaVariant1 | WizardSortItemSchemaModel3]
):
    root: WizardSortItemSchemaVariant1 | WizardSortItemSchemaModel3


class WizardFieldSchemaVariant1(APIModel):
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
    formatting: WizardFieldSchemaVariant1Formatting | None = None
    format: str | None = Field(
        default=None,
        description="Date or datetime format, separate from numeric formatting.",
    )
    hide_label_mode: Literal["show", "hide"] | str | None = Field(
        default=None,
        alias="hideLabelMode",
        description="Whether to hide the field label.",
    )
    bars_settings: WizardFieldSchemaVariant1BarsSettings | None = Field(
        default=None, alias="barsSettings"
    )
    sub_totals_settings: WizardFieldSchemaVariant1SubTotalsSettings | None = Field(
        default=None, alias="subTotalsSettings"
    )
    background_settings: WizardFieldSchemaVariant1BackgroundSettings | None = Field(
        default=None, alias="backgroundSettings"
    )
    column_settings: WizardFieldSchemaVariant1ColumnSettings | None = Field(
        default=None, alias="columnSettings"
    )
    hint_settings: WizardFieldSchemaVariant1HintSettings | None = Field(
        default=None, alias="hintSettings"
    )
    guid: str | None = Field(default=None, description="Hierarchy identifier.")
    title: str | None = Field(default=None, description="Hierarchy display title.")
    data_type: Literal["hierarchy"] = Field(
        ..., description="Data type identifying this field as a hierarchy."
    )
    fields: list[WizardFieldSchemaVariant1FieldsItem] | None = Field(
        default=None, description="Fields included in the hierarchy."
    )


class WizardV1GeolayerLayerSchemaVariant3Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1CombinedChartLayerSchemaVariant1Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1CombinedChartLayerSchemaVariant2Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1CombinedChartLayerSchemaVariant3Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1ConfigSchemaVisualizationVariant1Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1ConfigSchemaVisualizationVariant2Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1ConfigSchemaVisualizationVariant3Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1ConfigSchemaVisualizationVariant4Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1ConfigSchemaVisualizationVariant5Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1ConfigSchemaVisualizationVariant6Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1ConfigSchemaVisualizationVariant7Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1ConfigSchemaVisualizationVariant8Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1ConfigSchemaVisualizationVariant9Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1ConfigSchemaVisualizationVariant10Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1ConfigSchemaVisualizationVariant11Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1ConfigSchemaVisualizationVariant14Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardV1ConfigSchemaVisualizationVariant15Sort(APIModel):
    """Sorting configuration."""

    items: list[WizardSortItemSchemaModel4] | None = Field(
        default=None, description="Chart sorting rules."
    )


class WizardFieldSchema(
    RootModel[
        WizardFieldSchemaVariant1
        | WizardFieldSchemaVariant2
        | WizardFieldSchemaVariant3
        | WizardFieldSchemaVariant4
        | shared.OtherKind
    ]
):
    root: (
        WizardFieldSchemaVariant1
        | WizardFieldSchemaVariant2
        | WizardFieldSchemaVariant3
        | WizardFieldSchemaVariant4
        | shared.OtherKind
    )


class WizardLabelsItemSchemaModel4(WizardFieldSchemaVariant1, WizardLabelsItemSchema):
    pass


class WizardLabelsItemSchemaModel5(
    RootModel[
        WizardLabelsItemSchemaModel4
        | WizardLabelsItemSchemaModel1
        | WizardLabelsItemSchemaModel2
        | WizardLabelsItemSchemaModel3
        | WizardLabelsItemSchemaModel
    ]
):
    root: (
        WizardLabelsItemSchemaModel4
        | WizardLabelsItemSchemaModel1
        | WizardLabelsItemSchemaModel2
        | WizardLabelsItemSchemaModel3
        | WizardLabelsItemSchemaModel
    )


class WizardV1GeolayerLayerSchemaVariant1Points(APIModel):
    """Point coordinate configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields containing point coordinates."
    )


class WizardV1GeolayerLayerSchemaVariant1Size(APIModel):
    """Point size configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used to determine map point sizes."
    )
    settings: WizardV1GeolayerLayerSchemaVariant1SizeSettings | None = None


class WizardV1GeolayerLayerSchemaVariant1Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1GeolayerLayerSchemaVariant1ColorsSettings | None = None


class WizardV1GeolayerLayerSchemaVariant1Labels(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel5] | None = Field(
        default=None, description="Fields whose values are displayed as point labels."
    )


class WizardV1GeolayerLayerSchemaVariant1Tooltip(APIModel):
    """Tooltip configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields displayed in point tooltips."
    )
    settings: WizardV1GeolayerLayerSchemaVariant1TooltipSettings | None = None


class WizardV1GeolayerLayerSchemaVariant2Points(APIModel):
    """Point coordinate configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields containing point coordinates."
    )


class WizardV1GeolayerLayerSchemaVariant2Size(APIModel):
    """Point size configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used to determine map point sizes."
    )
    settings: WizardV1GeolayerLayerSchemaVariant2SizeSettings | None = None


class WizardV1GeolayerLayerSchemaVariant2Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1GeolayerLayerSchemaVariant2ColorsSettings | None = None


class WizardV1GeolayerLayerSchemaVariant2Labels(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel5] | None = Field(
        default=None, description="Fields whose values are displayed as point labels."
    )


class WizardV1GeolayerLayerSchemaVariant2Tooltip(APIModel):
    """Tooltip configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields displayed in point tooltips."
    )
    settings: WizardV1GeolayerLayerSchemaVariant2TooltipSettings | None = None


class WizardV1GeolayerLayerSchemaVariant3Polylines(APIModel):
    """Polyline configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields containing polyline coordinates."
    )
    settings: WizardV1GeolayerLayerSchemaVariant3PolylinesSettings | None = None


class WizardV1GeolayerLayerSchemaVariant3Measures(APIModel):
    """Measure configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Measures displayed in polyline tooltips."
    )


class WizardV1GeolayerLayerSchemaVariant3Grouping(APIModel):
    """Grouping configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used to group polyline points."
    )


class WizardV1GeolayerLayerSchemaVariant3Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1GeolayerLayerSchemaVariant3ColorsSettings | None = None


class WizardV1GeolayerLayerSchemaVariant4Polygons(APIModel):
    """Polygon configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields containing polygon geometry."
    )


class WizardV1GeolayerLayerSchemaVariant4Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1GeolayerLayerSchemaVariant4ColorsSettings | None = None


class WizardV1GeolayerLayerSchemaVariant4Tooltip(APIModel):
    """Tooltip configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields displayed in polygon tooltips."
    )
    settings: WizardV1GeolayerLayerSchemaVariant4TooltipSettings | None = None


class WizardV1GeolayerLayerSchemaVariant5Points(APIModel):
    """Point coordinate configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields containing heatmap point coordinates."
    )


class WizardV1GeolayerLayerSchemaVariant5Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1GeolayerLayerSchemaVariant5ColorsSettings | None = None


class WizardV1CombinedChartLayerSchemaVariant1X(APIModel):
    """X-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields placed on the X-axis."
    )
    settings: WizardV1CombinedChartLayerSchemaVariant1XSettings | None = None


class WizardV1CombinedChartLayerSchemaVariant1Y(APIModel):
    """Primary Y-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Fields placed on the primary Y-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: WizardV1CombinedChartLayerSchemaVariant1YSettings | None = None


class WizardV1CombinedChartLayerSchemaVariant1Y2(APIModel):
    """Secondary Y-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Fields placed on the secondary Y-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: WizardV1CombinedChartLayerSchemaVariant1Y2Settings | None = None


class WizardV1CombinedChartLayerSchemaVariant1Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1CombinedChartLayerSchemaVariant1ColorsSettings | None = None


class WizardV1CombinedChartLayerSchemaVariant1Shapes(APIModel):
    """Line shape configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for line encoding."
    )
    settings: WizardV1CombinedChartLayerSchemaVariant1ShapesSettings | None = None


class WizardV1CombinedChartLayerSchemaVariant1Labels(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel5] | None = Field(
        default=None, description="Fields whose values are displayed as data labels."
    )
    settings: WizardV1CombinedChartLayerSchemaVariant1LabelsSettings | None = None


class WizardV1CombinedChartLayerSchemaVariant2X(APIModel):
    """X-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields placed on the X-axis."
    )
    settings: WizardV1CombinedChartLayerSchemaVariant2XSettings | None = None


class WizardV1CombinedChartLayerSchemaVariant2Y(APIModel):
    """Y-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Fields placed on the Y-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: WizardV1CombinedChartLayerSchemaVariant2YSettings | None = None


class WizardV1CombinedChartLayerSchemaVariant2Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1CombinedChartLayerSchemaVariant2ColorsSettings | None = None


class WizardV1CombinedChartLayerSchemaVariant2Labels(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel5] | None = Field(
        default=None, description="Fields whose values are displayed as data labels."
    )
    settings: WizardV1CombinedChartLayerSchemaVariant2LabelsSettings | None = None


class WizardV1CombinedChartLayerSchemaVariant3X(APIModel):
    """X-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields placed on the X-axis."
    )
    settings: WizardV1CombinedChartLayerSchemaVariant3XSettings | None = None


class WizardV1CombinedChartLayerSchemaVariant3Y(APIModel):
    """Y-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Fields placed on the Y-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: WizardV1CombinedChartLayerSchemaVariant3YSettings | None = None


class WizardV1CombinedChartLayerSchemaVariant3Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1CombinedChartLayerSchemaVariant3ColorsSettings | None = None


class WizardV1CombinedChartLayerSchemaVariant3Labels(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel5] | None = Field(
        default=None, description="Fields whose values are displayed as data labels."
    )
    settings: WizardV1CombinedChartLayerSchemaVariant3LabelsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant1X(APIModel):
    """X-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields placed on the X-axis."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant1XSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant1Y(APIModel):
    """Primary Y-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Fields placed on the primary Y-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: WizardV1ConfigSchemaVisualizationVariant1YSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant1Y2(APIModel):
    """Secondary Y-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Fields placed on the secondary Y-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: WizardV1ConfigSchemaVisualizationVariant1Y2Settings | None = None


class WizardV1ConfigSchemaVisualizationVariant1Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant1ColorsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant1Shapes(APIModel):
    """Line shape configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for line encoding."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant1ShapesSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant1Labels(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel5] | None = Field(
        default=None, description="Fields whose values are displayed as data labels."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant1LabelsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant1Segments(APIModel):
    """Segmentation configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used to split the chart into segments."
    )


class WizardV1ConfigSchemaVisualizationVariant2X(APIModel):
    """X-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields placed on the X-axis."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant2XSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant2Y(APIModel):
    """Y-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Fields placed on the Y-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: WizardV1ConfigSchemaVisualizationVariant2YSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant2Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant2ColorsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant2Labels(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel5] | None = Field(
        default=None, description="Fields whose values are displayed as data labels."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant2LabelsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant2Segments(APIModel):
    """Segmentation configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used to split the chart into segments."
    )


class WizardV1ConfigSchemaVisualizationVariant3X(APIModel):
    """X-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields placed on the X-axis."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant3XSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant3Y(APIModel):
    """Y-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Fields placed on the Y-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: WizardV1ConfigSchemaVisualizationVariant3YSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant3Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant3ColorsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant3Segments(APIModel):
    """Segmentation configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used to split the chart into segments."
    )


class WizardV1ConfigSchemaVisualizationVariant3Labels(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel5] | None = Field(
        default=None, description="Fields whose values are displayed as data labels."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant3LabelsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant4X(APIModel):
    """X-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields placed on the X-axis."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant4XSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant4Y(APIModel):
    """Y-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Fields placed on the Y-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: WizardV1ConfigSchemaVisualizationVariant4YSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant4Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant4ColorsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant4Labels(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel5] | None = Field(
        default=None, description="Fields whose values are displayed as data labels."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant4LabelsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant4Segments(APIModel):
    """Segmentation configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used to split the chart into segments."
    )


class WizardV1ConfigSchemaVisualizationVariant5X(APIModel):
    """X-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields placed on the X-axis."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant5XSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant5Y(APIModel):
    """Y-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Fields placed on the Y-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: WizardV1ConfigSchemaVisualizationVariant5YSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant5Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant5ColorsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant5Labels(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel5] | None = Field(
        default=None, description="Fields whose values are displayed as data labels."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant5LabelsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant5Segments(APIModel):
    """Segmentation configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used to split the chart into segments."
    )


class WizardV1ConfigSchemaVisualizationVariant6X(APIModel):
    """X-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Fields placed on the X-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: WizardV1ConfigSchemaVisualizationVariant6XSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant6Y(APIModel):
    """Y-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields placed on the Y-axis."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant6YSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant6Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant6ColorsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant6Labels(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel5] | None = Field(
        default=None, description="Fields whose values are displayed as data labels."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant6LabelsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant7X(APIModel):
    """X-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Fields placed on the X-axis. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: WizardV1ConfigSchemaVisualizationVariant7XSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant7Y(APIModel):
    """Y-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields placed on the Y-axis."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant7YSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant7Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant7ColorsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant7Labels(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel5] | None = Field(
        default=None, description="Fields whose values are displayed as data labels."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant7LabelsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant8Dimensions(APIModel):
    """Dimension configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Dimensions used to create funnel stages."
    )


class WizardV1ConfigSchemaVisualizationVariant8Measures(APIModel):
    """Measure configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Measures used to size funnel stages. Measures only: a dimension placed here needs an aggregation.",
    )


class WizardV1ConfigSchemaVisualizationVariant8Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used to assign stage colors."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant8ColorsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant8Labels(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel5] | None = Field(
        default=None, description="Fields whose values are displayed as stage labels."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant8LabelsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant9X(APIModel):
    """X-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields placed on the X-axis."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant9XSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant9Y(APIModel):
    """Y-axis configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields placed on the Y-axis."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant9YSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant9Points(APIModel):
    """Point grouping configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Fields used to group points and add tooltip information.",
    )


class WizardV1ConfigSchemaVisualizationVariant9Size(APIModel):
    """Point size configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Fields used to determine point sizes. Measures only: a dimension placed here needs an aggregation.",
    )
    settings: WizardV1ConfigSchemaVisualizationVariant9SizeSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant9Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant9ColorsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant9Shapes(APIModel):
    """Marker shape configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for shape encoding."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant9ShapesSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant10Dimensions(APIModel):
    """Dimension configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Dimensions used to create pie slices."
    )


class WizardV1ConfigSchemaVisualizationVariant10Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant10ColorsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant10Measures(APIModel):
    """Measure configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Measures used to determine slice sizes. Measures only: a dimension placed here needs an aggregation.",
    )


class WizardV1ConfigSchemaVisualizationVariant10Labels(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel5] | None = Field(
        default=None, description="Fields whose values are displayed as slice labels."
    )


class WizardV1ConfigSchemaVisualizationVariant11Dimensions(APIModel):
    """Dimension configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Dimensions used to create pie slices."
    )


class WizardV1ConfigSchemaVisualizationVariant11Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for color encoding."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant11ColorsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant11Measures(APIModel):
    """Measure configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Measures used to determine slice sizes. Measures only: a dimension placed here needs an aggregation.",
    )


class WizardV1ConfigSchemaVisualizationVariant11Labels(APIModel):
    """Data label configuration."""

    items: list[WizardLabelsItemSchemaModel5] | None = Field(
        default=None, description="Fields whose values are displayed as slice labels."
    )


class WizardV1ConfigSchemaVisualizationVariant12Measures(APIModel):
    """Measure configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Measures displayed by the metric. Measures only: a dimension placed here needs an aggregation.",
    )


class WizardV1ConfigSchemaVisualizationVariant13Dimensions(APIModel):
    """Dimension configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Dimensions used to group treemap nodes."
    )


class WizardV1ConfigSchemaVisualizationVariant13Measures(APIModel):
    """Measure configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Measures used to size treemap nodes. Measures only: a dimension placed here needs an aggregation.",
    )


class WizardV1ConfigSchemaVisualizationVariant13Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used to assign node colors."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant13ColorsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant14Columns(APIModel):
    """Column configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields displayed as table columns."
    )


class WizardV1ConfigSchemaVisualizationVariant14Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for conditional coloring."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant14ColorsSettings | None = None


class WizardV1ConfigSchemaVisualizationVariant15Columns(APIModel):
    """Column configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Dimensions displayed as pivot columns."
    )


class WizardV1ConfigSchemaVisualizationVariant15Rows(APIModel):
    """Row configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Dimensions displayed as pivot rows."
    )


class WizardV1ConfigSchemaVisualizationVariant15Measures(APIModel):
    """Measure configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None,
        description="Measures displayed in pivot cells. Measures only: a dimension placed here needs an aggregation.",
    )


class WizardV1ConfigSchemaVisualizationVariant15Colors(APIModel):
    """Color configuration."""

    items: list[WizardFieldSchema] | None = Field(
        default=None, description="Fields used for conditional coloring."
    )
    settings: WizardV1ConfigSchemaVisualizationVariant15ColorsSettings | None = None


class WizardV1GeolayerLayerSchemaVariant1(APIModel):
    type: Literal["geopoint"] = Field(..., description="Geopoint layer type.")
    layer_settings: WizardV1GeolayerLayerSchemaVariant1LayerSettings | None = Field(
        default=None, alias="layerSettings"
    )
    points: WizardV1GeolayerLayerSchemaVariant1Points | None = None
    size: WizardV1GeolayerLayerSchemaVariant1Size | None = None
    colors: WizardV1GeolayerLayerSchemaVariant1Colors | None = None
    labels: WizardV1GeolayerLayerSchemaVariant1Labels | None = None
    tooltip: WizardV1GeolayerLayerSchemaVariant1Tooltip | None = None
    filters: WizardV1GeolayerLayerSchemaVariant1Filters | None = None


class WizardV1GeolayerLayerSchemaVariant2(APIModel):
    layer_settings: WizardV1GeolayerLayerSchemaVariant2LayerSettings | None = Field(
        default=None, alias="layerSettings"
    )
    points: WizardV1GeolayerLayerSchemaVariant2Points | None = None
    size: WizardV1GeolayerLayerSchemaVariant2Size | None = None
    colors: WizardV1GeolayerLayerSchemaVariant2Colors | None = None
    labels: WizardV1GeolayerLayerSchemaVariant2Labels | None = None
    tooltip: WizardV1GeolayerLayerSchemaVariant2Tooltip | None = None
    filters: WizardV1GeolayerLayerSchemaVariant2Filters | None = None
    type: Literal["geopoint-with-cluster"] = Field(
        ..., description="Clustered geopoint layer type."
    )


class WizardV1GeolayerLayerSchemaVariant3(APIModel):
    type: Literal["polyline"] = Field(..., description="Geopolyline layer type.")
    layer_settings: WizardV1GeolayerLayerSchemaVariant3LayerSettings | None = Field(
        default=None, alias="layerSettings"
    )
    polylines: WizardV1GeolayerLayerSchemaVariant3Polylines | None = None
    measures: WizardV1GeolayerLayerSchemaVariant3Measures | None = None
    grouping: WizardV1GeolayerLayerSchemaVariant3Grouping | None = None
    colors: WizardV1GeolayerLayerSchemaVariant3Colors | None = None
    sort: WizardV1GeolayerLayerSchemaVariant3Sort | None = None
    filters: WizardV1GeolayerLayerSchemaVariant3Filters | None = None


class WizardV1GeolayerLayerSchemaVariant4(APIModel):
    type: Literal["geopolygon"] = Field(..., description="Geopolygon layer type.")
    layer_settings: WizardV1GeolayerLayerSchemaVariant4LayerSettings | None = Field(
        default=None, alias="layerSettings"
    )
    polygons: WizardV1GeolayerLayerSchemaVariant4Polygons | None = None
    colors: WizardV1GeolayerLayerSchemaVariant4Colors | None = None
    tooltip: WizardV1GeolayerLayerSchemaVariant4Tooltip | None = None
    filters: WizardV1GeolayerLayerSchemaVariant4Filters | None = None


class WizardV1GeolayerLayerSchemaVariant5(APIModel):
    type: Literal["heatmap"] = Field(..., description="Geo heatmap layer type.")
    layer_settings: WizardV1GeolayerLayerSchemaVariant5LayerSettings | None = Field(
        default=None, alias="layerSettings"
    )
    points: WizardV1GeolayerLayerSchemaVariant5Points | None = None
    colors: WizardV1GeolayerLayerSchemaVariant5Colors | None = None
    filters: WizardV1GeolayerLayerSchemaVariant5Filters | None = None


class WizardV1CombinedChartLayerSchemaVariant1(APIModel):
    type: Literal["line"] = Field(..., description="Line layer type.")
    layer_settings: WizardV1CombinedChartLayerSchemaVariant1LayerSettings | None = Field(
        default=None, alias="layerSettings"
    )
    x: WizardV1CombinedChartLayerSchemaVariant1X | None = None
    y: WizardV1CombinedChartLayerSchemaVariant1Y | None = None
    y2: WizardV1CombinedChartLayerSchemaVariant1Y2 | None = None
    colors: WizardV1CombinedChartLayerSchemaVariant1Colors | None = None
    shapes: WizardV1CombinedChartLayerSchemaVariant1Shapes | None = None
    labels: WizardV1CombinedChartLayerSchemaVariant1Labels | None = None
    sort: WizardV1CombinedChartLayerSchemaVariant1Sort | None = None


class WizardV1CombinedChartLayerSchemaVariant2(APIModel):
    type: Literal["column"] = Field(..., description="Column layer type.")
    layer_settings: WizardV1CombinedChartLayerSchemaVariant2LayerSettings | None = Field(
        default=None, alias="layerSettings"
    )
    x: WizardV1CombinedChartLayerSchemaVariant2X | None = None
    y: WizardV1CombinedChartLayerSchemaVariant2Y | None = None
    colors: WizardV1CombinedChartLayerSchemaVariant2Colors | None = None
    labels: WizardV1CombinedChartLayerSchemaVariant2Labels | None = None
    sort: WizardV1CombinedChartLayerSchemaVariant2Sort | None = None


class WizardV1CombinedChartLayerSchemaVariant3(APIModel):
    type: Literal["area"] = Field(..., description="Area layer type.")
    layer_settings: WizardV1CombinedChartLayerSchemaVariant3LayerSettings | None = Field(
        default=None, alias="layerSettings"
    )
    x: WizardV1CombinedChartLayerSchemaVariant3X | None = None
    y: WizardV1CombinedChartLayerSchemaVariant3Y | None = None
    colors: WizardV1CombinedChartLayerSchemaVariant3Colors | None = None
    labels: WizardV1CombinedChartLayerSchemaVariant3Labels | None = None
    sort: WizardV1CombinedChartLayerSchemaVariant3Sort | None = None


class WizardV1ConfigSchemaVisualizationVariant1(APIModel):
    type: Literal["line"] = Field(..., description="Line visualization type.")
    chart_settings: WizardV1ConfigSchemaVisualizationVariant1ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )
    x: WizardV1ConfigSchemaVisualizationVariant1X | None = None
    y: WizardV1ConfigSchemaVisualizationVariant1Y | None = None
    y2: WizardV1ConfigSchemaVisualizationVariant1Y2 | None = None
    colors: WizardV1ConfigSchemaVisualizationVariant1Colors | None = None
    shapes: WizardV1ConfigSchemaVisualizationVariant1Shapes | None = None
    labels: WizardV1ConfigSchemaVisualizationVariant1Labels | None = None
    sort: WizardV1ConfigSchemaVisualizationVariant1Sort | None = None
    segments: WizardV1ConfigSchemaVisualizationVariant1Segments | None = None


class WizardV1ConfigSchemaVisualizationVariant2(APIModel):
    type: Literal["column"] = Field(..., description="Column visualization type.")
    chart_settings: WizardV1ConfigSchemaVisualizationVariant2ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )
    x: WizardV1ConfigSchemaVisualizationVariant2X | None = None
    y: WizardV1ConfigSchemaVisualizationVariant2Y | None = None
    colors: WizardV1ConfigSchemaVisualizationVariant2Colors | None = None
    labels: WizardV1ConfigSchemaVisualizationVariant2Labels | None = None
    sort: WizardV1ConfigSchemaVisualizationVariant2Sort | None = None
    segments: WizardV1ConfigSchemaVisualizationVariant2Segments | None = None


class WizardV1ConfigSchemaVisualizationVariant3(APIModel):
    chart_settings: WizardV1ConfigSchemaVisualizationVariant3ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )
    x: WizardV1ConfigSchemaVisualizationVariant3X | None = None
    y: WizardV1ConfigSchemaVisualizationVariant3Y | None = None
    colors: WizardV1ConfigSchemaVisualizationVariant3Colors | None = None
    sort: WizardV1ConfigSchemaVisualizationVariant3Sort | None = None
    segments: WizardV1ConfigSchemaVisualizationVariant3Segments | None = None
    type: Literal["column100p"] = Field(..., description="Normalized column visualization type.")
    labels: WizardV1ConfigSchemaVisualizationVariant3Labels | None = None


class WizardV1ConfigSchemaVisualizationVariant4(APIModel):
    type: Literal["area"] = Field(..., description="Area visualization type.")
    chart_settings: WizardV1ConfigSchemaVisualizationVariant4ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )
    x: WizardV1ConfigSchemaVisualizationVariant4X | None = None
    y: WizardV1ConfigSchemaVisualizationVariant4Y | None = None
    colors: WizardV1ConfigSchemaVisualizationVariant4Colors | None = None
    labels: WizardV1ConfigSchemaVisualizationVariant4Labels | None = None
    sort: WizardV1ConfigSchemaVisualizationVariant4Sort | None = None
    segments: WizardV1ConfigSchemaVisualizationVariant4Segments | None = None


class WizardV1ConfigSchemaVisualizationVariant5(APIModel):
    x: WizardV1ConfigSchemaVisualizationVariant5X | None = None
    y: WizardV1ConfigSchemaVisualizationVariant5Y | None = None
    colors: WizardV1ConfigSchemaVisualizationVariant5Colors | None = None
    labels: WizardV1ConfigSchemaVisualizationVariant5Labels | None = None
    sort: WizardV1ConfigSchemaVisualizationVariant5Sort | None = None
    segments: WizardV1ConfigSchemaVisualizationVariant5Segments | None = None
    type: Literal["area100p"] = Field(..., description="Normalized area visualization type.")
    chart_settings: WizardV1ConfigSchemaVisualizationVariant5ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )


class WizardV1ConfigSchemaVisualizationVariant6(APIModel):
    type: Literal["bar"] = Field(..., description="Bar visualization type.")
    chart_settings: WizardV1ConfigSchemaVisualizationVariant6ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )
    x: WizardV1ConfigSchemaVisualizationVariant6X | None = None
    y: WizardV1ConfigSchemaVisualizationVariant6Y | None = None
    colors: WizardV1ConfigSchemaVisualizationVariant6Colors | None = None
    labels: WizardV1ConfigSchemaVisualizationVariant6Labels | None = None
    sort: WizardV1ConfigSchemaVisualizationVariant6Sort | None = None


class WizardV1ConfigSchemaVisualizationVariant7(APIModel):
    chart_settings: WizardV1ConfigSchemaVisualizationVariant7ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )
    x: WizardV1ConfigSchemaVisualizationVariant7X | None = None
    y: WizardV1ConfigSchemaVisualizationVariant7Y | None = None
    colors: WizardV1ConfigSchemaVisualizationVariant7Colors | None = None
    sort: WizardV1ConfigSchemaVisualizationVariant7Sort | None = None
    type: Literal["bar100p"] = Field(..., description="Normalized bar visualization type.")
    labels: WizardV1ConfigSchemaVisualizationVariant7Labels | None = None


class WizardV1ConfigSchemaVisualizationVariant8(APIModel):
    type: Literal["funnel"] = Field(..., description="Funnel visualization type.")
    chart_settings: WizardV1ConfigSchemaVisualizationVariant8ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )
    dimensions: WizardV1ConfigSchemaVisualizationVariant8Dimensions | None = None
    measures: WizardV1ConfigSchemaVisualizationVariant8Measures | None = None
    colors: WizardV1ConfigSchemaVisualizationVariant8Colors | None = None
    labels: WizardV1ConfigSchemaVisualizationVariant8Labels | None = None
    sort: WizardV1ConfigSchemaVisualizationVariant8Sort | None = None


class WizardV1ConfigSchemaVisualizationVariant9(APIModel):
    type: Literal["scatter"] = Field(..., description="Scatter visualization type.")
    chart_settings: WizardV1ConfigSchemaVisualizationVariant9ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )
    x: WizardV1ConfigSchemaVisualizationVariant9X | None = None
    y: WizardV1ConfigSchemaVisualizationVariant9Y | None = None
    points: WizardV1ConfigSchemaVisualizationVariant9Points | None = None
    size: WizardV1ConfigSchemaVisualizationVariant9Size | None = None
    colors: WizardV1ConfigSchemaVisualizationVariant9Colors | None = None
    shapes: WizardV1ConfigSchemaVisualizationVariant9Shapes | None = None
    sort: WizardV1ConfigSchemaVisualizationVariant9Sort | None = None


class WizardV1ConfigSchemaVisualizationVariant10(APIModel):
    type: Literal["pie"] = Field(..., description="Pie visualization type.")
    chart_settings: WizardV1ConfigSchemaVisualizationVariant10ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )
    dimensions: WizardV1ConfigSchemaVisualizationVariant10Dimensions | None = None
    colors: WizardV1ConfigSchemaVisualizationVariant10Colors | None = None
    measures: WizardV1ConfigSchemaVisualizationVariant10Measures | None = None
    sort: WizardV1ConfigSchemaVisualizationVariant10Sort | None = None
    labels: WizardV1ConfigSchemaVisualizationVariant10Labels | None = None


class WizardV1ConfigSchemaVisualizationVariant11(APIModel):
    dimensions: WizardV1ConfigSchemaVisualizationVariant11Dimensions | None = None
    colors: WizardV1ConfigSchemaVisualizationVariant11Colors | None = None
    measures: WizardV1ConfigSchemaVisualizationVariant11Measures | None = None
    sort: WizardV1ConfigSchemaVisualizationVariant11Sort | None = None
    labels: WizardV1ConfigSchemaVisualizationVariant11Labels | None = None
    type: Literal["donut"] = Field(..., description="Donut visualization type.")
    chart_settings: WizardV1ConfigSchemaVisualizationVariant11ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )


class WizardV1ConfigSchemaVisualizationVariant12(APIModel):
    type: Literal["metric"] = Field(..., description="Metric visualization type.")
    is_markup: bool | None = Field(
        default=None,
        alias="isMarkup",
        description="Whether the metric value uses the markup data type.",
    )
    chart_settings: WizardV1ConfigSchemaVisualizationVariant12ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )
    measures: WizardV1ConfigSchemaVisualizationVariant12Measures | None = None
    colors: WizardV1ConfigSchemaVisualizationVariant12Colors | None = None


class WizardV1ConfigSchemaVisualizationVariant13(APIModel):
    type: Literal["treemap"] = Field(..., description="Treemap visualization type.")
    chart_settings: WizardV1ConfigSchemaVisualizationVariant13ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )
    dimensions: WizardV1ConfigSchemaVisualizationVariant13Dimensions | None = None
    measures: WizardV1ConfigSchemaVisualizationVariant13Measures | None = None
    colors: WizardV1ConfigSchemaVisualizationVariant13Colors | None = None


class WizardV1ConfigSchemaVisualizationVariant14(APIModel):
    type: Literal["flatTable"] = Field(..., description="Flat table visualization type.")
    chart_settings: WizardV1ConfigSchemaVisualizationVariant14ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )
    columns: WizardV1ConfigSchemaVisualizationVariant14Columns | None = None
    colors: WizardV1ConfigSchemaVisualizationVariant14Colors | None = None
    sort: WizardV1ConfigSchemaVisualizationVariant14Sort | None = None


class WizardV1ConfigSchemaVisualizationVariant15(APIModel):
    type: Literal["pivotTable"] = Field(..., description="Pivot table visualization type.")
    chart_settings: WizardV1ConfigSchemaVisualizationVariant15ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )
    columns: WizardV1ConfigSchemaVisualizationVariant15Columns | None = None
    rows: WizardV1ConfigSchemaVisualizationVariant15Rows | None = None
    measures: WizardV1ConfigSchemaVisualizationVariant15Measures | None = None
    colors: WizardV1ConfigSchemaVisualizationVariant15Colors | None = None
    sort: WizardV1ConfigSchemaVisualizationVariant15Sort | None = None


class WizardV1GeolayerLayerSchema(
    RootModel[
        WizardV1GeolayerLayerSchemaVariant1
        | WizardV1GeolayerLayerSchemaVariant2
        | WizardV1GeolayerLayerSchemaVariant3
        | WizardV1GeolayerLayerSchemaVariant4
        | WizardV1GeolayerLayerSchemaVariant5
        | shared.OtherKindByType
    ]
):
    root: (
        WizardV1GeolayerLayerSchemaVariant1
        | WizardV1GeolayerLayerSchemaVariant2
        | WizardV1GeolayerLayerSchemaVariant3
        | WizardV1GeolayerLayerSchemaVariant4
        | WizardV1GeolayerLayerSchemaVariant5
        | shared.OtherKindByType
    )


class WizardV1CombinedChartLayerSchema(
    RootModel[
        WizardV1CombinedChartLayerSchemaVariant1
        | WizardV1CombinedChartLayerSchemaVariant2
        | WizardV1CombinedChartLayerSchemaVariant3
        | shared.OtherKindByType
    ]
):
    root: (
        WizardV1CombinedChartLayerSchemaVariant1
        | WizardV1CombinedChartLayerSchemaVariant2
        | WizardV1CombinedChartLayerSchemaVariant3
        | shared.OtherKindByType
    )


class WizardV1ConfigSchemaVisualizationVariant16(APIModel):
    type: Literal["geolayer"] = Field(..., description="Geolayer visualization type.")
    chart_settings: WizardV1ConfigSchemaVisualizationVariant16ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )
    layers: list[WizardV1GeolayerLayerSchema] | None = Field(
        default=None, description="Layers included in the map."
    )
    selected_layer_id: str | None = Field(
        default=None,
        alias="selectedLayerId",
        description="Identifier of the currently selected layer.",
    )


class WizardV1ConfigSchemaVisualizationVariant17(APIModel):
    type: Literal["combined-chart"] = Field(..., description="Combined chart visualization type.")
    chart_settings: WizardV1ConfigSchemaVisualizationVariant17ChartSettings | None = Field(
        default=None, alias="chartSettings"
    )
    layers: list[WizardV1CombinedChartLayerSchema] | None = Field(
        default=None, description="Layers included in the combined chart."
    )
    selected_layer_id: str | None = Field(
        default=None,
        alias="selectedLayerId",
        description="Identifier of the currently selected layer.",
    )


class WizardV1ConfigSchema(APIModel):
    sources: WizardV1ConfigSchemaSources | None = None
    visualization: (
        WizardV1ConfigSchemaVisualizationVariant1
        | WizardV1ConfigSchemaVisualizationVariant2
        | WizardV1ConfigSchemaVisualizationVariant3
        | WizardV1ConfigSchemaVisualizationVariant4
        | WizardV1ConfigSchemaVisualizationVariant5
        | WizardV1ConfigSchemaVisualizationVariant6
        | WizardV1ConfigSchemaVisualizationVariant7
        | WizardV1ConfigSchemaVisualizationVariant8
        | WizardV1ConfigSchemaVisualizationVariant9
        | WizardV1ConfigSchemaVisualizationVariant10
        | WizardV1ConfigSchemaVisualizationVariant11
        | WizardV1ConfigSchemaVisualizationVariant12
        | WizardV1ConfigSchemaVisualizationVariant13
        | WizardV1ConfigSchemaVisualizationVariant14
        | WizardV1ConfigSchemaVisualizationVariant15
        | WizardV1ConfigSchemaVisualizationVariant16
        | WizardV1ConfigSchemaVisualizationVariant17
        | shared.OtherKindByType
        | None
    ) = Field(default=None, description="Chart visualization configuration.")


class WizardV1(APIModel):
    version: Literal[1] = Field(..., description="Entry API version.")
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the entry."
    )
    key: str | None = Field(default=None, description="Key identifier of the entry.")
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
        default=None, alias="revId", description="Version ID for the Wizard chart."
    )
    saved_id: str | None = Field(default=None, alias="savedId", description="Saved version ID.")
    published_id: str | None = Field(
        default=None, alias="publishedId", description="Published version ID."
    )
    tenant_id: str | None = Field(default=None, alias="tenantId", description="Tenant ID.")
    hidden: bool | None = Field(default=None, description="Indicates if the entry is hidden.")
    public: bool | None = Field(default=None, description="Indicates if the entry is public.")
    workbook_id: str | None = Field(
        default=None,
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
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    links: dict[str, Any] | None = Field(default=None, description="Link information.")
    annotation: WizardV1Annotation | None = None
    data: WizardV1ConfigSchema | None = None


class GetWizardChartV1Result(APIModel):
    entry: WizardV1 | None = None
    is_favorite: bool | None = Field(
        default=None,
        alias="isFavorite",
        description="Indicates if the chart is marked as favorite.",
    )
    permissions: GetWizardChartV1ResultPermissions | None = None


class UpdateWizardV1Result(APIModel):
    entry: WizardV1 | None = None


class UpdateWizardV1Args(RequestBody):
    chart_id: str = Field(..., alias="chartId")
    annotation: shared.EntryAnnotationArg | None = None
    mode: shared.EntryUpdateMode
    rev_id: str | None = Field(default=None, alias="revId")
    data: WizardV1ConfigSchema


class CreateWizardChartV1Result(APIModel):
    entry: WizardV1 | None = None


class CreateWizardChartV1Args(EntryLocationIdentifiers):
    data: WizardV1ConfigSchema | None = None
    annotation: shared.EntryAnnotationArg | None = None
