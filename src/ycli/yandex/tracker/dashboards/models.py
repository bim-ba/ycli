"""Pydantic models for Tracker dashboards and their cycle-time widgets."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
)


class Dashboard(APIModel):
    """A Tracker dashboard (``POST /dashboards/`` response).

    Example:
        >>> Dashboard.model_validate({"id": 10, "name": "New Dashboard"}).name
        'New Dashboard'
    """

    self_url: str | None = Field(
        default=None, alias="self", description="API resource address of this dashboard."
    )
    id: int | str | None = Field(default=None, description="Dashboard identifier.")
    version: int | None = Field(
        default=None, description="Dashboard version (bumped on each edit)."
    )
    name: str | None = Field(default=None, description="Dashboard name.")
    layout: str | None = Field(
        default=None, description="Widget layout mode, e.g. ``one-column``, ``two-columns``."
    )
    created_by: DisplayStr = Field(
        default=None, alias="createdBy", description="Display name of the dashboard creator."
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    owner: DisplayStr = Field(default=None, description="Display name of the dashboard owner.")


class Widget(APIModel):
    """A dashboard widget (``POST /dashboards/{id}/widgets/cycleTime`` response).

    Example:
        >>> Widget.model_validate({"id": 123, "description": "My widget"}).description
        'My widget'
    """

    self_url: str | None = Field(
        default=None, alias="self", description="API resource address of this widget."
    )
    id: int | str | None = Field(default=None, description="Widget identifier.")
    version: int | None = Field(default=None, description="Widget version (bumped on each edit).")
    description: str | None = Field(default=None, description="Widget name.")
    dashboard: DisplayStr = Field(
        default=None, description="Display name of the dashboard the widget sits on."
    )
    query: str | None = Field(default=None, description="Query-language filter feeding the widget.")
    start: str | None = Field(
        default=None, description="Calculation start formula, e.g. ``now()-2w``."
    )
    end: str | None = Field(default=None, description="Calculation end formula, e.g. ``now()-2d``.")
    mode: str | None = Field(default=None, description="Data display mode, e.g. ``common-lines``.")


class DashboardOwner(APIModel):
    """The ``owner`` sub-object of a dashboard create body — a ``{"id": <login|id>}`` reference.

    Example:
        >>> DashboardOwner(id="user").model_dump()
        {'id': 'user'}
    """

    id: str = Field(description="Login or id of the dashboard owner.")


class DashboardCreate(APIModel):
    """Typed request body for ``POST /dashboards/`` (create a dashboard).

    Example:
        >>> DashboardCreate(name="Team board", layout="two-columns").model_dump(exclude_none=True)
        {'name': 'Team board', 'layout': 'two-columns'}
    """

    name: str = Field(description="Dashboard name.")
    layout: str | None = Field(
        default=None,
        description="Widget layout: one-column, two-columns, three-columns, "
        "narrow-left-wide-right, one-top-two-bottom.",
    )
    owner: DashboardOwner | None = Field(
        default=None, description="Owner reference; defaults to the creator when omitted."
    )


class CycleTimeWidget(APIModel):
    """Typed request body for ``POST /dashboards/{id}/widgets/cycleTime`` (add a cycle-time chart).

    Example:
        >>> CycleTimeWidget(description="My widget", query="Queue: TEST").model_dump(
        ...     by_alias=True, exclude_none=True
        ... )
        {'description': 'My widget', 'query': 'Queue: TEST'}
    """

    description: str = Field(description="Widget name (required).")
    query: str | None = Field(default=None, description="Query-language filter selecting issues.")
    filter: dict[str, Any] | None = Field(
        default=None, description="Parameter filter ``{field: value}`` selecting issues."
    )
    filter_id: int | None = Field(
        default=None, serialization_alias="filterId", description="Id of a saved filter to use."
    )
    from_statuses: list[dict[str, Any]] | None = Field(
        default=None,
        serialization_alias="fromStatuses",
        description="Statuses the work starts from, as ``[{'key': ...}]``.",
    )
    to_statuses: list[dict[str, Any]] | None = Field(
        default=None,
        serialization_alias="toStatuses",
        description="Statuses the work ends at, as ``[{'key': ...}]``.",
    )
    start: str | None = Field(
        default=None, description="Calculation start formula, e.g. ``now()-2w`` (default 2 years)."
    )
    end: str | None = Field(
        default=None, description="Calculation end formula, e.g. ``now()-2d`` (default ``now()``)."
    )
    mode: str | None = Field(
        default=None,
        description="Display mode: common-lines, common-lines-and-points, status-lines.",
    )
    auto_updatable: bool | None = Field(
        default=None,
        serialization_alias="autoUpdatable",
        description="Whether the chart refreshes automatically.",
    )
