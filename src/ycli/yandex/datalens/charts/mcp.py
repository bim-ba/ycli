"""DataLens charts FastMCP tools (read-only) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.datalens.charts.models import ChartData
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import RO, datalens_client

mcp = FastMCP("datalens-charts")

ChartID = Annotated[str, Field(description="Chart id.")]


@mcp.tool(name="charts_data_get", annotations={**RO, "title": "Read the data of a DataLens chart"})
def data_get(
    chart_id: ChartID,
    params: Annotated[
        dict[str, str | list[str]] | None,
        Field(description="Values for the chart's parameters, by name: one value or several."),
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> ChartData:
    """The data a saved chart shows, as tables of columns and rows.

    The chart runs with its saved settings. ``chartType`` says how it is built (``wizard``,
    ``ql``, ``editor``). A pivot table is not supported, and a chart whose source cannot be
    reached answers with an error.
    ``entries_list`` with the scope ``widget`` finds charts.
    """
    return client.charts.data_get(chart_id, params=params)
