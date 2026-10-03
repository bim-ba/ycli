"""Tracker ``/projects`` operations (legacy Projects API v3), each declared once (sans-IO).

Examples:
    >>> get_project(1, expand="queues").params
    {'expand': 'queues'}
    >>> edit_project(1, {"queues": "TEST"}, version=2).method
    'PUT'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.projects.models import Project
from ycli.yandex.tracker.queues.models import Queue


def list_projects(*, expand: str | None = None) -> Endpoint[ItemList[Project]]:
    return Endpoint("GET", "projects", ItemList[Project], params={"expand": expand})


def get_project(project_id: int, *, expand: str | None = None) -> Endpoint[Project]:
    return Endpoint("GET", f"projects/{segment(project_id)}", Project, params={"expand": expand})


def list_project_queues(project_id: int, *, expand: str | None = None) -> Endpoint[ItemList[Queue]]:
    return Endpoint(
        "GET", f"projects/{segment(project_id)}/queues", ItemList[Queue], params={"expand": expand}
    )


def create_project(body: dict[str, Any]) -> Endpoint[Project]:
    return Endpoint("POST", "projects", Project, json=body)


def edit_project(
    project_id: int, body: dict[str, Any], *, version: int, expand: str | None = None
) -> Endpoint[Project]:
    """``PUT /projects/{id}?version=`` — the lock is required; PUT sets, so it is idempotent."""
    return Endpoint(
        "PUT",
        f"projects/{segment(project_id)}",
        Project,
        json=body,
        params={"version": version, "expand": expand},
    )


def delete_project(project_id: int) -> Endpoint[None]:
    return Endpoint("DELETE", f"projects/{segment(project_id)}")
