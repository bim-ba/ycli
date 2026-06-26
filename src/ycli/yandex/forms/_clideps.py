"""Lazy Typer DI for the forms CLI."""
from __future__ import annotations

import typer

from ycli.yandex.forms.client import FormsClient


def forms_client(ctx: typer.Context) -> FormsClient:
    """Return the request-scoped FormsClient, building it from env on first access.

    Lazy so ``--help`` (which never runs a command body) needs no creds; cached on
    ``ctx.obj`` so multiple accesses within one invocation share the session.

    Example:
        >>> forms_client(ctx)  # doctest: +SKIP
    """
    if ctx.obj is None:
        ctx.obj = FormsClient.from_env()
    return ctx.obj
