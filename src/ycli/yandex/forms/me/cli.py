"""`forms me` commands."""

import typer

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.me.models import User

app = typer.Typer(name="me", help="Forms authenticated user.", no_args_is_help=True)


@app.command()
def get(*, forms: FormsClient) -> User:
    """Print the authenticated user (a safe auth probe)."""
    return forms.me.get()
