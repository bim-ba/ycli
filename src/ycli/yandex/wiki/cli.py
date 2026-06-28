"""Yandex Wiki CLI — mounts the per-resource sub-apps (AppContext DI via ctx.obj)."""
from __future__ import annotations

import typer

from ycli.yandex.wiki.attachments.cli import app as attachments_app
from ycli.yandex.wiki.comments.cli import app as comments_app
from ycli.yandex.wiki.me.cli import app as me_app
from ycli.yandex.wiki.pages.cli import app as pages_app

app = typer.Typer(name="wiki", help="Yandex Wiki API.", no_args_is_help=True)

app.add_typer(me_app)
app.add_typer(pages_app)
app.add_typer(comments_app)
app.add_typer(attachments_app)
