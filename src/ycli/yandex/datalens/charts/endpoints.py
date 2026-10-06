"""DataLens chart operations, declared once (sans-IO).

Examples:
    >>> data_get("ch1", params=None).body
    {'chartId': 'ch1'}
"""

from collections.abc import Mapping, Sequence

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
from ycli.yandex.datalens.charts.models import ChartData
from ycli.yandex.datalens.schemas.data import GetChartDataArgs


def data_get(
    chart_id: str, *, params: Mapping[str, str | Sequence[str]] | None
) -> Endpoint[ChartData]:
    given = (
        None
        if params is None
        else {
            name: value if isinstance(value, str) else list(value) for name, value in params.items()
        }
    )
    body = GetChartDataArgs(chartId=chart_id, params=given)
    return RPC("getChartData", ChartData, json=body, effect=Effect.READ)
