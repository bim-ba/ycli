"""Tracker ``/projects`` client on the httpx2 core (legacy Projects API v3).

The docs point to the unified entities API for projects; this resource wraps the older
endpoints anyway. Every method sends one declaration from :mod:`.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.projects import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.projects.models import (
        Project,
        ProjectCreate,
        ProjectList,
        ProjectUpdate,
    )
    from ycli.yandex.tracker.queues.models import QueueList


class ProjectsClient(Resource):
    """List, get, create, edit and delete projects; list a project's queues."""

    def list(self, *, expand: str | None = None) -> ProjectList:
        """``GET /projects`` → every project of the organization.

        ``expand="queues"`` adds each project's queues.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.projects.list().root[0].name  # doctest: +SKIP
            'Launch'
        """
        return self._session.send(endpoints.list_projects(expand=expand))

    def get(self, project_id: int, *, expand: str | None = None) -> Project:
        """``GET /projects/{project_id}`` → one project.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.projects.get(1).version  # doctest: +SKIP
            2
        """
        return self._session.send(endpoints.get_project(project_id, expand=expand))

    def queues(self, project_id: int, *, expand: str | None = None) -> QueueList:
        """``GET /projects/{project_id}/queues`` → the queues whose issues are in the project.

        ``expand`` takes the same blocks as :meth:`QueuesClient.get` (``all``, ``components``, …).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.projects.queues(1).root[0].key  # doctest: +SKIP
            'TEST'
        """
        return self._session.send(endpoints.list_project_queues(project_id, expand=expand))

    def create(self, body: ProjectCreate) -> Project:
        """``POST /projects`` → create a project from a typed ``ProjectCreate`` body.

        Projects v3 is the legacy API (entities replace it): the test organization accepted
        ``queues`` but bound no queue, so ``queues`` of the new project came back empty.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.projects.create(
            ...     ProjectCreate(name="Launch", queues="TEST")
            ... ).id  # doctest: +SKIP
            '9'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_project(dumped))

    def edit(
        self, project_id: int, body: ProjectUpdate, *, version: int, expand: str | None = None
    ) -> Project:
        """``PUT /projects/{project_id}?version=`` → change the set fields of a project.

        ``version`` is the project's current version; ``body.queues`` is required.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> body = ProjectUpdate(queues="TEST", name="Renamed")
            >>> client.projects.edit(9, body, version=1).version  # doctest: +SKIP
            2
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(
            endpoints.edit_project(project_id, dumped, version=version, expand=expand)
        )

    def delete(self, project_id: int) -> None:
        """``DELETE /projects/{project_id}`` → 204; raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.projects.delete(9)  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_project(project_id))
