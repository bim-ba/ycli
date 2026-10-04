"""Tracker ``/projects`` client on the httpx2 core (legacy Projects API v3).

The docs point to the unified entities API for projects; this resource wraps the older
endpoints anyway. Every method sends one declaration from :mod:`.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.projects import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.projects.models import Project, ProjectCreate, ProjectUpdate
    from ycli.yandex.tracker.queues.models import Queue


class ProjectsClient(Resource):
    """List, get, create, update and delete projects; list a project's queues."""

    def list(self, *, expand: str | None = None) -> ItemList[Project]:
        """``GET /projects`` → every project of the organization.

        ``expand="queues"`` adds each project's queues.

        Args:
            expand: Extra blocks to include; ``"queues"`` adds each project's queues.

        Returns:
            Every project.

        Examples:
            >>> tracker.projects.list(expand="queues").root[0].name
            'Project'
        """
        return self._session.send(endpoints.list_(expand=expand))

    def get(self, project_id: int, *, expand: str | None = None) -> Project:
        """``GET /projects/{project_id}`` → one project.

        Args:
            project_id: The project's id.
            expand: Extra blocks to include, as in :meth:`list`.

        Returns:
            The project.

        Examples:
            >>> tracker.projects.get(21, expand="queues").version
            1
        """
        return self._session.send(endpoints.get(project_id, expand=expand))

    def queues(self, project_id: int, *, expand: str | None = None) -> ItemList[Queue]:
        """``GET /projects/{project_id}/queues`` → the queues whose issues are in the project.

        ``expand`` takes the same blocks as :meth:`QueuesClient.get` (``all``, ``components``, …).

        Args:
            project_id: The project's id.
            expand: Extra queue blocks to include.

        Returns:
            The project's queues.

        Examples:
            >>> tracker.projects.queues(23, expand="components,versions").root[0].key
            'ORG'
        """
        return self._session.send(endpoints.queues(project_id, expand=expand))

    def create(self, body: ProjectCreate) -> Project:
        """``POST /projects`` → create a project from a typed ``ProjectCreate`` body.

        Projects v3 is the legacy API (entities replace it): the test organization accepted
        ``queues`` but bound no queue, so ``queues`` of the new project came back empty.

        Args:
            body: The new project's name, queues and optional fields.

        Returns:
            The created project.

        Examples:
            >>> from ycli.yandex.tracker.projects.models import ProjectCreate
            >>> tracker.projects.create(ProjectCreate(name="Launch", queues="LAUNCH")).id
            '9'
        """
        return self._session.send(endpoints.create(body))

    def update(
        self, project_id: int, body: ProjectUpdate, *, version: int, expand: str | None = None
    ) -> Project:
        """``PUT /projects/{project_id}?version=`` → change the set fields of a project.

        ``version`` is the project's current version; ``body.queues`` is required.

        Args:
            project_id: The project's id.
            body: The fields to change; ``queues`` is required.
            version: The project's current version.
            expand: Extra blocks to include, as in :meth:`list`.

        Returns:
            The updated project.

        Examples:
            >>> from ycli.yandex.tracker.projects.models import ProjectUpdate
            >>> body = ProjectUpdate(queues="EDITQ", name="Renamed")
            >>> tracker.projects.update(31, body, version=5, expand="queues").version
            6
        """
        return self._session.send(
            endpoints.update(project_id, body, version=version, expand=expand)
        )

    def delete(self, project_id: int) -> None:
        """``DELETE /projects/{project_id}`` → 204; raises on non-2xx.

        Args:
            project_id: The project's id.

        Examples:
            >>> tracker.projects.delete(33)
        """
        self._session.send(endpoints.delete(project_id))
