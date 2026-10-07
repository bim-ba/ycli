"""DataLens reports client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.reports import endpoints

if TYPE_CHECKING:
    from ycli.yandex.datalens.reports.models import (
        EntryAnnotation,
        Report,
        ReportCreated,
        ReportData,
        ReportMeta,
        ReportSaved,
    )


class ReportsClient(Resource):
    """Reports: slides of charts and texts, made to be read and printed.

    Measured (2026-10-06): reading is whole, writing is not. A report saved through the
    API loses the ``layout`` of the elements of its slides and part of its ``settings``
    (``create`` and ``update`` alike); DataLens drops them without a word, though ycli
    sends every value it was given.
    """

    def get(
        self,
        entry_id: str,
        *,
        rev_id: str | None = None,
        include_permissions: bool | None = None,
        include_favorite: bool | None = None,
    ) -> Report:
        """``getReport`` → one report: its slides and what stands on them.

        Args:
            entry_id: The report's id.
            rev_id: The revision to read; the current one when left out.
            include_permissions: Also say what the caller may do with it.
            include_favorite: Also say whether it is a favourite of the caller.

        Returns:
            The report.

        Examples:
            >>> datalens.reports.get("rep00000000001").entry.entry_id
            'rep00000000001'
        """
        return self._session.send(
            endpoints.get(
                entry_id,
                rev_id=rev_id,
                include_permissions=include_permissions,
                include_favorite=include_favorite,
            )
        )

    def create(
        self,
        *,
        data: ReportData,
        meta: ReportMeta | None,
        annotation: EntryAnnotation | None = None,
        include_permissions: bool | None = None,
        key: str | None = None,
        workbook_id: str | None = None,
        name: str | None = None,
    ) -> ReportCreated:
        """``createReport`` — create a report → it, with its id.

        Measured (2026-10-06): a report saved through the API loses the ``layout`` of the elements
        of its slides and part of its ``settings``; DataLens drops them without a word.
        A copy made from the ``data`` of a report read with ``get`` is valid, and has lost
        where its elements stood.

        Give ``workbook_id`` and ``name`` for where it lies (``key`` where the old placement
        model is used).

        Args:
            data: What the report holds: its slides and its settings.
            meta: Metadata of the entry; ``None`` for none.
            annotation: A description of the report.
            include_permissions: Also say what the caller may do with the new report.
            key: The entry's key, in a folder.
            workbook_id: The workbook to create it in.
            name: The report's name.

        Returns:
            The created report.

        Examples:
            >>> from ycli.yandex.datalens.reports.models import ReportData
            >>> data = ReportData.model_validate({"slides": [{"id": "s1"}]})
            >>> created = datalens.reports.create(
            ...     data=data, meta=None, workbook_id="wb000000000001", name="Q1"
            ... )
            >>> created.entry.entry_id
            'rep00000000001'
        """
        return self._session.send(
            endpoints.create(
                data=data,
                meta=meta,
                annotation=annotation,
                include_permissions=include_permissions,
                key=key,
                workbook_id=workbook_id,
                name=name,
            )
        )

    def update(
        self,
        entry_id: str,
        *,
        data: ReportData,
        mode: str,
        meta: ReportMeta | None,
        rev_id: str | None = None,
        annotation: EntryAnnotation | None = None,
    ) -> ReportSaved:
        """``updateReport`` — save a report as given → what was saved.

        DataLens does not check a revision here: a save overwrites what was saved since you read it
        (measured).

        Measured (2026-10-06): a report saved through the API loses the ``layout`` of the elements
        of its slides and part of its ``settings``; DataLens drops them without a word.
        So do not save a report that exists without telling its owner what it will lose.

        ``data`` replaces what the report holds: read it, change it, send it back whole.

        Args:
            entry_id: The report's id.
            data: What the report holds.
            mode: ``save`` or ``publish``.
            meta: Metadata of the entry; ``None`` for none.
            rev_id: The revision the change is made on; DataLens does not check it (measured).
            annotation: A description of the report.

        Returns:
            The report as saved.

        Examples:
            >>> from ycli.yandex.datalens.reports.models import ReportData
            >>> data = ReportData.model_validate({"slides": [{"id": "s1"}, {"id": "s2"}]})
            >>> saved = datalens.reports.update("rep00000000001", data=data, mode="save", meta=None)
            >>> saved.entry.rev_id
            'rev2'
        """
        return self._session.send(
            endpoints.update(
                entry_id, data=data, mode=mode, meta=meta, rev_id=rev_id, annotation=annotation
            )
        )

    def delete(self, entry_id: str) -> None:
        """``deleteReport`` — delete a report.

        Args:
            entry_id: The report's id.

        Examples:
            >>> datalens.reports.delete("rep00000000001")
        """
        self._session.send(endpoints.delete(entry_id))
