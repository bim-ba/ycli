"""Yandex Forms CLI — mounts the per-resource sub-apps (AppContext DI via ctx.obj)."""

from __future__ import annotations

import typer

from ycli.yandex.forms.answers.cli import app as answers_app
from ycli.yandex.forms.conditions.cli import app as conditions_app
from ycli.yandex.forms.files.cli import app as files_app
from ycli.yandex.forms.filling.cli import app as filling_app
from ycli.yandex.forms.images.cli import app as images_app
from ycli.yandex.forms.keysets.cli import app as keysets_app
from ycli.yandex.forms.me.cli import app as me_app
from ycli.yandex.forms.operations.cli import app as operations_app
from ycli.yandex.forms.questions.cli import app as questions_app
from ycli.yandex.forms.surveys.cli import app as surveys_app

app = typer.Typer(name="forms", help="Yandex Forms read.", no_args_is_help=True)

app.add_typer(me_app)
app.add_typer(surveys_app)
app.add_typer(questions_app)
app.add_typer(conditions_app)
app.add_typer(answers_app)
app.add_typer(keysets_app)
app.add_typer(operations_app)
app.add_typer(files_app)
app.add_typer(images_app)
app.add_typer(filling_app)
