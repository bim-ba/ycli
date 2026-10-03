"""Wiki ``/recovery_tokens`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.wiki.recovery import endpoints

if TYPE_CHECKING:
    from ycli.yandex.wiki.recovery.models import RecoveredPage


class RecoveryClient(Resource):
    """Restore a deleted page by its recovery token."""

    def restore(self, token: str) -> RecoveredPage:
        """``POST /recovery_tokens/{token}/recover`` → the restored page and how many came back.

        Redeems a ``recovery_token`` returned by ``PagesClient.delete`` to undo the delete.
        No request body — the token in the path is the whole request.

        Args:
            token: The recovery token ``PagesClient.delete`` returned.

        Returns:
            The restored page's ``id`` and ``slug``, and how many pages were restored.

        Examples:
            >>> wiki.recovery.restore("recovery-token-1").slug
            'eng/restored'
        """
        return self._session.send(endpoints.restore_page(token))
