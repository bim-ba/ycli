"""Declarative Forms /operations client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.forms.base import FormsResource
from ycli.yandex.forms.operations.models import OperationResult


class OperationsClient(FormsResource):
    """Declarative HTTP for ``/operations`` — the generic async-operation poll target."""

    @uplink.returns.json()
    @uplink.get("operations/{operation_id}")
    def get(self, operation_id: uplink.Path) -> OperationResult:  # ty: ignore[empty-body]
        """``GET /operations/{operation_id}`` → the operation's current :class:`OperationResult`.

        Poll this on the ``id`` an async trigger returned (e.g. ``answers export --no-wait``)
        until :attr:`OperationResult.is_terminal`.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.operations.get("op-4a1b").is_ready  # doctest: +SKIP
            True
        """
