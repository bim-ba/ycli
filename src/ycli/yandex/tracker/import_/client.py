"""Tracker data-import client on the httpx2 core (admin-only writes).

Every method sends one declaration from :mod:`ycli.yandex.tracker.import_.endpoints`. Import
preserves the source ``createdAt`` / ``createdBy``. The four JSON imports return the canonical
sibling entity model (the worklog import returns ``WorklogList`` — the live endpoint answers with
a JSON array); the file import is ``multipart/form-data`` with ``filename`` / ``createdAt`` /
``createdBy`` as query parameters.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.import_ import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.attachments.models import Attachment
    from ycli.yandex.tracker.comments.models import Comment
    from ycli.yandex.tracker.issues.models import Issue
    from ycli.yandex.tracker.links.models import Link
    from ycli.yandex.tracker.worklog.models import WorklogList


class ImportClient(Resource):
    """The Tracker ``/_import`` endpoints (admin-only)."""

    def task(self, body: dict[str, Any]) -> Issue:
        """``POST /issues/_import`` — import an issue preserving its history. Returns the ``Issue``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.import_.task(
            ...     {"queue": "TEST", "summary": "T", "createdAt": "…", "createdBy": "11"}
            ... ).key  # doctest: +SKIP
            'TEST-1'
        """
        return self._session.send(endpoints.import_task(body))

    def comment(self, issue_key: str, body: dict[str, Any]) -> Comment:
        """``POST /issues/{issue_key}/comments/_import`` — import a comment; returns ``Comment``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.import_.comment(
            ...     "TEST-1", {"text": "T", "createdAt": "…", "createdBy": "11"}
            ... ).text  # doctest: +SKIP
            'T'
        """
        return self._session.send(endpoints.import_comment(issue_key, body))

    def link(self, issue_key: str, body: dict[str, Any]) -> Link:
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
        return self._session.send(endpoints.import_link(issue_key, body))

    def worklog(self, issue_key: str, body: dict[str, Any]) -> WorklogList:
        """``POST /issues/{issue_key}/worklogs/_import`` — import a worklog (note plural path).

        Returns a ``WorklogList`` — the live endpoint answers with a JSON **array** of the
        created worklog record(s), not a single object.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.import_.worklog(
            ...     "TEST-1",
            ...     {"duration": "PT1H", "createdAt": "…", "createdBy": "u", "start": "…"},
            ... ).root[0].duration  # doctest: +SKIP
            'PT1H'
        """
        return self._session.send(endpoints.import_worklog(issue_key, body))

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
        endpoint = endpoints.import_file(
            issue_key,
            filename=filename,
            created_at=created_at,
            created_by=created_by,
            data=data,
        )
        return self._session.send(endpoint)

    def comment_file(
        self,
        issue_key: str,
        comment_id: str,
        *,
        filename: str,
        created_at: str,
        created_by: str,
        data: bytes,
    ) -> Attachment:
        """Import a file onto a comment, preserving its ``createdAt`` / ``createdBy``.

        ``POST /issues/{issue_key}/comments/{comment_id}/attachments/_import`` (multipart); the
        times must fall after the comment's creation and before its last update. Returns the
        created ``Attachment``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.import_.comment_file(
            ...     "JUNE-2", "2238", filename="pic.png", created_at="…", created_by="11", data=b"…"
            ... ).name  # doctest: +SKIP
            'pic.png'
        """
        endpoint = endpoints.import_comment_file(
            issue_key,
            comment_id,
            filename=filename,
            created_at=created_at,
            created_by=created_by,
            data=data,
        )
        return self._session.send(endpoint)
