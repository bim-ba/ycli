"""Contract cases for DataLens charts (see tests/contract/)."""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect

CHART = "ch000000000001"
PARAMS = {"year": "2026", "city": ["Moscow", "Kazan"]}
TABLES = {
    "chartType": "wizard",
    "results": [
        {
            "schema": [
                {"name": "City", "guid": "guid-1", "type": "string"},
                {"name": "Orders", "guid": "guid-2", "type": "integer"},
            ],
            "rows": [["Moscow", 120]],
        }
    ],
}

CASES = [
    Case(
        "datalens.charts.data_get",
        args=(CHART,),
        cli=["datalens", "charts", "data-get", CHART],
        mcp=("datalens_charts_data_get", {"chart_id": CHART}),
        effect=Effect.READ,
        exchanges=[(Sent("POST", "rpc/getChartData", json={"chartId": CHART}), Reply(json=TABLES))],
    ),
    Case(
        "datalens.charts.data_get",
        args=(CHART,),
        kwargs={"params": PARAMS},
        cli=["datalens", "charts", "data-get", CHART, "--params", json.dumps(PARAMS)],
        mcp=("datalens_charts_data_get", {"chart_id": CHART, "params": PARAMS}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getChartData", json={"chartId": CHART, "params": PARAMS}),
                Reply(json=TABLES),
            )
        ],
    ),
]
