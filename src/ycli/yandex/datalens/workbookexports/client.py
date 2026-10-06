"""DataLens workbook exports client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.workbookexports import endpoints

if TYPE_CHECKING:
    from ycli.yandex.datalens.workbookexports.models import (
        WorkbookExport,
        WorkbookExportCancelled,
        WorkbookExportStarted,
        WorkbookExportStatus,
    )


class WorkbookExportsClient(Resource):
    """Exports of a workbook: everything it holds as one document, to import elsewhere."""

    def start(self, workbook_id: str) -> WorkbookExportStarted:
        """``startWorkbookExport`` — start exporting a workbook → the id of the export.

        The export runs on its own: ask :meth:`status_get` until it is over, then
        :meth:`result_get` for the document.

        Args:
            workbook_id: The workbook's id.

        Returns:
            The id of the export.

        Examples:
            >>> datalens.workbookexports.start("wb000000000001").export_id
            'exp0000000001'
        """
        return self._session.send(endpoints.start(workbook_id))

    def status_get(self, export_id: str) -> WorkbookExportStatus:
        """``getWorkbookExportStatus`` → how far an export is.

        ``status`` is ``pending``, ``success`` or ``error``; ``notifications`` holds what the
        export has to say about an entry: its id, a level and a message.

        Args:
            export_id: The export's id.

        Returns:
            The status, the progress in percent and the notifications.

        Examples:
            >>> state = datalens.workbookexports.status_get("exp0000000001")
            >>> state.status.root, state.progress
            ('success', 100)
        """
        return self._session.send(endpoints.status_get(export_id))

    def result_get(self, export_id: str) -> WorkbookExport:
        """``getWorkbookExportResult`` → the exported workbook.

        ``data`` is what :meth:`WorkbookImportsClient.start` takes. An export that is not over,
        or was cancelled, answers ``409 Conflict``.

        Args:
            export_id: The export's id.

        Returns:
            The export: ``data.export`` holds the entries of the workbook, ``data.hash`` its
            checksum.

        Examples:
            >>> exported = datalens.workbookexports.result_get("exp0000000001")
            >>> sorted(exported.data.export)
            ['entries', 'version']
        """
        return self._session.send(endpoints.result_get(export_id))

    def cancel(self, export_id: str) -> WorkbookExportCancelled:
        """``cancelWorkbookExport`` — stop an export → its id.

        Cancelling an export that is over, or cancelling twice, answers the same.

        Args:
            export_id: The export's id.

        Returns:
            The id of the export.

        Examples:
            >>> datalens.workbookexports.cancel("exp0000000002").export_id
            'exp0000000002'
        """
        return self._session.send(endpoints.cancel(export_id))
