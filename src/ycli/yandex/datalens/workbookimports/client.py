"""DataLens workbook imports client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.workbookimports import endpoints

if TYPE_CHECKING:
    from ycli.yandex.datalens.workbookimports.models import (
        WorkbookImportStarted,
        WorkbookImportStatus,
    )


class WorkbookImportsClient(Resource):
    """Imports of a workbook: a new workbook made from the document an export gave."""

    def start(
        self,
        data: dict[str, Any],
        *,
        title: str,
        collection_id: str | None = None,
        description: str | None = None,
    ) -> WorkbookImportStarted:
        """``startWorkbookImport`` — start making a workbook from an export → its ids.

        The workbook exists at once and is filled as the import runs: ask :meth:`status_get`
        until it is over.

        Args:
            data: The ``data`` of an export's result: its ``export`` and its ``hash``.
            title: The title of the new workbook.
            collection_id: The collection to make it in; the root when left out.
            description: The description of the new workbook.

        Returns:
            The id of the import and the id of the new workbook.

        Examples:
            >>> exported = {"export": {"version": "1", "entries": {}}, "hash": "h1"}
            >>> started = datalens.workbookimports.start(
            ...     exported, title="Sales, copy", collection_id="col0000000001"
            ... )
            >>> started.import_id, started.workbook_id
            ('imp0000000001', 'wb000000000002')
        """
        return self._session.send(
            endpoints.start(data, title=title, collection_id=collection_id, description=description)
        )

    def status_get(self, import_id: str) -> WorkbookImportStatus:
        """``getWorkbookImportStatus`` → how far an import is.

        ``status`` is ``pending``, ``success`` or ``error``; ``notifications`` holds what the
        import has to say about an entry: its id, a level and a message.

        Args:
            import_id: The import's id.

        Returns:
            The status, the progress in percent and the id of the workbook.

        Examples:
            >>> state = datalens.workbookimports.status_get("imp0000000001")
            >>> state.status.root, state.workbook_id
            ('success', 'wb000000000002')
        """
        return self._session.send(endpoints.status_get(import_id))
