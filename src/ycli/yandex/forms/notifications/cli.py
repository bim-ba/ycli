"""`forms notifications` commands: the runs of a form's integrations (reads + restart, cancel)."""

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption, values_option
from ycli.settings import AppConfig
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.models import IntegrationType, RunStatus
from ycli.yandex.forms.notifications.models import (
    Notification,
    NotificationAction,
    NotificationDetails,
    NotificationFilter,
    NotificationStatus,
)
from ycli.yandex.forms.typedefs import NotificationIDArg, SurveyIDArg
from ycli.yandex.models import ItemList, SortDirection

app = typer.Typer(
    name="notifications", help="Forms integration runs (notifications).", no_args_is_help=True
)


@app.command("list")
def list_(
    survey_id: Annotated[
        str | None, typer.Option(help="Only this form's runs (24-char hex id).")
    ] = None,
    hook_id: Annotated[int | None, typer.Option(help="Only this integration group.")] = None,
    subscription_id: Annotated[int | None, typer.Option(help="Only this integration.")] = None,
    answer_id: Annotated[int | None, typer.Option(help="Only runs for this answer.")] = None,
    status: Annotated[
        list[str] | None,
        values_option(RunStatus, "--status", help="Only runs in this state (repeatable)."),
    ] = None,
    created_since: Annotated[str | None, typer.Option(help="ISO-8601: queued at or after.")] = None,
    created_until: Annotated[
        str | None, typer.Option(help="ISO-8601: queued at or before.")
    ] = None,
    finished_since: Annotated[str | None, typer.Option(help="ISO-8601: ended at or after.")] = None,
    finished_until: Annotated[
        str | None, typer.Option(help="ISO-8601: ended at or before.")
    ] = None,
    visible: Annotated[
        bool | None,
        typer.Option("--visible/--no-visible", help="Only shown (or only hidden) runs."),
    ] = None,
    integration_type: Annotated[
        str | None,
        values_option(
            IntegrationType, "--integration-type", help="Only runs of this kind of integration."
        ),
    ] = None,
    ordering: Annotated[
        str | None, values_option(SortDirection, help="asc is oldest first, the default.")
    ] = None,
    limit: LimitOption = None,
    all_: AllOption = False,
    *,
    config: AppConfig,
    forms: FormsClient,
) -> ItemList[Notification]:
    """List integration runs, filtered (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return forms.notifications.list(
        NotificationFilter(
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
        ),
        limit=cap,
    )


@app.command()
def get(notification_id: NotificationIDArg, *, forms: FormsClient) -> NotificationDetails:
    """Print one run with its context, response and error."""
    return forms.notifications.get(notification_id)


@app.command()
def status_get(notification_id: NotificationIDArg, *, forms: FormsClient) -> NotificationStatus:
    """Print a run's state only (pending, success, error or canceled)."""
    return forms.notifications.status_get(notification_id)


@app.command()
def restart(notification_id: NotificationIDArg, *, forms: FormsClient) -> NotificationAction:
    """Run the integration again for that answer (POST /notifications/{id}/restart)."""
    return forms.notifications.restart(notification_id)


@app.command()
def cancel(notification_id: NotificationIDArg, *, forms: FormsClient) -> NotificationAction:
    """Stop a run that has not finished (POST /notifications/{id}/cancel)."""
    return forms.notifications.cancel(notification_id)


@app.command()
def errors_list(survey_id: SurveyIDArg, *, forms: FormsClient) -> ItemList[int]:
    """List the ids of form SURVEY_ID's failed runs; read each with `notifications get`."""
    return forms.notifications.errors_list(survey_id)
