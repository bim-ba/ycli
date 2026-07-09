"""Declarative Yandex Wiki /recovery_tokens client (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly.
"""

import uplink

from ycli.yandex.wiki.base import WikiResource
from ycli.yandex.wiki.recovery.models import RecoveredPage


class RecoveryClient(WikiResource):
    """Declarative HTTP for ``/recovery_tokens`` (restore a deleted page by token)."""

    @uplink.returns.json()
    @uplink.post("recovery_tokens/{token}/recover")
    def restore(self, token: uplink.Path) -> RecoveredPage:  # ty: ignore[empty-body]
        """``POST /recovery_tokens/{token}/recover`` → the restored page's ``{id, slug}``.

        Redeems a ``recovery_token`` returned by ``PagesClient.delete`` to undo the delete.
        No request body — the token in the path is the whole request.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.recovery.restore("a1b2c3d4-…").slug  # doctest: +SKIP
            'data/x'
        """
