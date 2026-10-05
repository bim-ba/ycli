"""Tracker ``/projects`` operations (legacy Projects API v3), each declared once (sans-IO).

Examples:
    >>> get(1, expand="queues").params
    {'expand': 'queues'}
    >>> update(1, {"queues": "TEST"}, version=2).method
    'PUT'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.projects.models import Project, ProjectCreate, ProjectUpdate
from ycli.yandex.tracker.queues.models import Queue


def list_(*, expand: str | None = None) -> Endpoint[ItemList[Project]]:
    return Endpoint("GET", "projects", ItemList[Project], params={"expand": expand})


def get(project_id: int, *, expand: str | None = None) -> Endpoint[Project]:
    return Endpoint("GET", f"projects/{segment(project_id)}", Project, params={"expand": expand})


def queues_list(project_id: int, *, expand: str | None = None) -> Endpoint[ItemList[Queue]]:
    return Endpoint(
        "GET", f"projects/{segment(project_id)}/queues", ItemList[Queue], params={"expand": expand}
    )


def create(body: ProjectCreate) -> Endpoint[Project]:
    return Endpoint("POST", "projects", Project, json=body)


def update(
    project_id: int, body: ProjectUpdate, *, version: int, expand: str | None = None
) -> Endpoint[Project]:
    """``PUT /projects/{id}?version=`` — the lock is required; PUT sets, so it is idempotent."""
    return Endpoint(
        "PUT",
        f"projects/{segment(project_id)}",
        Project,
        json=body,
        params={"version": version, "expand": expand},
    )


def delete(project_id: int) -> Endpoint[None]:
    return Endpoint("DELETE", f"projects/{segment(project_id)}")
