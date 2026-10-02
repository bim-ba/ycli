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
        """``POST /recovery_tokens/{token}/recover`` → the restored page's ``{id, slug}``.

        Redeems a ``recovery_token`` returned by ``PagesClient.delete`` to undo the delete.
        No request body — the token in the path is the whole request.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.recovery.restore("a1b2c3d4-…").slug  # doctest: +SKIP
            'data/x'
        """
        return self._session.send(endpoints.restore_page(token))
