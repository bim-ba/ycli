"""DataLens screenshot operations, declared once (sans-IO).

Examples:
    >>> dashboard_get("d1").path
    'rpc/getDashScreenshot'
"""

from collections.abc import Mapping
from typing import Any

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
from ycli.yandex.datalens.schemas.screenshots import GetChartScreenshotArgs, GetDashScreenshotArgs
from ycli.yandex.datalens.screenshots.models import Screenshot


def dashboard_get(
    dash_id: str,
    *,
    type: str | None = None,  # noqa: A002  # the API's own name for it
    base64: bool | None = None,
    s3: bool | None = None,
    width: int | float | None = None,
    height: int | float | None = None,
    full_page: bool | None = None,
    query_params: Mapping[str, Any] | None = None,
) -> Endpoint[Screenshot]:
    body = GetDashScreenshotArgs(
        dashId=dash_id,
        type=type,
        base64=base64,
        s3=s3,
        width=width,
        height=height,
        fullPage=full_page,
        queryParams=None if query_params is None else dict(query_params),
    )
    return RPC("getDashScreenshot", Screenshot, json=body, effect=Effect.READ)


def chart_get(
    chart_id: str,
    *,
    type: str | None = None,  # noqa: A002  # the API's own name for it
    base64: bool | None = None,
    s3: bool | None = None,
    width: int | float | None = None,
    height: int | float | None = None,
    full_page: bool | None = None,
    query_params: Mapping[str, Any] | None = None,
) -> Endpoint[Screenshot]:
    body = GetChartScreenshotArgs(
        chartId=chart_id,
        type=type,
        base64=base64,
        s3=s3,
        width=width,
        height=height,
        fullPage=full_page,
        queryParams=None if query_params is None else dict(query_params),
    )
    return RPC("getChartScreenshot", Screenshot, json=body, effect=Effect.READ)
