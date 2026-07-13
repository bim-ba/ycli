"""Tracker users FastMCP tools (reads-only)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, app_config, tracker_client
from ycli.yandex.tracker.users.models import User, UserList

mcp = FastMCP("tracker-users")


@mcp.tool(name="users_get", annotations={**RO, "title": "Get Tracker user"}, tags=TAGS)
def get(
    login_or_id: Annotated[
        str,
        Field(description="User login or numeric uid; for a digits-only login use login:<digits>."),
    ],
    expand: Annotated[
        str | None,
        Field(description="Extra data to include in the response, e.g. groups."),
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> User:
    """Look up a single organisation user account by login or uid, including name, email and
    licence/dismissal status. Use this when you already know one user; use ``users_list`` to
    browse or enumerate the whole directory. Pass ``expand="groups"`` to include the user's groups.

    >>> users_get(login_or_id="username", expand="groups")  # doctest: +SKIP
    """
    return client.users.get(login_or_id=login_or_id, expand=expand)


@mcp.tool(name="users_list", annotations={**RO, "title": "List Tracker users"}, tags=TAGS)
def list_(
    limit: Annotated[
        int,
        Field(description="Max users to return; 0 means the YCLI_MAX_ITEMS cap (default 500)."),
    ] = 0,
    expand: Annotated[
        str | None,
        Field(description="Extra data to include per user, e.g. groups."),
    ] = None,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> UserList:
    """All users registered in the organisation, auto-paginated via the relative id-cursor and
    sorted by ascending uid. Capped at YCLI_MAX_ITEMS (default 500) unless ``limit`` is given; use
    ``users_get`` instead when you already know the specific login or uid.

    >>> users_list(limit=50, expand="groups")  # doctest: +SKIP
    """
    cap = resolve_cap(limit, config.max_items)
    return client.users.list(limit=cap, expand=expand)
