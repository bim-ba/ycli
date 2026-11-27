# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from typing import Any, Literal

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody


class GetScreenshotResult(APIModel):
    data: str | None = Field(
        default=None,
        description="URL of the uploaded file or its base64 representation.",
    )
    status: int | float | None = None
    code: str | None = None
    message: str | None = None


class GetChartScreenshotArgs(RequestBody):
    type: Literal["png", "jpeg", "jpg"] | str | None = Field(
        default=None, description="Output file format. Defaults to png."
    )
    base64: bool | None = Field(
        default=None, description="Whether to return the file as a base64 string."
    )
    s3: bool | None = Field(
        default=None,
        description="Whether to upload the file to S3. Defaults to true unless base64 is enabled.",
    )
    width: int | float | None = Field(default=None, description="Viewport width in pixels.")
    height: int | float | None = Field(default=None, description="Viewport height in pixels.")
    full_page: bool | None = Field(
        default=None, alias="fullPage", description="Whether to capture the full page."
    )
    query_params: dict[str, Any] | None = Field(
        default=None,
        alias="queryParams",
        description="Additional query parameters of the captured page, for example chart or dashboard parameters.",
    )
    chart_id: str = Field(..., alias="chartId", description="ID of the chart to capture.")


class GetDashScreenshotArgs(RequestBody):
    type: Literal["png", "jpeg", "jpg"] | str | None = Field(
        default=None, description="Output file format. Defaults to png."
    )
    base64: bool | None = Field(
        default=None, description="Whether to return the file as a base64 string."
    )
    s3: bool | None = Field(
        default=None,
        description="Whether to upload the file to S3. Defaults to true unless base64 is enabled.",
    )
    width: int | float | None = Field(default=None, description="Viewport width in pixels.")
    height: int | float | None = Field(default=None, description="Viewport height in pixels.")
    full_page: bool | None = Field(
        default=None, alias="fullPage", description="Whether to capture the full page."
    )
    query_params: dict[str, Any] | None = Field(
        default=None,
        alias="queryParams",
        description="Additional query parameters of the captured page, for example chart or dashboard parameters.",
    )
    dash_id: str = Field(..., alias="dashId", description="ID of the dashboard to capture.")
