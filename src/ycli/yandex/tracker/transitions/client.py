"""Declarative Tracker issue-transitions client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.

NOTE: ``execute`` uses ``builtins.list`` explicitly because the ``list`` method in this
class shadows ``builtins.list`` in the class namespace — uplink resolves annotations
eagerly at class-definition time, so ``-> list:`` on ``execute`` would resolve to the
uplink ``RequestDefinitionBuilder`` from the ``list`` method above it.
"""
import builtins

import uplink

from ycli.yandex.tracker._base import TrackerResource
from ycli.yandex.tracker.transitions.models import TransitionList


class TransitionsClient(TrackerResource):
    """Declarative HTTP for ``/issues/{key}/transitions``."""

    @uplink.returns.json()
    @uplink.get("issues/{key}/transitions")
    def list(self, key: uplink.Path) -> TransitionList:  # ty: ignore[empty-body]
        """``GET /issues/{key}/transitions`` → available transitions.

        Example:
            >>> client = TrackerClient.from_env()  # doctest: +SKIP
            >>> client.transitions.list(key="DATAENGINEERING-1").root[0].id  # doctest: +SKIP
            'start_progress'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("issues/{key}/transitions/{transition_id}/_execute")
    def execute(
        self, key: uplink.Path, transition_id: uplink.Path, body: uplink.Body
    ) -> builtins.list:  # ty: ignore[empty-body]
        """``POST /issues/{key}/transitions/{id}/_execute`` → raw JSON (post-move transitions).

        Return type is ``builtins.list`` (not ``list[Any]``) — two reasons:
        1. ``list[Any]`` raises ``TypeError`` at class-definition time (uplink tries to subscript).
        2. Bare ``list`` would resolve to ``TransitionsClient.list`` (the method above this one)
           because uplink evaluates annotations eagerly in class scope. ``builtins.list`` is
           unambiguous. Runtime value is ``list[Any]``.

        Example:
            >>> client = TrackerClient.from_env()  # doctest: +SKIP
            >>> client.transitions.execute("DATAENGINEERING-1", "start_progress", {})[0]["id"]  # doctest: +SKIP
            'stop_progress'
        """
