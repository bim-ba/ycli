"""Declarative Yandex Wiki /operations client (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly.
"""

import uplink

from ycli.yandex.wiki.base import WikiResource
from ycli.yandex.wiki.operations.models import (
    CloneOperationStatus,
    GridCloneOperationStatus,
)


class OperationsClient(WikiResource):
    """Declarative HTTP for ``/operations`` — status reads for async page/grid clones.

    Both endpoints are normal reads (they surface on MCP): re-read one until its ``status`` is
    terminal to wait for a clone triggered by ``pages clone`` / ``grids clone``.
    """

    @uplink.returns.json()
    @uplink.get("operations/clone/{task_id}")
    def clone_get(self, task_id: uplink.Path) -> CloneOperationStatus:  # ty: ignore[empty-body]
        """``GET /operations/clone/{task_id}`` → a page-clone's status (poll this to wait).

        The ``task_id`` is the ``operation.id`` returned by ``PagesClient.clone``. Poll until
        ``is_terminal``; on ``success`` the ``result.page`` names the clone.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.operations.clone_get("task-1").is_terminal  # doctest: +SKIP
            True
        """

    @uplink.returns.json()
    @uplink.get("operations/clone_inline_grid/{task_id}")
    def gridclone_get(self, task_id: uplink.Path) -> GridCloneOperationStatus:  # ty: ignore[empty-body]
        """``GET /operations/clone_inline_grid/{task_id}`` → a grid-clone's status (poll to wait).

        The ``task_id`` is the ``operation.id`` returned by ``GridsClient.clone``. Poll until
        ``is_terminal``; on ``success`` the ``result.grid_id`` names the copy.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.operations.gridclone_get("task-1").is_terminal  # doctest: +SKIP
            True
        """
