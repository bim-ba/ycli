"""DataLens screenshots FastMCP tools (reads): a picture of a dashboard or a chart."""

from typing import Annotated, Any

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import RO, datalens_client, new_server
from ycli.yandex.datalens.screenshots.models import ImageType, Screenshot

mcp = new_server("datalens-screenshots")

Type = Annotated[
    ImageType | None,
    Field(description="The format of the picture: png (the default), jpeg or jpg."),
]
Base64 = Annotated[
    bool | None,
    Field(description="Put the file itself in `data`, base64-encoded: large, ask first."),
]
S3 = Annotated[
    bool | None,
    Field(description="Put the file in S3 and `data` is its link; the default unless base64."),
]
Width = Annotated[
    int | float | None, Field(description="The width of the page in pixels, at most 6000.")
]
Height = Annotated[
    int | float | None, Field(description="The height of the page in pixels, at most 6000.")
]
FullPage = Annotated[
    bool | None, Field(description="Capture the whole page, not one screen of it.")
]


@mcp.tool(
    name="screenshots_dashboard_get",
    annotations={**RO, "title": "Get a DataLens dashboard screenshot"},
)
def dashboard_get(
    dash_id: Annotated[str, Field(description="The dashboard to capture.")],
    type: Type = None,  # noqa: A002  # the API's own name for it
    base64: Base64 = None,
    s3: S3 = None,
    width: Width = None,
    height: Height = None,
    full_page: FullPage = None,
    query_params: Annotated[
        dict[str, Any] | None,
        Field(
            description='Parameters of the page: {"tab": "<tab id>"} picks a tab, '
            '{"_theme": "dark"} the dark theme; a dashboard parameter goes by its name.'
        ),
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> Screenshot:
    """A picture of a saved dashboard, rendered by DataLens: by default a link to its file.

    The picture shows the data. DataLens takes about three of these a minute. Experimental.
    """
    return client.screenshots.dashboard_get(
        dash_id,
        type=type,
        base64=base64,
        s3=s3,
        width=width,
        height=height,
        full_page=full_page,
        query_params=query_params,
    )


@mcp.tool(
    name="screenshots_chart_get",
    annotations={**RO, "title": "Get a DataLens chart screenshot"},
)
def chart_get(
    chart_id: Annotated[str, Field(description="The chart to capture.")],
    type: Type = None,  # noqa: A002  # the API's own name for it
    base64: Base64 = None,
    s3: S3 = None,
    width: Width = None,
    height: Height = None,
    full_page: FullPage = None,
    query_params: Annotated[
        dict[str, Any] | None,
        Field(
            description="Parameters of the page: values of the chart's parameters by name, "
            '{"_theme": "dark"} for the dark theme.'
        ),
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> Screenshot:
    """A picture of a saved chart, rendered by DataLens: by default a link to its file.

    The picture shows the data. DataLens takes about three of these a minute. Experimental.
    """
    return client.screenshots.chart_get(
        chart_id,
        type=type,
        base64=base64,
        s3=s3,
        width=width,
        height=height,
        full_page=full_page,
        query_params=query_params,
    )
