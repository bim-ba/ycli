# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from typing import Any, Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class EntryScope(
    RootModel[
        Literal[
            "dash",
            "report",
            "widget",
            "dataset",
            "folder",
            "connection",
            "compute",
            "artifact",
            "sql_query",
        ]
        | str
    ],
    hide_input_in_errors=True,
):
    root: (
        Literal[
            "dash",
            "report",
            "widget",
            "dataset",
            "folder",
            "connection",
            "compute",
            "artifact",
            "sql_query",
        ]
        | str
    ) = Field(..., description="Type of the entry, e.g. `dash` — dashboard, `widget` — chart, etc.")


class DashStringDefaultValueV2(RootModel[str | list[str]], hide_input_in_errors=True):
    root: str | list[str] = Field(
        ...,
        description="A dashboard parameter value represented by one or multiple strings.",
    )


class DashColorByThemeV2(APIModel):
    light: str | None = Field(default=None, description="Color for the light theme.")
    dark: str | None = Field(default=None, description="Color for the dark theme.")


class DashControlSourceExternalV2(APIModel):
    """External control source."""

    chart_id: str | None = Field(
        default=None, alias="chartId", description="Source chart identifier."
    )


class DashLayoutItemV2(APIModel):
    i: str | None = Field(default=None, description="Dashboard item identifier.")
    h: int | float | None = Field(default=None, description="Item height in grid units.")
    w: int | float | None = Field(default=None, description="Item width in grid units.")
    x: int | float | None = Field(default=None, description="Horizontal grid position.")
    y: int | float | None = Field(default=None, description="Vertical grid position.")
    parent: str | None = Field(default=None, description="Parent item identifier.")


class DashConnectionV2(APIModel):
    from_: str | None = Field(default=None, alias="from", description="Source widget identifier.")
    to: str | None = Field(default=None, description="Target widget identifier.")
    kind: Literal["ignore"] = Field(..., description="Connection type.")


class EntryPermissions(APIModel):
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


class EntryBranch(RootModel[Literal["saved", "published"] | str], hide_input_in_errors=True):
    root: Literal["saved", "published"] | str = Field(
        ..., description="Entry branch: saved or published."
    )


class EntryAnnotationArg(APIModel):
    description: str | None = Field(default=None, description="Description of the entry.")


class EntryUpdateMode(RootModel[Literal["save", "publish"] | str], hide_input_in_errors=True):
    root: Literal["save", "publish"] | str = Field(..., description="Entry update mode.")


class WorkbookTransferProcessStatus(
    RootModel[Literal["pending", "success", "error"] | str], hide_input_in_errors=True
):
    root: Literal["pending", "success", "error"] | str = Field(
        ..., description="Status of the workbook transfer process."
    )


class WorkbookTransferNotificationLevel(
    RootModel[Literal["info", "warning", "critical"] | str], hide_input_in_errors=True
):
    root: Literal["info", "warning", "critical"] | str = Field(
        ..., description="Severity level of the workbook transfer notification."
    )


class WorkbookTransferNotification(APIModel):
    entry_id: str | None = Field(
        default=None,
        alias="entryId",
        description="ID of the entry associated with the notification.",
    )
    scope: EntryScope | None = None
    code: str | None = Field(default=None, description="Notification code.")
    message: str | None = Field(default=None, description="Notification message.")
    level: WorkbookTransferNotificationLevel | None = None
    details: Any | None = Field(default=None, description="Additional notification details.")


class OtherKind(APIModel):
    """A kind the specification does not describe: kept as it came."""


class DatalensOperationCreatedAt(APIModel):
    """Operation creation timestamp."""

    seconds: str | None = Field(default=None, description="Number of seconds since the Unix epoch.")
    nanos: int | float | None = Field(
        default=None, description="Fractional seconds in nanoseconds."
    )


class DatalensOperationModifiedAt(APIModel):
    """Operation last modification timestamp."""

    seconds: str | None = Field(default=None, description="Number of seconds since the Unix epoch.")
    nanos: int | float | None = Field(
        default=None, description="Fractional seconds in nanoseconds."
    )


class DatalensOperationMetadata(APIModel):
    """Metadata associated with the operation."""


class DashControlSourceDatasetV2Variant1(APIModel):
    dataset_id: str | None = Field(
        default=None, alias="datasetId", description="Source dataset identifier."
    )
    dataset_field_id: str | None = Field(
        default=None,
        alias="datasetFieldId",
        description="Source dataset field identifier.",
    )
    field_type: (
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
    ) = Field(default=None, alias="fieldType", description="Source dataset field data type.")
    dataset_field_type: Literal["DIMENSION", "MEASURE", "PSEUDO", "PARAMETER"] | str | None = Field(
        default=None, alias="datasetFieldType", description="Source dataset field type."
    )
    required: bool | None = Field(
        default=None, description="Whether the control value is required."
    )
    show_hint: bool | None = Field(
        default=None, alias="showHint", description="Whether to show the control hint."
    )
    show_title: bool | None = Field(
        default=None,
        alias="showTitle",
        description="Whether to show the control title.",
    )
    hint: str | None = Field(default=None, description="Control hint text.")
    accent_type: Literal["info"] | None = Field(
        default=None, alias="accentType", description="Control accent style."
    )
    inner_title: str | None = Field(
        default=None,
        alias="innerTitle",
        description="Title displayed inside the control.",
    )
    show_inner_title: bool | None = Field(
        default=None,
        alias="showInnerTitle",
        description="Whether to show the title inside the control.",
    )
    operation: (
        Literal[
            "IN",
            "NIN",
            "EQ",
            "NE",
            "GT",
            "LT",
            "GTE",
            "LTE",
            "ISNULL",
            "ISNOTNULL",
            "ISTARTSWITH",
            "STARTSWITH",
            "IENDSWITH",
            "ENDSWITH",
            "ICONTAINS",
            "CONTAINS",
            "NOTICONTAINS",
            "NOTCONTAINS",
            "BETWEEN",
            "LENEQ",
            "LENGT",
            "LENGTE",
            "LENLT",
            "LENLTE",
            "NO_SELECTED_VALUES",
        ]
        | str
        | None
    ) = Field(default=None, description="Filtering operation.")
    title_placement: Literal["hide", "left", "top"] | str | None = Field(
        default=None, alias="titlePlacement", description="Control title placement."
    )
    multiselectable: bool | None = Field(
        default=None, description="Whether multiple values can be selected."
    )
    element_type: Literal["select"] = Field(
        ..., alias="elementType", description="Select control type."
    )
    default_value: str | list[str] | None = Field(
        default=None,
        alias="defaultValue",
        description="Default selected value or values.",
    )


class DashControlSourceDatasetV2Variant2(APIModel):
    dataset_id: str | None = Field(
        default=None, alias="datasetId", description="Source dataset identifier."
    )
    dataset_field_id: str | None = Field(
        default=None,
        alias="datasetFieldId",
        description="Source dataset field identifier.",
    )
    field_type: (
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
        default=None, alias="fieldType", description="Type of the field used by the date control."
    )
    dataset_field_type: Literal["DIMENSION", "MEASURE", "PSEUDO", "PARAMETER"] | str | None = Field(
        default=None, alias="datasetFieldType", description="Source dataset field type."
    )
    required: bool | None = Field(
        default=None, description="Whether the control value is required."
    )
    show_hint: bool | None = Field(
        default=None, alias="showHint", description="Whether to show the control hint."
    )
    show_title: bool | None = Field(
        default=None,
        alias="showTitle",
        description="Whether to show the control title.",
    )
    hint: str | None = Field(default=None, description="Control hint text.")
    accent_type: Literal["info"] | None = Field(
        default=None, alias="accentType", description="Control accent style."
    )
    inner_title: str | None = Field(
        default=None,
        alias="innerTitle",
        description="Title displayed inside the control.",
    )
    show_inner_title: bool | None = Field(
        default=None,
        alias="showInnerTitle",
        description="Whether to show the title inside the control.",
    )
    operation: (
        Literal[
            "IN",
            "NIN",
            "EQ",
            "NE",
            "GT",
            "LT",
            "GTE",
            "LTE",
            "ISNULL",
            "ISNOTNULL",
            "ISTARTSWITH",
            "STARTSWITH",
            "IENDSWITH",
            "ENDSWITH",
            "ICONTAINS",
            "CONTAINS",
            "NOTICONTAINS",
            "NOTCONTAINS",
            "BETWEEN",
            "LENEQ",
            "LENGT",
            "LENGTE",
            "LENLT",
            "LENLTE",
            "NO_SELECTED_VALUES",
        ]
        | str
        | None
    ) = Field(default=None, description="Filtering operation.")
    title_placement: Literal["hide", "left", "top"] | str | None = Field(
        default=None, alias="titlePlacement", description="Control title placement."
    )
    is_range: bool | None = Field(
        default=None,
        alias="isRange",
        description="Whether the control selects a date range.",
    )
    element_type: Literal["date"] = Field(
        ..., alias="elementType", description="Date control type."
    )
    default_value: str | None = Field(
        default=None, alias="defaultValue", description="Default date value."
    )


class DashControlSourceDatasetV2Variant3(APIModel):
    dataset_id: str | None = Field(
        default=None, alias="datasetId", description="Source dataset identifier."
    )
    dataset_field_id: str | None = Field(
        default=None,
        alias="datasetFieldId",
        description="Source dataset field identifier.",
    )
    field_type: (
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
    ) = Field(default=None, alias="fieldType", description="Source dataset field data type.")
    dataset_field_type: Literal["DIMENSION", "MEASURE", "PSEUDO", "PARAMETER"] | str | None = Field(
        default=None, alias="datasetFieldType", description="Source dataset field type."
    )
    required: bool | None = Field(
        default=None, description="Whether the control value is required."
    )
    show_hint: bool | None = Field(
        default=None, alias="showHint", description="Whether to show the control hint."
    )
    show_title: bool | None = Field(
        default=None,
        alias="showTitle",
        description="Whether to show the control title.",
    )
    hint: str | None = Field(default=None, description="Control hint text.")
    accent_type: Literal["info"] | None = Field(
        default=None, alias="accentType", description="Control accent style."
    )
    inner_title: str | None = Field(
        default=None,
        alias="innerTitle",
        description="Title displayed inside the control.",
    )
    show_inner_title: bool | None = Field(
        default=None,
        alias="showInnerTitle",
        description="Whether to show the title inside the control.",
    )
    operation: (
        Literal[
            "IN",
            "NIN",
            "EQ",
            "NE",
            "GT",
            "LT",
            "GTE",
            "LTE",
            "ISNULL",
            "ISNOTNULL",
            "ISTARTSWITH",
            "STARTSWITH",
            "IENDSWITH",
            "ENDSWITH",
            "ICONTAINS",
            "CONTAINS",
            "NOTICONTAINS",
            "NOTCONTAINS",
            "BETWEEN",
            "LENEQ",
            "LENGT",
            "LENGTE",
            "LENLT",
            "LENLTE",
            "NO_SELECTED_VALUES",
        ]
        | str
        | None
    ) = Field(default=None, description="Filtering operation.")
    title_placement: Literal["hide", "left", "top"] | str | None = Field(
        default=None, alias="titlePlacement", description="Control title placement."
    )
    element_type: Literal["input"] = Field(
        ..., alias="elementType", description="Input control type."
    )
    default_value: str | None = Field(
        default=None, alias="defaultValue", description="Default input value."
    )


class DashControlSourceDatasetV2Variant4(APIModel):
    dataset_id: str | None = Field(
        default=None, alias="datasetId", description="Source dataset identifier."
    )
    dataset_field_id: str | None = Field(
        default=None,
        alias="datasetFieldId",
        description="Source dataset field identifier.",
    )
    field_type: (
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
    ) = Field(default=None, alias="fieldType", description="Source dataset field data type.")
    dataset_field_type: Literal["DIMENSION", "MEASURE", "PSEUDO", "PARAMETER"] | str | None = Field(
        default=None, alias="datasetFieldType", description="Source dataset field type."
    )
    required: bool | None = Field(
        default=None, description="Whether the control value is required."
    )
    show_hint: bool | None = Field(
        default=None, alias="showHint", description="Whether to show the control hint."
    )
    show_title: bool | None = Field(
        default=None,
        alias="showTitle",
        description="Whether to show the control title.",
    )
    hint: str | None = Field(default=None, description="Control hint text.")
    accent_type: Literal["info"] | None = Field(
        default=None, alias="accentType", description="Control accent style."
    )
    inner_title: str | None = Field(
        default=None,
        alias="innerTitle",
        description="Title displayed inside the control.",
    )
    show_inner_title: bool | None = Field(
        default=None,
        alias="showInnerTitle",
        description="Whether to show the title inside the control.",
    )
    operation: (
        Literal[
            "IN",
            "NIN",
            "EQ",
            "NE",
            "GT",
            "LT",
            "GTE",
            "LTE",
            "ISNULL",
            "ISNOTNULL",
            "ISTARTSWITH",
            "STARTSWITH",
            "IENDSWITH",
            "ENDSWITH",
            "ICONTAINS",
            "CONTAINS",
            "NOTICONTAINS",
            "NOTCONTAINS",
            "BETWEEN",
            "LENEQ",
            "LENGT",
            "LENGTE",
            "LENLT",
            "LENLTE",
            "NO_SELECTED_VALUES",
        ]
        | str
        | None
    ) = Field(default=None, description="Filtering operation.")
    title_placement: Literal["hide", "left", "top"] | str | None = Field(
        default=None, alias="titlePlacement", description="Control title placement."
    )
    element_type: Literal["checkbox"] = Field(
        ..., alias="elementType", description="Checkbox control type."
    )
    default_value: str | None = Field(
        default=None, alias="defaultValue", description="Default checkbox value."
    )


class DashControlSourceManualV2Variant1AcceptableValuesVariant1Item(APIModel):
    value: str | None = Field(default=None, description="Allowed control value.")
    title: str | None = Field(default=None, description="Label for the allowed value.")


class DashControlSourceManualV2Variant1AcceptableValuesVariant2(APIModel):
    from_: str | None = Field(
        default=None, alias="from", description="Start of the allowed value range."
    )
    to: str | None = Field(default=None, description="End of the allowed value range.")


class DashControlSourceManualV2Variant2AcceptableValuesVariant1Item(APIModel):
    value: str | None = Field(default=None, description="Allowed control value.")
    title: str | None = Field(default=None, description="Label for the allowed value.")


class DashControlSourceManualV2Variant2AcceptableValuesVariant2(APIModel):
    from_: str | None = Field(
        default=None, alias="from", description="Start of the allowed value range."
    )
    to: str | None = Field(default=None, description="End of the allowed value range.")


class DashControlSourceManualV2Variant3AcceptableValuesVariant1Item(APIModel):
    value: str | None = Field(default=None, description="Allowed control value.")
    title: str | None = Field(default=None, description="Label for the allowed value.")


class DashControlSourceManualV2Variant3AcceptableValuesVariant2(APIModel):
    from_: str | None = Field(
        default=None, alias="from", description="Start of the allowed value range."
    )
    to: str | None = Field(default=None, description="End of the allowed value range.")


class DashControlSourceManualV2Variant4AcceptableValuesVariant1Item(APIModel):
    value: str | None = Field(default=None, description="Allowed control value.")
    title: str | None = Field(default=None, description="Label for the allowed value.")


class DashControlSourceManualV2Variant4AcceptableValuesVariant2(APIModel):
    from_: str | None = Field(
        default=None, alias="from", description="Start of the allowed value range."
    )
    to: str | None = Field(default=None, description="End of the allowed value range.")


class USAccessBindingDeltaAccessBindingSubject(APIModel):
    """Subject to which the role is assigned."""

    id: str | None = Field(default=None, description="Unique identifier of the subject.")
    type: (
        Literal[
            "system",
            "userAccount",
            "federatedUser",
            "serviceAccount",
            "group",
            "invitee",
        ]
        | str
        | None
    ) = Field(default=None, description="Type of the subject.")


class AccessBindingInheritedFrom(APIModel):
    """Resource from which the access binding is inherited."""

    id: str | None = Field(default=None, description="Unique identifier of the resource.")
    type: str | None = Field(default=None, description="Type of the resource.")


class SubjectWithBindingsSubjectClaims(APIModel):
    """Subject details."""

    sub: str | None = Field(default=None, description="Subject identifier.")
    sub_type: (
        Literal[
            "SUBJECT_TYPE_UNSPECIFIED",
            "USER_ACCOUNT",
            "GROUP",
            "INVITEE",
            "SERVICE_ACCOUNT",
            "_system",
        ]
        | str
        | None
    ) = Field(default=None, alias="subType", description="Subject type.")
    email: str | None = Field(default=None, description="Subject email address.")


class LakehouseOperationCreatedAt(APIModel):
    """Time when the operation was created."""

    seconds: str | None = Field(default=None, description="Number of seconds since the Unix epoch.")
    nanos: int | float | None = Field(
        default=None, description="Fractional seconds in nanoseconds."
    )


class LakehouseOperationModifiedAt(APIModel):
    """Time when the operation was last modified."""

    seconds: str | None = Field(default=None, description="Number of seconds since the Unix epoch.")
    nanos: int | float | None = Field(
        default=None, description="Fractional seconds in nanoseconds."
    )


class LakehouseOperationError(APIModel):
    """Operation error, if the operation failed."""

    code: int | float | None = Field(default=None, description="Operation error code.")
    message: str | None = Field(default=None, description="Operation error message.")
    details: list[Any] | None = Field(
        default=None, description="Additional operation error details."
    )


class DatalensOperation(APIModel):
    """Asynchronous datalens operation."""

    id: str | None = Field(default=None, description="Unique identifier of the operation.")
    description: str | None = Field(default=None, description="Description of the operation.")
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the operation.",
    )
    created_at: DatalensOperationCreatedAt | None = Field(default=None, alias="createdAt")
    modified_at: DatalensOperationModifiedAt | None = Field(default=None, alias="modifiedAt")
    metadata: DatalensOperationMetadata | None = None
    done: bool | None = Field(default=None, description="Indicates if the operation has completed.")


class DashControlSourceDatasetV2(
    RootModel[
        DashControlSourceDatasetV2Variant1
        | DashControlSourceDatasetV2Variant2
        | DashControlSourceDatasetV2Variant3
        | DashControlSourceDatasetV2Variant4
        | OtherKind
    ],
    hide_input_in_errors=True,
):
    root: (
        DashControlSourceDatasetV2Variant1
        | DashControlSourceDatasetV2Variant2
        | DashControlSourceDatasetV2Variant3
        | DashControlSourceDatasetV2Variant4
        | OtherKind
    ) = Field(..., description="Dataset control source.")


class AccessBinding(APIModel):
    role_id: str | None = Field(
        default=None,
        alias="roleId",
        description="ID of the role assigned to the subject.",
    )
    inherited_from: AccessBindingInheritedFrom | None = Field(default=None, alias="inheritedFrom")


class SubjectWithBindings(APIModel):
    subject_claims: SubjectWithBindingsSubjectClaims | None = Field(
        default=None, alias="subjectClaims"
    )
    access_bindings: list[AccessBinding] | None = Field(
        default=None,
        alias="accessBindings",
        description="Access bindings assigned directly to the subject.",
    )
    inherited_access_bindings: list[AccessBinding] | None = Field(
        default=None,
        alias="inheritedAccessBindings",
        description="Access bindings inherited by the subject.",
    )


class ListAccessBindingsResult(APIModel):
    subjects_with_bindings: list[SubjectWithBindings] | None = Field(
        default=None,
        alias="subjectsWithBindings",
        description="Subjects and their access bindings.",
    )
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for retrieving the next page of results.",
    )


class LakehouseOperation(APIModel):
    id: str | None = Field(default=None, description="Unique ID of the operation.")
    description: str | None = Field(default=None, description="Description of the operation.")
    created_at: LakehouseOperationCreatedAt | None = Field(default=None, alias="createdAt")
    created_by: str | None = Field(
        default=None, alias="createdBy", description="ID of the operation creator."
    )
    modified_at: LakehouseOperationModifiedAt | None = Field(default=None, alias="modifiedAt")
    done: bool | None = Field(default=None, description="Whether the operation has completed.")
    metadata: dict[str, Any] | None = Field(
        default=None, description="Service-specific operation metadata."
    )
    error: LakehouseOperationError | None = None
    response: dict[str, Any] | None = Field(
        default=None, description="Service-specific operation response."
    )


class DashControlSourceManualV2Variant1(APIModel):
    field_name: str | None = Field(
        default=None,
        alias="fieldName",
        description="Parameter name for the manual control.",
    )
    acceptable_values: (
        list[DashControlSourceManualV2Variant1AcceptableValuesVariant1Item]
        | DashControlSourceManualV2Variant1AcceptableValuesVariant2
        | None
    ) = Field(
        default=None, alias="acceptableValues", description="Values accepted by the manual control."
    )
    required: bool | None = Field(
        default=None, description="Whether the control value is required."
    )
    show_hint: bool | None = Field(
        default=None, alias="showHint", description="Whether to show the control hint."
    )
    show_title: bool | None = Field(
        default=None,
        alias="showTitle",
        description="Whether to show the control title.",
    )
    hint: str | None = Field(default=None, description="Control hint text.")
    accent_type: Literal["info"] | None = Field(
        default=None, alias="accentType", description="Control accent style."
    )
    inner_title: str | None = Field(
        default=None,
        alias="innerTitle",
        description="Title displayed inside the control.",
    )
    show_inner_title: bool | None = Field(
        default=None,
        alias="showInnerTitle",
        description="Whether to show the title inside the control.",
    )
    operation: (
        Literal[
            "IN",
            "NIN",
            "EQ",
            "NE",
            "GT",
            "LT",
            "GTE",
            "LTE",
            "ISNULL",
            "ISNOTNULL",
            "ISTARTSWITH",
            "STARTSWITH",
            "IENDSWITH",
            "ENDSWITH",
            "ICONTAINS",
            "CONTAINS",
            "NOTICONTAINS",
            "NOTCONTAINS",
            "BETWEEN",
            "LENEQ",
            "LENGT",
            "LENGTE",
            "LENLT",
            "LENLTE",
            "NO_SELECTED_VALUES",
        ]
        | str
        | None
    ) = Field(default=None, description="Filtering operation.")
    title_placement: Literal["hide", "left", "top"] | str | None = Field(
        default=None, alias="titlePlacement", description="Control title placement."
    )
    multiselectable: bool | None = Field(
        default=None, description="Whether multiple values can be selected."
    )
    element_type: Literal["select"] = Field(
        ..., alias="elementType", description="Select control type."
    )
    default_value: str | list[str] | None = Field(
        default=None,
        alias="defaultValue",
        description="Default selected value or values.",
    )


class DashControlSourceManualV2Variant2(APIModel):
    field_name: str | None = Field(
        default=None,
        alias="fieldName",
        description="Parameter name for the manual control.",
    )
    acceptable_values: (
        list[DashControlSourceManualV2Variant2AcceptableValuesVariant1Item]
        | DashControlSourceManualV2Variant2AcceptableValuesVariant2
        | None
    ) = Field(
        default=None, alias="acceptableValues", description="Values accepted by the manual control."
    )
    required: bool | None = Field(
        default=None, description="Whether the control value is required."
    )
    show_hint: bool | None = Field(
        default=None, alias="showHint", description="Whether to show the control hint."
    )
    show_title: bool | None = Field(
        default=None,
        alias="showTitle",
        description="Whether to show the control title.",
    )
    hint: str | None = Field(default=None, description="Control hint text.")
    accent_type: Literal["info"] | None = Field(
        default=None, alias="accentType", description="Control accent style."
    )
    inner_title: str | None = Field(
        default=None,
        alias="innerTitle",
        description="Title displayed inside the control.",
    )
    show_inner_title: bool | None = Field(
        default=None,
        alias="showInnerTitle",
        description="Whether to show the title inside the control.",
    )
    operation: (
        Literal[
            "IN",
            "NIN",
            "EQ",
            "NE",
            "GT",
            "LT",
            "GTE",
            "LTE",
            "ISNULL",
            "ISNOTNULL",
            "ISTARTSWITH",
            "STARTSWITH",
            "IENDSWITH",
            "ENDSWITH",
            "ICONTAINS",
            "CONTAINS",
            "NOTICONTAINS",
            "NOTCONTAINS",
            "BETWEEN",
            "LENEQ",
            "LENGT",
            "LENGTE",
            "LENLT",
            "LENLTE",
            "NO_SELECTED_VALUES",
        ]
        | str
        | None
    ) = Field(default=None, description="Filtering operation.")
    title_placement: Literal["hide", "left", "top"] | str | None = Field(
        default=None, alias="titlePlacement", description="Control title placement."
    )
    is_range: bool | None = Field(
        default=None,
        alias="isRange",
        description="Whether the control selects a date range.",
    )
    element_type: Literal["date"] = Field(
        ..., alias="elementType", description="Date control type."
    )
    field_type: (
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
        default=None, alias="fieldType", description="Type of the field used by the date control."
    )
    default_value: str | None = Field(
        default=None, alias="defaultValue", description="Default date value."
    )


class DashControlSourceManualV2Variant3(APIModel):
    field_name: str | None = Field(
        default=None,
        alias="fieldName",
        description="Parameter name for the manual control.",
    )
    acceptable_values: (
        list[DashControlSourceManualV2Variant3AcceptableValuesVariant1Item]
        | DashControlSourceManualV2Variant3AcceptableValuesVariant2
        | None
    ) = Field(
        default=None, alias="acceptableValues", description="Values accepted by the manual control."
    )
    required: bool | None = Field(
        default=None, description="Whether the control value is required."
    )
    show_hint: bool | None = Field(
        default=None, alias="showHint", description="Whether to show the control hint."
    )
    show_title: bool | None = Field(
        default=None,
        alias="showTitle",
        description="Whether to show the control title.",
    )
    hint: str | None = Field(default=None, description="Control hint text.")
    accent_type: Literal["info"] | None = Field(
        default=None, alias="accentType", description="Control accent style."
    )
    inner_title: str | None = Field(
        default=None,
        alias="innerTitle",
        description="Title displayed inside the control.",
    )
    show_inner_title: bool | None = Field(
        default=None,
        alias="showInnerTitle",
        description="Whether to show the title inside the control.",
    )
    operation: (
        Literal[
            "IN",
            "NIN",
            "EQ",
            "NE",
            "GT",
            "LT",
            "GTE",
            "LTE",
            "ISNULL",
            "ISNOTNULL",
            "ISTARTSWITH",
            "STARTSWITH",
            "IENDSWITH",
            "ENDSWITH",
            "ICONTAINS",
            "CONTAINS",
            "NOTICONTAINS",
            "NOTCONTAINS",
            "BETWEEN",
            "LENEQ",
            "LENGT",
            "LENGTE",
            "LENLT",
            "LENLTE",
            "NO_SELECTED_VALUES",
        ]
        | str
        | None
    ) = Field(default=None, description="Filtering operation.")
    title_placement: Literal["hide", "left", "top"] | str | None = Field(
        default=None, alias="titlePlacement", description="Control title placement."
    )
    element_type: Literal["input"] = Field(
        ..., alias="elementType", description="Input control type."
    )
    default_value: str | None = Field(
        default=None, alias="defaultValue", description="Default input value."
    )


class DashControlSourceManualV2Variant4(APIModel):
    field_name: str | None = Field(
        default=None,
        alias="fieldName",
        description="Parameter name for the manual control.",
    )
    acceptable_values: (
        list[DashControlSourceManualV2Variant4AcceptableValuesVariant1Item]
        | DashControlSourceManualV2Variant4AcceptableValuesVariant2
        | None
    ) = Field(
        default=None, alias="acceptableValues", description="Values accepted by the manual control."
    )
    required: bool | None = Field(
        default=None, description="Whether the control value is required."
    )
    show_hint: bool | None = Field(
        default=None, alias="showHint", description="Whether to show the control hint."
    )
    show_title: bool | None = Field(
        default=None,
        alias="showTitle",
        description="Whether to show the control title.",
    )
    hint: str | None = Field(default=None, description="Control hint text.")
    accent_type: Literal["info"] | None = Field(
        default=None, alias="accentType", description="Control accent style."
    )
    inner_title: str | None = Field(
        default=None,
        alias="innerTitle",
        description="Title displayed inside the control.",
    )
    show_inner_title: bool | None = Field(
        default=None,
        alias="showInnerTitle",
        description="Whether to show the title inside the control.",
    )
    operation: (
        Literal[
            "IN",
            "NIN",
            "EQ",
            "NE",
            "GT",
            "LT",
            "GTE",
            "LTE",
            "ISNULL",
            "ISNOTNULL",
            "ISTARTSWITH",
            "STARTSWITH",
            "IENDSWITH",
            "ENDSWITH",
            "ICONTAINS",
            "CONTAINS",
            "NOTICONTAINS",
            "NOTCONTAINS",
            "BETWEEN",
            "LENEQ",
            "LENGT",
            "LENGTE",
            "LENLT",
            "LENLTE",
            "NO_SELECTED_VALUES",
        ]
        | str
        | None
    ) = Field(default=None, description="Filtering operation.")
    title_placement: Literal["hide", "left", "top"] | str | None = Field(
        default=None, alias="titlePlacement", description="Control title placement."
    )
    element_type: Literal["checkbox"] = Field(
        ..., alias="elementType", description="Checkbox control type."
    )
    default_value: str | None = Field(
        default=None, alias="defaultValue", description="Default checkbox value."
    )


class USAccessBindingDeltaAccessBinding(APIModel):
    """Access binding to add or remove."""

    role_id: str | None = Field(
        default=None,
        alias="roleId",
        description="ID of the role assigned to the subject.",
    )
    subject: USAccessBindingDeltaAccessBindingSubject | None = None


class DashControlSourceManualV2(
    RootModel[
        DashControlSourceManualV2Variant1
        | DashControlSourceManualV2Variant2
        | DashControlSourceManualV2Variant3
        | DashControlSourceManualV2Variant4
        | OtherKind
    ],
    hide_input_in_errors=True,
):
    root: (
        DashControlSourceManualV2Variant1
        | DashControlSourceManualV2Variant2
        | DashControlSourceManualV2Variant3
        | DashControlSourceManualV2Variant4
        | OtherKind
    ) = Field(..., description="Manual control source.")


class USAccessBindingDelta(APIModel):
    action: Literal["ADD", "REMOVE"] | str | None = Field(
        default=None, description="Action to perform on the access binding."
    )
    access_binding: USAccessBindingDeltaAccessBinding | None = Field(
        default=None, alias="accessBinding"
    )
