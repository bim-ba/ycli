"""Yandex Forms CLI — mounts the per-resource sub-apps (AppContext DI via ctx.obj)."""

from __future__ import annotations

import typer

from ycli.yandex.forms.answers.cli import app as answers_app
from ycli.yandex.forms.me.cli import app as me_app
from ycli.yandex.forms.questions.cli import app as questions_app
from ycli.yandex.forms.surveys.cli import app as surveys_app

app = typer.Typer(name="forms", help="Yandex Forms read.", no_args_is_help=True)

app.add_typer(me_app)
app.add_typer(surveys_app)
app.add_typer(questions_app)
app.add_typer(answers_app)
