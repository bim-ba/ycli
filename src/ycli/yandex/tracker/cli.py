"""Yandex Tracker CLI — mounts the per-resource sub-apps (lazy client DI via _clideps)."""
from __future__ import annotations

import typer

from ycli.yandex.tracker.changelog.cli import app as changelog_app
from ycli.yandex.tracker.comments.cli import app as comments_app
from ycli.yandex.tracker.issues.cli import app as issues_app
from ycli.yandex.tracker.issuetypes.cli import app as issuetypes_app
from ycli.yandex.tracker.links.cli import app as links_app
from ycli.yandex.tracker.linktypes.cli import app as linktypes_app
from ycli.yandex.tracker.priorities.cli import app as priorities_app
from ycli.yandex.tracker.transitions.cli import app as transitions_app
from ycli.yandex.tracker.worklog.cli import app as worklog_app

app = typer.Typer(name="tracker", help="Yandex Tracker read/write.", no_args_is_help=True)

app.add_typer(issues_app)
app.add_typer(comments_app)
app.add_typer(links_app)
app.add_typer(transitions_app)
app.add_typer(worklog_app)
app.add_typer(changelog_app)
app.add_typer(priorities_app)
app.add_typer(issuetypes_app)
app.add_typer(linktypes_app)
