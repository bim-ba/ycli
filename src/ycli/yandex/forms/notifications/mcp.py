"""Forms notifications FastMCP tools (reads + restart and cancel, honest hints)."""

from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import RO, TAGS, WRITE, WRITE_TAGS, app_config, forms_client
from ycli.yandex.forms.notifications.models import (
    Notification,
    NotificationAction,
    NotificationDetails,
    NotificationStatus,
)
from ycli.yandex.models import ItemList

mcp = FastMCP("forms-notifications")

NotificationId = Annotated[
    int, Field(description="Notification id (integer) from notifications_list.")
]
Status = Literal["pending", "success", "error", "canceled"]
IntegrationType = Literal[
    "email", "tracker", "tracker_comment", "wiki", "jsonrpc", "post", "put", "http", "function"
]


@mcp.tool(
    name="notifications_list",
    annotations={**RO, "title": "List Forms integration runs"},
    tags=TAGS,
)
def list_(
    survey_id: Annotated[
        str | None, Field(description="Only this form's runs (24-char hex).")
    ] = None,
    hook_id: Annotated[int | None, Field(description="Only this integration group.")] = None,
    subscription_id: Annotated[int | None, Field(description="Only this integration.")] = None,
    answer_id: Annotated[int | None, Field(description="Only runs for this answer.")] = None,
    status: Annotated[list[Status] | None, Field(description="Only runs in these states.")] = None,
    created_since: Annotated[str | None, Field(description="ISO-8601: queued at or after.")] = None,
    created_until: Annotated[
        str | None, Field(description="ISO-8601: queued at or before.")
    ] = None,
    finished_since: Annotated[str | None, Field(description="ISO-8601: ended at or after.")] = None,
    finished_until: Annotated[
        str | None, Field(description="ISO-8601: ended at or before.")
    ] = None,
    visible: Annotated[
        bool | None, Field(description="True: only shown runs; false: only hidden ones.")
    ] = None,
    integration_type: Annotated[
        IntegrationType | None, Field(description="Only runs of this integration type.")
    ] = None,
    ordering: Annotated[
        Literal["asc", "desc"] | None,
        Field(description="asc (oldest first, the API default) or desc."),
    ] = None,
    limit: Annotated[int, Field(description="Most runs to return (0 = the configured cap).")] = 0,
    client: FormsClient = Depends(forms_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[Notification]:
    """Runs of a form's integrations (one per answer and integration), across pages.

    Capped at the configured item cap unless ``limit`` is given. Read one run's context,
    response and error with ``notifications_get``.
    """
    cap = config.http.cap(limit)
    return client.notifications.list(
        survey_id=survey_id,
        hook_id=hook_id,
        subscription_id=subscription_id,
        answer_id=answer_id,
        status=list(status) if status else None,
        created_since=created_since,
        created_until=created_until,
        finished_since=finished_since,
        finished_until=finished_until,
        visible=visible,
        integration_type=integration_type,
        ordering=ordering,
        limit=cap,
    )


@mcp.tool(
    name="notifications_get",
    annotations={**RO, "title": "Get a Forms integration run"},
    tags=TAGS,
)
def get(
    notification_id: NotificationId, client: FormsClient = Depends(forms_client)
) -> NotificationDetails:
    """One integration run with what the integration was given, answered and failed with."""
    return client.notifications.get(notification_id)


@mcp.tool(
    name="notifications_status_get",
    annotations={**RO, "title": "Get a Forms integration run state"},
    tags=TAGS,
)
def status_get(
    notification_id: NotificationId, client: FormsClient = Depends(forms_client)
) -> NotificationStatus:
    """The state of one integration run: pending, success, error or canceled."""
    return client.notifications.status_get(notification_id)


@mcp.tool(
    name="notifications_restart",
    annotations={**WRITE, "title": "Restart a Forms integration run"},
    tags=WRITE_TAGS,
)
def restart(
    notification_id: NotificationId, client: FormsClient = Depends(forms_client)
) -> NotificationAction:
    """Run the integration again for that answer.

    A ``result.status`` of ``operation`` means it runs in the background: poll
    ``result.operation_id`` with ``operations_get``.
    """
    return client.notifications.restart(notification_id)


@mcp.tool(
    name="notifications_cancel",
    annotations={**WRITE, "title": "Cancel a Forms integration run"},
    tags=WRITE_TAGS,
)
def cancel(
    notification_id: NotificationId, client: FormsClient = Depends(forms_client)
) -> NotificationAction:
    """Stop an integration run that has not finished.

    A run that is already canceled or finished answers ``result.status`` ``skip``.
    """
    return client.notifications.cancel(notification_id)


@mcp.tool(
    name="notifications_errors_list",
    annotations={**RO, "title": "List a Forms survey's failed integration runs"},
    tags=TAGS,
)
def errors_list(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    client: FormsClient = Depends(forms_client),
) -> ItemList[int]:
    """Ids of a form's failed integration runs that are still shown.

    Read each with ``notifications_get``.
    """
    return client.notifications.errors_list(survey_id)
