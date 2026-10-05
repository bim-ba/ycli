"""Yandex Forms CLI — mounts the per-resource sub-apps."""

import typer

from ycli.yandex.forms import SERVICE
from ycli.yandex.forms.access.cli import app as access_app
from ycli.yandex.forms.answers.cli import app as answers_app
from ycli.yandex.forms.conditions.cli import app as conditions_app
from ycli.yandex.forms.files.cli import app as files_app
from ycli.yandex.forms.filling.cli import app as filling_app
from ycli.yandex.forms.history.cli import app as history_app
from ycli.yandex.forms.hooks.cli import app as hooks_app
from ycli.yandex.forms.images.cli import app as images_app
from ycli.yandex.forms.keysets.cli import app as keysets_app
from ycli.yandex.forms.me.cli import app as me_app
from ycli.yandex.forms.notifications.cli import app as notifications_app
from ycli.yandex.forms.operations.cli import app as operations_app
from ycli.yandex.forms.questions.cli import app as questions_app
from ycli.yandex.forms.subscriptions.cli import app as subscriptions_app
from ycli.yandex.forms.surveys.cli import app as surveys_app
from ycli.yandex.forms.variables.cli import app as variables_app
from ycli.yandex.status.service_cli import service_auth_app

# Help text lives in the service registry (ycli.yandex.forms.SERVICE).
app = typer.Typer(name="forms", no_args_is_help=True)

app.add_typer(service_auth_app(SERVICE))
app.add_typer(me_app)
app.add_typer(surveys_app)
app.add_typer(questions_app)
app.add_typer(conditions_app)
app.add_typer(access_app)
app.add_typer(history_app)
app.add_typer(answers_app)
app.add_typer(keysets_app)
app.add_typer(operations_app)
app.add_typer(notifications_app)
app.add_typer(files_app)
app.add_typer(images_app)
app.add_typer(filling_app)
app.add_typer(hooks_app)
app.add_typer(subscriptions_app)
app.add_typer(variables_app)
