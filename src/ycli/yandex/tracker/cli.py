"""Yandex Tracker CLI — mounts the per-resource sub-apps (AppContext DI via ctx.obj)."""

from __future__ import annotations

import typer

from ycli.yandex.tracker.applications.cli import app as applications_app
from ycli.yandex.tracker.attachments.cli import app as attachments_app
from ycli.yandex.tracker.autoactions.cli import app as autoactions_app
from ycli.yandex.tracker.boards.cli import app as boards_app
from ycli.yandex.tracker.bulk.cli import app as bulk_app
from ycli.yandex.tracker.changelog.cli import app as changelog_app
from ycli.yandex.tracker.checklists.cli import app as checklists_app
from ycli.yandex.tracker.columns.cli import app as columns_app
from ycli.yandex.tracker.comments.cli import app as comments_app
from ycli.yandex.tracker.components.cli import app as components_app
from ycli.yandex.tracker.dashboards.cli import app as dashboards_app
from ycli.yandex.tracker.entities.cli import app as entities_app
from ycli.yandex.tracker.fields.cli import app as fields_app
from ycli.yandex.tracker.filters.cli import app as filters_app
from ycli.yandex.tracker.import_.cli import app as import_app
from ycli.yandex.tracker.issues.cli import app as issues_app
from ycli.yandex.tracker.issuetypes.cli import app as issuetypes_app
from ycli.yandex.tracker.links.cli import app as links_app
from ycli.yandex.tracker.linktypes.cli import app as linktypes_app
from ycli.yandex.tracker.localfields.cli import app as localfields_app
from ycli.yandex.tracker.macros.cli import app as macros_app
from ycli.yandex.tracker.me.cli import app as me_app
from ycli.yandex.tracker.priorities.cli import app as priorities_app
from ycli.yandex.tracker.queues.cli import app as queues_app
from ycli.yandex.tracker.remotelinks.cli import app as remotelinks_app
from ycli.yandex.tracker.resolutions.cli import app as resolutions_app
from ycli.yandex.tracker.sprints.cli import app as sprints_app
from ycli.yandex.tracker.statuses.cli import app as statuses_app
from ycli.yandex.tracker.transitions.cli import app as transitions_app
from ycli.yandex.tracker.triggers.cli import app as triggers_app
from ycli.yandex.tracker.users.cli import app as users_app
from ycli.yandex.tracker.worklog.cli import app as worklog_app

app = typer.Typer(name="tracker", help="Yandex Tracker read/write.", no_args_is_help=True)

app.add_typer(me_app)
app.add_typer(issues_app)
app.add_typer(comments_app)
app.add_typer(links_app)
app.add_typer(transitions_app)
app.add_typer(worklog_app)
app.add_typer(changelog_app)
app.add_typer(checklists_app)
app.add_typer(columns_app)
app.add_typer(priorities_app)
app.add_typer(issuetypes_app)
app.add_typer(linktypes_app)
app.add_typer(users_app)
app.add_typer(statuses_app)
app.add_typer(resolutions_app)
app.add_typer(queues_app)
app.add_typer(localfields_app)
app.add_typer(fields_app)
app.add_typer(components_app)
app.add_typer(filters_app)
app.add_typer(applications_app)
app.add_typer(boards_app)
app.add_typer(sprints_app)
app.add_typer(attachments_app)
app.add_typer(macros_app)
app.add_typer(triggers_app)
app.add_typer(autoactions_app)
app.add_typer(bulk_app)
app.add_typer(remotelinks_app)
app.add_typer(import_app)
app.add_typer(dashboards_app)
app.add_typer(entities_app)
