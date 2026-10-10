"""Forms notifications FastMCP tools (reads + restart and cancel, honest hints)."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import (
    RO,
    WRITE,
    All,
    Next,
    app_config,
    forms_client,
    new_server,
)
from ycli.yandex.forms.models import IntegrationType, RunStatus
from ycli.yandex.forms.notifications.models import (
    Notification,
    NotificationAction,
    NotificationDetails,
    NotificationStatus,
)
from ycli.yandex.models import ItemList, Listed, SortDirection

mcp = new_server("forms-notifications")

NotificationID = Annotated[
    int, Field(description="Notification id (integer) from notifications_list.")
]


@mcp.tool(
    name="notifications_list",
    annotations={**RO, "title": "List Forms integration runs"},
)
def list_(
    survey_id: Annotated[
        str | None,
        Field(description="The form whose runs to list (24-char hex); without it, 404."),
    ] = None,
    hook_id: Annotated[int | None, Field(description="Only this integration group.")] = None,
    subscription_id: Annotated[int | None, Field(description="Only this integration.")] = None,
    answer_id: Annotated[int | None, Field(description="Only runs for this answer.")] = None,
    status: Annotated[
        list[RunStatus] | None, Field(description="Only runs in these states.")
    ] = None,
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
        SortDirection | None,
        Field(description="asc (oldest first, the API default) or desc."),
    ] = None,
    limit: Annotated[
        int | None, Field(ge=1, description="Most runs to return (omitted: the configured cap).")
    ] = None,
    all: All = False,
    next: Next = None,
    client: FormsClient = Depends(forms_client),
    config: AppConfig = Depends(app_config),
) -> Listed[Notification]:
    """Runs of a form's integrations (one per answer and integration), across pages.

    Give ``survey_id``: without it the API answers 404 Not Found, and the other filters only
    narrow that form's runs. Capped at the configured item cap unless ``limit`` is given. Read
    one run's context, response and error with ``notifications_get``.
    """
    cap = config.http.tool_cap(limit, all_=all)
    return client.notifications.list(
        survey_id=survey_id,
        hook_id=hook_id,
        subscription_id=subscription_id,
        answer_id=answer_id,
        status=status,
        created_since=created_since,
        created_until=created_until,
        finished_since=finished_since,
        finished_until=finished_until,
        visible=visible,
        integration_type=integration_type,
        ordering=ordering,
        limit=cap,
        next=next,
    ).collect()


@mcp.tool(
    name="notifications_get",
    annotations={**RO, "title": "Get a Forms integration run"},
)
def get(
    notification_id: NotificationID, client: FormsClient = Depends(forms_client)
) -> NotificationDetails:
    """One integration run with what the integration was given, answered and failed with."""
    return client.notifications.get(notification_id)


@mcp.tool(
    name="notifications_status_get",
    annotations={**RO, "title": "Get a Forms integration run state"},
)
def status_get(
    notification_id: NotificationID, client: FormsClient = Depends(forms_client)
) -> NotificationStatus:
    """The state of one integration run: pending, success, error or canceled."""
    return client.notifications.status_get(notification_id)


@mcp.tool(
    name="notifications_restart",
    annotations={**WRITE, "title": "Restart a Forms integration run"},
)
def restart(
    notification_id: NotificationID, client: FormsClient = Depends(forms_client)
) -> NotificationAction:
    """Run the integration again for that answer.

    A ``result.status`` of ``operation`` means it runs in the background: poll
    ``result.operation_id`` with ``operations_get``.
    """
    return client.notifications.restart(notification_id)


@mcp.tool(
    name="notifications_cancel",
    annotations={**WRITE, "title": "Cancel a Forms integration run"},
)
def cancel(
    notification_id: NotificationID, client: FormsClient = Depends(forms_client)
) -> NotificationAction:
    """Stop an integration run that has not finished.

    A run that is already canceled or finished answers ``result.status`` ``skip``.
    """
    return client.notifications.cancel(notification_id)


@mcp.tool(
    name="notifications_errors_list",
    annotations={**RO, "title": "List a Forms survey's failed integration runs"},
)
def errors_list(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    client: FormsClient = Depends(forms_client),
) -> ItemList[int]:
    """Ids of a form's failed integration runs that are still shown.

    Read each with ``notifications_get``.
    """
    return client.notifications.errors_list(survey_id)
