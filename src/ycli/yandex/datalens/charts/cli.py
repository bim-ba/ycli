"""`datalens charts` commands."""

import json
from typing import Annotated

import typer

from ycli.yandex.datalens.charts.models import ChartData
from ycli.yandex.datalens.client import DataLensClient

app = typer.Typer(name="charts", help="DataLens charts.", no_args_is_help=True)

ChartIDArg = Annotated[str, typer.Argument(metavar="CHART_ID", help="Chart id.")]


@app.command("data-get")
def data_get(
    chart_id: ChartIDArg,
    params: Annotated[
        str | None,
        typer.Option(
            "--params",
            help='Values for the chart\'s parameters, as a JSON object: {"year": "2026", '
            '"city": ["Moscow", "Kazan"]}.',
        ),
    ] = None,
    *,
    datalens: DataLensClient,
) -> ChartData:
    """Print the data a saved chart shows, as tables; a pivot table is not supported."""
    return datalens.charts.data_get(chart_id, params=None if params is None else json.loads(params))
