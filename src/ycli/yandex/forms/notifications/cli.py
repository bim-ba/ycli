"""`forms notifications` commands: the runs of a form's integrations (reads + restart, cancel)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.notifications.models import (
    NotificationAction,
    NotificationDetails,
    NotificationIdList,
    NotificationList,
    NotificationStatus,
)
from ycli.yandex.forms.typedefs import NotificationIdArg, SurveyIdArg

app = typer.Typer(
    name="notifications", help="Forms integration runs (notifications).", no_args_is_help=True
)


@app.command("list")
def list_(
    survey_id: Annotated[str, typer.Option(help="Only this form's runs (24-char hex id).")] = "",
    hook_id: Annotated[int | None, typer.Option(help="Only this integration group.")] = None,
    subscription_id: Annotated[int | None, typer.Option(help="Only this integration.")] = None,
    answer_id: Annotated[int | None, typer.Option(help="Only runs for this answer.")] = None,
    status: Annotated[
        list[str] | None,
        typer.Option("--status", help="pending, success, error or canceled (repeatable)."),
    ] = None,
    created_since: Annotated[str, typer.Option(help="ISO-8601: queued at or after.")] = "",
    created_until: Annotated[str, typer.Option(help="ISO-8601: queued at or before.")] = "",
    finished_since: Annotated[str, typer.Option(help="ISO-8601: ended at or after.")] = "",
    finished_until: Annotated[str, typer.Option(help="ISO-8601: ended at or before.")] = "",
    visible: Annotated[
        bool | None,
        typer.Option("--visible/--no-visible", help="Only shown (or only hidden) runs."),
    ] = None,
    integration_type: Annotated[
        str,
        typer.Option(
            "--type",
            help="email, tracker, tracker_comment, wiki, jsonrpc, http or function.",
        ),
    ] = "",
    ordering: Annotated[str, typer.Option(help="asc (oldest first, the default) or desc.")] = "",
    limit: LimitOption = 0,
    all_: AllOption = False,
    *,
    config: AppConfig,
    forms: FormsClient,
) -> NotificationList:
    """List integration runs, filtered (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return forms.notifications.list(
        survey_id=survey_id or None,
        hook_id=hook_id,
        subscription_id=subscription_id,
        answer_id=answer_id,
        status=status,
        created_since=created_since or None,
        created_until=created_until or None,
        finished_since=finished_since or None,
        finished_until=finished_until or None,
        visible=visible,
        integration_type=integration_type or None,
        ordering=ordering or None,
        limit=cap,
    )


@app.command()
def get(notification_id: NotificationIdArg, *, forms: FormsClient) -> NotificationDetails:
    """Print one run with its context, response and error."""
    return forms.notifications.get(notification_id)


@app.command()
def status(notification_id: NotificationIdArg, *, forms: FormsClient) -> NotificationStatus:
    """Print a run's state only (pending, success, error or canceled)."""
    return forms.notifications.status_get(notification_id)


@app.command()
def restart(notification_id: NotificationIdArg, *, forms: FormsClient) -> NotificationAction:
    """Run the integration again for that answer (POST /notifications/{id}/restart)."""
    return forms.notifications.restart(notification_id)


@app.command()
def cancel(notification_id: NotificationIdArg, *, forms: FormsClient) -> NotificationAction:
    """Stop a run that has not finished (POST /notifications/{id}/cancel)."""
    return forms.notifications.cancel(notification_id)


@app.command()
def errors(survey_id: SurveyIdArg, *, forms: FormsClient) -> NotificationIdList:
    """List the ids of form SURVEY_ID's failed runs; read each with `notifications get`."""
    return forms.notifications.errors_list(survey_id)
