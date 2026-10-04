"""Wiki ``/operations`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.wiki.operations import endpoints

if TYPE_CHECKING:
    from ycli.yandex.wiki.operations.models import (
        CloneOperationStatus,
        GridCloneOperationStatus,
        MoveOperationStatus,
    )


class OperationsClient(Resource):
    """Status reads for async page/grid clones and page moves.

    Every endpoint is a normal read (they surface on MCP): re-read one until its ``status`` is
    terminal to wait for the operation triggered by ``pages clone`` / ``grids clone`` /
    ``pages move``.
    """

    def clone_get(self, task_id: str) -> CloneOperationStatus:
        """``GET /operations/clone/{task_id}`` → a page-clone's status (poll this to wait).

        The ``task_id`` is the ``operation.id`` returned by ``PagesClient.clone``. Poll until
        ``is_terminal``; on ``success`` the ``result.page`` names the clone.

        Args:
            task_id: The operation's id.

        Returns:
            The clone's status.

        Examples:
            >>> wiki.operations.clone_get("task-5201").is_terminal
            True
        """
        return self._session.send(endpoints.clone_get(task_id))

    def gridclone_get(self, task_id: str) -> GridCloneOperationStatus:
        """``GET /operations/clone_inline_grid/{task_id}`` → a grid-clone's status (poll to wait).

        The ``task_id`` is the ``operation.id`` returned by ``GridsClient.clone``. Poll until
        ``is_terminal``; on ``success`` the ``result.grid_id`` names the copy.

        Args:
            task_id: The operation's id.

        Returns:
            The grid clone's status.

        Examples:
            >>> wiki.operations.gridclone_get("task-5301").is_terminal
            False
        """
        return self._session.send(endpoints.gridclone_get(task_id))

    def move_get(self, task_id: str) -> MoveOperationStatus:
        """``GET /operations/move/{task_id}`` → a page-move's status (poll this to wait).

        Undocumented by Yandex (present in the live OpenAPI only) and may change. The ``task_id``
        is the ``operation.id`` returned by ``PagesClient.move``. Poll until ``is_terminal``; on
        ``success`` the ``result.page_count`` says how many pages moved.

        Args:
            task_id: The operation's id.

        Returns:
            The move's status.

        Examples:
            >>> wiki.operations.move_get("task-5401").result.page_count
            4
        """
        return self._session.send(endpoints.move_get(task_id))
