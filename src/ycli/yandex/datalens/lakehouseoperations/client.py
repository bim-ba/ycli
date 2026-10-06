"""DataLens Lakehouse operations client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.lakehouseoperations import endpoints

if TYPE_CHECKING:
    from ycli.yandex.datalens.models import LakehouseOperation


class LakehouseOperationsClient(Resource):
    """Lakehouse operations: what making a cloud environment or a REST catalog started."""

    def get(self, operation_id: str) -> LakehouseOperation:
        """``getLakehouseOperation`` → how far an operation is (experimental, not measured).

        Ask until ``done``; then ``error`` says why it failed, or ``response`` holds what it
        made. An id nothing knows answers ``403 Permission denied``, not ``404``.

        Args:
            operation_id: The operation's id.

        Returns:
            The operation.

        Examples:
            >>> state = datalens.lakehouseoperations.get("op0000000000001")
            >>> state.done, state.error
            (True, None)
        """
        return self._session.send(endpoints.get(operation_id))
