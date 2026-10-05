# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import ConfigDict, Field, RootModel

from ycli.yandex.models import APIModel, RequestBody

from . import shared
from .shared import EntryLocationIdentifiers


class GetQLChartArgs(RequestBody):
    chart_id: str = Field(
        ...,
        alias="chartId",
        description="ID of the QL chart to return. You can find it in the chart settings in DataLens interface.",
    )
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook the QL chart belongs to. If navigation across folders is enabled and the QL chart belongs to a folder, the value must be `null`.",
    )
    rev_id: str | None = Field(
        default=None,
        alias="revId",
        description="Version ID for the QL chart.<br/> If the field is empty, you will get the current version of the QL chart.",
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


class DeleteQLChartArgs(RequestBody):
    chart_id: str = Field(..., alias="chartId")


class DeleteQLChartResponse(APIModel):
    pass


class UpdateQLChartResponse(RootModel[dict[str, Any]]):
    root: dict[str, Any]


class CreateQLChartResponse(RootModel[dict[str, Any]]):
    root: dict[str, Any]


class UpdateQLChartArgsData(RootModel[dict[str, Any]]):
    root: dict[str, Any]


class CreateQLChartArgsData(RootModel[dict[str, Any]]):
    root: dict[str, Any]


class UpdateQLChartArgs(APIModel):
    model_config = ConfigDict(
        extra="allow",
    )
    __annotations__ = {
        "__pydantic_extra__": dict[str, Any],
    }
    entry_id: str = Field(..., alias="entryId")
    template: Literal["ql"]
    annotation: shared.EntryAnnotationArg | None = None
    mode: shared.EntryUpdateMode
    data: UpdateQLChartArgsData


class CreateQLChartArgs(EntryLocationIdentifiers):
    template: Literal["ql"]
    annotation: shared.EntryAnnotationArg | None = None
    data: CreateQLChartArgsData | None = None
