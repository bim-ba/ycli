"""Declarative Tracker data-import client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.

Every method here is an admin-only WRITE (import preserves the source ``createdAt`` /
``createdBy``). The four JSON imports return the canonical sibling entity model; the file
import is ``multipart/form-data`` — the file bytes ride in a :class:`uplink.Part`, while
``filename`` / ``createdAt`` / ``createdBy`` are query parameters (the public :meth:`file`
wrapper hides the ``uplink.Part`` mechanics).
"""

import uplink

from ycli.yandex.tracker.attachments.models import Attachment
from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.comments.models import Comment
from ycli.yandex.tracker.issues.models import Issue
from ycli.yandex.tracker.links.models import Link
from ycli.yandex.tracker.worklog.models import Worklog


class ImportClient(TrackerResource):
    """Declarative HTTP for the Tracker ``/_import`` endpoints (admin-only)."""

    @uplink.returns.json()
    @uplink.json
    @uplink.post("issues/_import")
    def task(self, body: uplink.Body) -> Issue:  # ty: ignore[empty-body]
        """``POST /issues/_import`` — import an issue preserving its history. Returns the ``Issue``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.import_.task(
            ...     {"queue": "TEST", "summary": "T", "createdAt": "…", "createdBy": "11"}
            ... ).key  # doctest: +SKIP
            'TEST-1'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("issues/{issue_key}/comments/_import")
    def comment(self, issue_key: uplink.Path, body: uplink.Body) -> Comment:  # ty: ignore[empty-body]
        """``POST /issues/{issue_key}/comments/_import`` — import a comment; returns ``Comment``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.import_.comment(
            ...     "TEST-1", {"text": "T", "createdAt": "…", "createdBy": "11"}
            ... ).text  # doctest: +SKIP
            'T'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("issues/{issue_key}/links/_import")
    def link(self, issue_key: uplink.Path, body: uplink.Body) -> Link:  # ty: ignore[empty-body]
        """``POST /issues/{issue_key}/links/_import`` — import an issue link. Returns the ``Link``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.import_.link(
            ...     "TEST-1",
            ...     {
            ...         "relationship": "relates",
            ...         "issue": "TEST-2",
            ...         "createdAt": "…",
            ...         "createdBy": "11",
            ...     },
            ... ).object_key  # doctest: +SKIP
            'TEST-2'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("issues/{issue_key}/worklogs/_import")
    def worklog(self, issue_key: uplink.Path, body: uplink.Body) -> Worklog:  # ty: ignore[empty-body]
        """``POST /issues/{issue_key}/worklogs/_import`` — import a worklog (note plural path).

        Returns the created ``Worklog``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.import_.worklog(
            ...     "TEST-1",
            ...     {"duration": "PT1H", "createdAt": "…", "createdBy": "u", "start": "…"},
            ... ).duration  # doctest: +SKIP
            'PT1H'
        """

    @uplink.returns.json()
    @uplink.multipart
    @uplink.post("issues/{issue_key}/attachments/_import")
    def _file(
        self,
        issue_key: uplink.Path,
        filename: uplink.Query,
        created_at: uplink.Query("createdAt"),  # ty: ignore[invalid-type-form]
        created_by: uplink.Query("createdBy"),  # ty: ignore[invalid-type-form]
        file_data: uplink.Part,
    ) -> Attachment:  # ty: ignore[empty-body]
        """``POST …/attachments/_import`` (multipart; internal — callers use :meth:`file`)."""

    def file(
        self,
        issue_key: str,
        *,
        filename: str,
        created_at: str,
        created_by: str,
        data: bytes,
    ) -> Attachment:
        """Import a file (multipart/form-data) preserving its ``createdAt`` / ``createdBy``.

        ``data`` are the raw file bytes; ``filename`` / ``created_at`` / ``created_by`` become
        query parameters. Returns the created ``Attachment``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.import_.file(
            ...     "JUNE-2", filename="pic.png", created_at="…", created_by="11", data=b"…"
            ... ).name  # doctest: +SKIP
            'pic.png'
        """
        return self._file(
            issue_key,
            filename=filename,
            created_at=created_at,
            created_by=created_by,
            file_data=data,
        )
