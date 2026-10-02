"""Forms ``/operations`` client on the httpx2 core — the generic async-operation poll target."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.operations import endpoints

if TYPE_CHECKING:
    from ycli.yandex.forms.operations.models import OperationResult


class OperationsClient(Resource):
    """Read the status of an asynchronous Forms operation."""

    def get(self, operation_id: str) -> OperationResult:
        """``GET /operations/{operation_id}`` → the operation's current :class:`OperationResult`.

        Poll it on the ``id`` an async trigger returned (``answers export --no-wait``) until
        :attr:`OperationResult.is_terminal`.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.operations.get("op-4a1b").is_terminal  # doctest: +SKIP
            True
        """
        return self._session.send(endpoints.get_operation(operation_id))
