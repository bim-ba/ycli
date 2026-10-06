"""DataLens charts client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.charts import endpoints

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ycli.yandex.datalens.charts.models import ChartData


class ChartsClient(Resource):
    """Charts: what a dashboard shows, built in the wizard, in QL or in the editor."""

    def data_get(
        self, chart_id: str, *, params: Mapping[str, str | Sequence[str]] | None = None
    ) -> ChartData:
        """``getChartData`` → the data a saved chart shows, as tables.

        The chart runs with its saved settings; ``params`` gives the values of its parameters,
        the page of a table among them. ``chartType`` says how the chart is built (``wizard``,
        ``ql``, ``editor``), and each table of ``results`` has its columns and its rows. A
        pivot table is not supported (``422``), and a chart whose source cannot be reached
        answers ``427``.

        Args:
            chart_id: The id of a saved chart.
            params: Values for the chart's parameters, by name: one value or several.

        Returns:
            The tables of the chart.

        Examples:
            >>> tables = datalens.charts.data_get("ch000000000001").root
            >>> tables.chart_type, tables.results[0].rows
            ('wizard', [['Moscow', 120]])
        """
        return self._session.send(endpoints.data_get(chart_id, params=params))
