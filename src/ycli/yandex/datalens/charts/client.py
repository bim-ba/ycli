"""DataLens charts client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.charts import endpoints

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ycli.yandex.datalens.charts.models import (
        ChartData,
        EditorChart,
        EditorChartCreate,
        EditorChartCreated,
        EditorChartSaved,
        EditorChartUpdate,
        EntryAnnotation,
        QLChart,
        QLChartChange,
        QLChartCreated,
        QLChartData,
        QLChartSaved,
        WizardChart,
        WizardChartCreated,
        WizardChartData,
        WizardChartSaved,
    )


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

    def wizard_get(
        self,
        chart_id: str,
        *,
        workbook_id: str | None = None,
        rev_id: str | None = None,
        include_permissions: bool | None = None,
        include_links: bool | None = None,
        include_favorite: bool | None = None,
        branch: str | None = None,
    ) -> WizardChart:
        """``getWizardChart`` → one chart built in the wizard: its datasets and what it shows.

        Args:
            chart_id: The chart's id.
            workbook_id: The workbook the chart lies in.
            rev_id: The revision to read; the current one when left out.
            include_permissions: Also say what the caller may do with it.
            include_links: Also say what it is linked to.
            include_favorite: Also say whether it is a favourite of the caller.
            branch: Which version to read: ``saved`` or ``published``; the published one when
                left out (measured). A save writes the saved one: read ``saved`` before
                changing the chart.

        Returns:
            The chart.

        Examples:
            >>> chart = datalens.charts.wizard_get("ch000000000001")
            >>> chart.entry.entry_id, chart.entry.data.visualization.type
            ('ch000000000001', 'flatTable')
        """
        return self._session.send(
            endpoints.wizard_get(
                chart_id,
                workbook_id=workbook_id,
                rev_id=rev_id,
                include_permissions=include_permissions,
                include_links=include_links,
                include_favorite=include_favorite,
                branch=branch,
            )
        )

    def wizard_create(
        self,
        data: WizardChartData,
        *,
        annotation: EntryAnnotation | None = None,
        key: str | None = None,
        workbook_id: str | None = None,
        name: str | None = None,
    ) -> WizardChartCreated:
        """``createWizardChart`` — create a chart of the wizard → it, with its id.

        Give ``workbook_id`` and ``name`` for where it lies (``key`` where the old placement
        model is used). The ``data`` of a chart read with ``wizard_get`` is a valid one.

        Args:
            data: The datasets the chart reads and what it shows.
            annotation: A description of the chart.
            key: The entry's key, in a folder.
            workbook_id: The workbook to create it in.
            name: The chart's name.

        Returns:
            The created chart.

        Examples:
            >>> from ycli.yandex.datalens.charts.models import WizardChartData
            >>> table = {"type": "flatTable", "columns": {"items": [{"guid": "guid-1"}]}}
            >>> data = WizardChartData.model_validate(
            ...     {"sources": {"datasetsIds": ["ds000000000001"]}, "visualization": table}
            ... )
            >>> created = datalens.charts.wizard_create(
            ...     data, workbook_id="wb000000000001", name="Sales"
            ... )
            >>> created.entry.entry_id
            'ch000000000001'
        """
        return self._session.send(
            endpoints.wizard_create(
                data, annotation=annotation, key=key, workbook_id=workbook_id, name=name
            )
        )

    def wizard_update(
        self,
        chart_id: str,
        *,
        mode: str,
        data: WizardChartData,
        annotation: EntryAnnotation | None = None,
        rev_id: str | None = None,
    ) -> WizardChartSaved:
        """``updateWizardChart`` — save a chart of the wizard as given → what was saved.

        DataLens does not check a revision here: a save overwrites what was saved since you read it
        (measured).

        ``data`` replaces what the chart holds: read it, change it, send it back whole.
        ``save`` keeps the change as a draft (``savedId`` moves, ``publishedId`` stays);
        ``publish`` makes it the version everyone sees.

        Args:
            chart_id: The chart's id.
            mode: ``save`` or ``publish``.
            data: The datasets the chart reads and what it shows.
            annotation: A description of the chart.
            rev_id: The revision the change is made on; DataLens does not check it (measured).

        Returns:
            The chart as saved.

        Examples:
            >>> from ycli.yandex.datalens.charts.models import WizardChartData
            >>> table = {"type": "flatTable", "columns": {"items": [{"guid": "guid-1"}]}}
            >>> data = WizardChartData.model_validate(
            ...     {"sources": {"datasetsIds": ["ds000000000001"]}, "visualization": table}
            ... )
            >>> saved = datalens.charts.wizard_update("ch000000000001", mode="save", data=data)
            >>> saved.entry.rev_id
            'rev2'
        """
        return self._session.send(
            endpoints.wizard_update(
                chart_id, mode=mode, data=data, annotation=annotation, rev_id=rev_id
            )
        )

    def wizard_delete(self, chart_id: str) -> None:
        """``deleteWizardChart`` — delete a chart of the wizard; dashboards that show it lose it.

        The API has no way to bring it back, and a dashboard that shows it keeps naming its
        id (measured).

        Args:
            chart_id: The chart's id.

        Examples:
            >>> datalens.charts.wizard_delete("ch000000000001")
        """
        self._session.send(endpoints.wizard_delete(chart_id))

    def ql_get(
        self,
        chart_id: str,
        *,
        workbook_id: str | None = None,
        rev_id: str | None = None,
        include_permissions: bool | None = None,
        include_links: bool | None = None,
        include_favorite: bool | None = None,
        branch: str | None = None,
    ) -> QLChart:
        """``getQLChart`` → one QL chart: flat, with no ``entry`` around it.

        Args:
            chart_id: The chart's id.
            workbook_id: The workbook the chart lies in.
            rev_id: The revision to read; the current one when left out.
            include_permissions: Also say what the caller may do with it.
            include_links: Also say what it is linked to.
            include_favorite: Also say whether it is a favourite of the caller.
            branch: Which version to read: ``saved`` or ``published``; the published one when
                left out (measured). A save writes the saved one: read ``saved`` before
                changing the chart.

        Returns:
            The chart.

        Examples:
            >>> chart = datalens.charts.ql_get("ch000000000001")
            >>> chart.entry_id, chart.type
            ('ch000000000001', 'table_ql_node')
        """
        return self._session.send(
            endpoints.ql_get(
                chart_id,
                workbook_id=workbook_id,
                rev_id=rev_id,
                include_permissions=include_permissions,
                include_links=include_links,
                include_favorite=include_favorite,
                branch=branch,
            )
        )

    def ql_create(
        self,
        *,
        template: str,
        data: QLChartData,
        annotation: EntryAnnotation | None = None,
        key: str | None = None,
        workbook_id: str | None = None,
        name: str | None = None,
    ) -> QLChartCreated:
        """``createQLChart`` — create a QL chart → what DataLens answers.

        Neither the content of a QL chart nor the reply is described by the specification:
        ``data`` goes as given, the reply is kept as it came.

        Args:
            template: The template of the chart; the API takes only ``ql`` today.
            data: What the chart holds: its query and how it is shown.
            annotation: A description of the chart.
            key: The entry's key, in a folder.
            workbook_id: The workbook to create it in.
            name: The chart's name.

        Returns:
            The reply, as it came.

        Examples:
            >>> from ycli.yandex.datalens.charts.models import QLChartData
            >>> data = QLChartData({"queryValue": "select 1"})
            >>> created = datalens.charts.ql_create(
            ...     template="ql", data=data, workbook_id="wb000000000001", name="Top"
            ... )
            >>> created.root["entry"]["entryId"]
            'ch000000000001'
        """
        return self._session.send(
            endpoints.ql_create(
                template=template,
                data=data,
                annotation=annotation,
                key=key,
                workbook_id=workbook_id,
                name=name,
            )
        )

    def ql_update(
        self,
        entry_id: str,
        *,
        template: str,
        mode: str,
        data: QLChartChange,
        annotation: EntryAnnotation | None = None,
    ) -> QLChartSaved:
        """``updateQLChart`` — save a QL chart as given → what DataLens answers.

        DataLens does not check a revision here: a save overwrites what was saved since you read it
        (measured).

        Args:
            entry_id: The chart's id.
            template: The template of the chart; the API takes only ``ql`` today.
            mode: ``save`` or ``publish``.
            data: What the chart holds; it replaces the whole of it.
            annotation: A description of the chart.

        Returns:
            The reply, as it came.

        Examples:
            >>> from ycli.yandex.datalens.charts.models import QLChartChange
            >>> data = QLChartChange({"queryValue": "select 2"})
            >>> saved = datalens.charts.ql_update(
            ...     "ch000000000001", template="ql", mode="save", data=data
            ... )
            >>> saved.root["entry"]["entryId"]
            'ch000000000001'
        """
        return self._session.send(
            endpoints.ql_update(
                entry_id, template=template, mode=mode, data=data, annotation=annotation
            )
        )

    def ql_delete(self, chart_id: str) -> None:
        """``deleteQLChart`` — delete a QL chart; dashboards that show it lose it.

        Args:
            chart_id: The chart's id.

        Examples:
            >>> datalens.charts.ql_delete("ch000000000001")
        """
        self._session.send(endpoints.ql_delete(chart_id))

    def editor_get(
        self,
        chart_id: str,
        *,
        workbook_id: str | None = None,
        rev_id: str | None = None,
        include_permissions: bool | None = None,
        include_links: bool | None = None,
        include_favorite: bool | None = None,
        branch: str | None = None,
    ) -> EditorChart:
        """``getEditorChart`` → one chart of the editor: its kind (``type``) and its code.

        Args:
            chart_id: The chart's id.
            workbook_id: The workbook the chart lies in.
            rev_id: The revision to read; the current one when left out.
            include_permissions: Also say what the caller may do with it.
            include_links: Also say what it is linked to.
            include_favorite: Also say whether it is a favourite of the caller.
            branch: Which version to read: ``saved`` or ``published``; the published one when
                left out (measured). A save writes the saved one: read ``saved`` before
                changing the chart.

        Returns:
            The chart.

        Examples:
            >>> chart = datalens.charts.editor_get("ch000000000001")
            >>> chart.entry.type
            'table_node'
        """
        return self._session.send(
            endpoints.editor_get(
                chart_id,
                workbook_id=workbook_id,
                rev_id=rev_id,
                include_permissions=include_permissions,
                include_links=include_links,
                include_favorite=include_favorite,
                branch=branch,
            )
        )

    def editor_create(self, entry: EditorChartCreate) -> EditorChartCreated:
        """``createEditorChart`` — create a chart of the editor → it, with its id.

        ``type`` says which kind it is (``table_node``, ``d3_node``, ``markdown_node``,
        ``advanced-chart_node``, ``control_node``) and ``data`` holds its tabs of code.

        Args:
            entry: The new chart: where it lies, its kind and its code.

        Returns:
            The created chart.

        Examples:
            >>> from pydantic import TypeAdapter
            >>> from ycli.yandex.datalens.charts.models import EditorChartCreate
            >>> new = TypeAdapter(EditorChartCreate).validate_python(
            ...     {"type": "table_node", "workbookId": "wb000000000001", "name": "Top"}
            ... )
            >>> datalens.charts.editor_create(new).entry.type
            'table_node'
        """
        return self._session.send(endpoints.editor_create(entry))

    def editor_update(self, entry: EditorChartUpdate, *, mode: str) -> EditorChartSaved:
        """``updateEditorChart`` — save a chart of the editor as given → what was saved.

        DataLens does not check a revision here: a save overwrites what was saved since you read it
        (measured).

        Args:
            entry: The chart to save: its ``entryId``, its kind and its code.
            mode: ``save`` or ``publish``.

        Returns:
            The chart as saved.

        Examples:
            >>> from pydantic import TypeAdapter
            >>> from ycli.yandex.datalens.charts.models import EditorChartUpdate
            >>> change = TypeAdapter(EditorChartUpdate).validate_python(
            ...     {"type": "table_node", "entryId": "ch000000000001"}
            ... )
            >>> datalens.charts.editor_update(change, mode="save").entry.type
            'table_node'
        """
        return self._session.send(endpoints.editor_update(entry, mode=mode))

    def editor_delete(self, chart_id: str) -> None:
        """``deleteEditorChart`` — delete a chart of the editor; dashboards that show it lose it.

        Args:
            chart_id: The chart's id.

        Examples:
            >>> datalens.charts.editor_delete("ch000000000001")
        """
        self._session.send(endpoints.editor_delete(chart_id))
