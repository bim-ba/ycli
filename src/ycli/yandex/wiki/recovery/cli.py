"""`wiki recovery` commands — restore a page deleted via `wiki pages delete`."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.models import PageIdentity

app = typer.Typer(
    name="recovery", help="Wiki page recovery (restore by token).", no_args_is_help=True
)


@app.command()
def restore(
    token: Annotated[
        str, typer.Argument(metavar="TOKEN", help="recovery_token from `wiki pages delete`.")
    ],
    *,
    wiki: WikiClient,
) -> PageIdentity:
    """Restore a deleted page by its recovery TOKEN (POST /recovery_tokens/{token}/recover)."""
    return wiki.recovery.restore(token=token)
