"""Wiki ``/operations`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.wiki.operations import endpoints

if TYPE_CHECKING:
    from ycli.yandex.wiki.operations.models import (
        CloneOperationStatus,
        GridCloneOperationStatus,
    )


class OperationsClient(Resource):
    """Status reads for async page/grid clones.

    Both endpoints are normal reads (they surface on MCP): re-read one until its ``status`` is
    terminal to wait for a clone triggered by ``pages clone`` / ``grids clone``.
    """

    def clone_get(self, task_id: str) -> CloneOperationStatus:
        """``GET /operations/clone/{task_id}`` → a page-clone's status (poll this to wait).

        The ``task_id`` is the ``operation.id`` returned by ``PagesClient.clone``. Poll until
        ``is_terminal``; on ``success`` the ``result.page`` names the clone.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.operations.clone_get("task-1").is_terminal  # doctest: +SKIP
            True
        """
        return self._session.send(endpoints.get_clone_status(task_id))

    def gridclone_get(self, task_id: str) -> GridCloneOperationStatus:
        """``GET /operations/clone_inline_grid/{task_id}`` → a grid-clone's status (poll to wait).

        The ``task_id`` is the ``operation.id`` returned by ``GridsClient.clone``. Poll until
        ``is_terminal``; on ``success`` the ``result.grid_id`` names the copy.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.operations.gridclone_get("task-1").is_terminal  # doctest: +SKIP
            True
        """
        return self._session.send(endpoints.get_grid_clone_status(task_id))
