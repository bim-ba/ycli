# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.


from pydantic import Field

from ycli.yandex.models import RequestBody

from . import shared


class ListSharedEntryAccessBindingsArgs(RequestBody):
    entry_id: str = Field(
        ...,
        alias="entryId",
        description="ID of the common object whose access bindings to retrieve.",
    )
    get_inherited_bindings: bool | None = Field(
        default=None,
        alias="getInheritedBindings",
        description="Whether to include inherited access bindings.",
    )
    page_size: int | float | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum number of subjects to return.",
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for retrieving the next page of results.",
    )


class UpdateSharedEntryAccessBindingsArgs(RequestBody):
    entry_id: str = Field(
        ...,
        alias="entryId",
        description="ID of the common object whose access bindings to update.",
    )
    deltas: list[shared.USAccessBindingDelta] = Field(
        ..., description="Access binding changes to apply."
    )
