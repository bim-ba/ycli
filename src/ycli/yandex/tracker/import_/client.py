"""Tracker data-import client on the httpx2 core (admin-only writes).

Every method sends one declaration from :mod:`ycli.yandex.tracker.import_.endpoints`. Import
preserves the source ``createdAt`` / ``createdBy``. The four JSON imports return the canonical
sibling entity model (the worklog import returns ``ItemList[Worklog]``: the live endpoint
answers with a JSON array); the file import is ``multipart/form-data`` with ``filename`` /
``createdAt`` / ``createdBy`` as query parameters.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.import_ import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.attachments.models import Attachment
    from ycli.yandex.tracker.comments.models import Comment
    from ycli.yandex.tracker.issues.models import Issue
    from ycli.yandex.tracker.links.models import Link
    from ycli.yandex.tracker.worklog.models import Worklog


class ImportClient(Resource):
    """The Tracker ``/_import`` endpoints (admin-only)."""

    def task(self, body: dict[str, Any]) -> Issue:
        """``POST /issues/_import`` — import an issue preserving its history. Returns the ``Issue``.

        Args:
            body: The issue fields, including the source ``createdAt`` and ``createdBy``.

        Returns:
            The imported issue.

        Examples:
            >>> tracker.import_.task(
            ...     {
            ...         "queue": "TEST",
            ...         "summary": "Old task",
            ...         "createdAt": "2017-08-29T12:34:41.740+0000",
            ...         "createdBy": "11",
            ...         "key": "TEST-41",
            ...     }
            ... ).key
            'TEST-41'
        """
        return self._session.send(endpoints.import_task(body))

    def comment(self, issue_key: str, body: dict[str, Any]) -> Comment:
        """``POST /issues/{issue_key}/comments/_import`` — import a comment; returns ``Comment``.

        Args:
            issue_key: The issue's key.
            body: The comment fields, including the source ``createdAt`` and ``createdBy``.

        Returns:
            The imported comment.

        Examples:
            >>> tracker.import_.comment(
            ...     "TEST-2",
            ...     {
            ...         "text": "Old comment",
            ...         "createdAt": "2019-02-03T04:05:06.000+0000",
            ...         "createdBy": "13",
            ...     },
            ... ).text
            'Old comment'
        """
        return self._session.send(endpoints.import_comment(issue_key, body))

    def link(self, issue_key: str, body: dict[str, Any]) -> Link:
        """``POST /issues/{issue_key}/links/_import`` — import an issue link. Returns the ``Link``.

        Args:
            issue_key: The issue's key.
            body: The link fields, including the source ``createdAt`` and ``createdBy``.

        Returns:
            The imported link.

        Examples:
            >>> tracker.import_.link(
            ...     "TEST-3",
            ...     {
            ...         "relationship": "depends on",
            ...         "issue": "TEST-4",
            ...         "createdAt": "2020-03-04T05:06:07.000+0000",
            ...         "createdBy": "14",
            ...     },
            ... ).object.key
            'TEST-4'
        """
        return self._session.send(endpoints.import_link(issue_key, body))

    def worklog(self, issue_key: str, body: dict[str, Any]) -> ItemList[Worklog]:
        """``POST /issues/{issue_key}/worklogs/_import`` — import a worklog (note plural path).

        Returns a ``ItemList[Worklog]`` — the live endpoint answers with a JSON **array** of the
        created worklog record(s), not a single object.

        Args:
            issue_key: The issue's key.
            body: The worklog fields, including the source ``createdAt`` and ``createdBy``.

        Returns:
            The created worklog record(s).

        Examples:
            >>> tracker.import_.worklog(
            ...     "TEST-5",
            ...     {
            ...         "duration": "PT2H",
            ...         "createdAt": "2021-04-05T06:07:08.000+0000",
            ...         "createdBy": "15",
            ...         "start": "2021-04-05T09:00:00.000+0000",
            ...     },
            ... ).root[0].duration
            'PT2H'
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

        Args:
            issue_key: The issue's key.
            filename: The attachment's file name.
            created_at: The source creation time.
            created_by: The source author.
            data: The raw file bytes.

        Returns:
            The created attachment.

        Examples:
            >>> tracker.import_.file(
            ...     "JUNE-5",
            ...     filename="renamed.png",
            ...     created_at="2022-05-06T07:08:09.000+0000",
            ...     created_by="16",
            ...     data=b"PNGDATA",
            ... ).name
            'renamed.png'
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

        ``POST /issues/{issue_key}/comments/{comment_id}/attachments/_import`` (multipart);
        ``created_at`` must fall between the comment's creation and its last update (for a
        comment never edited, exactly its ``createdAt``), else Tracker answers 422. Returns the
        created ``Attachment``.

        Args:
            issue_key: The issue's key.
            comment_id: The comment's id.
            filename: The attachment's file name.
            created_at: The source creation time.
            created_by: The source author.
            data: The raw file bytes.

        Returns:
            The created attachment.

        Examples:
            >>> tracker.import_.comment_file(
            ...     "JUNE-7",
            ...     "2238",
            ...     filename="scan.png",
            ...     created_at="2024-07-08T09:10:11.000+0000",
            ...     created_by="18",
            ...     data=b"PNGDATA",
            ... ).name
            'scan.png'
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
