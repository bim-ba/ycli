"""Tracker users FastMCP tools (reads-only)."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import LIMIT_CAP, RO, app_config, new_server, tracker_client
from ycli.yandex.tracker.users.models import User

mcp = new_server("tracker-users")


@mcp.tool(name="users_get", annotations={**RO, "title": "Get Tracker user"})
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
    """Look up a single organisation user account by login or uid.

    The account includes name, email and licence/dismissal status. Use this when you already know
    one user; use ``users_list`` to browse or enumerate the whole directory. Pass
    ``expand="groups"`` to include the user's groups.
    """
    return client.users.get(login_or_id=login_or_id, expand=expand)


@mcp.tool(name="users_list", annotations={**RO, "title": "List Tracker users"})
def list_(
    limit: Annotated[
        int | None,
        Field(ge=1, description=f"Max users to return; {LIMIT_CAP}"),
    ] = None,
    expand: Annotated[
        str | None,
        Field(description="Extra data to include per user, e.g. groups."),
    ] = None,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[User]:
    """All users registered in the organisation, sorted by ascending uid.

    Auto-paginated via the relative id-cursor. Capped at the configured item cap unless ``limit``
    is given; use ``users_get`` instead when you already know the specific login or uid.
    """
    cap = config.http.cap(limit)
    return client.users.list(limit=cap, expand=expand)
