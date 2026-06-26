"""Lazy Typer DI for the wiki CLI — builds the WikiClient on first command use (not at --help)."""
from __future__ import annotations

import typer

from ycli.yandex.wiki.client import WikiClient


def wiki_client(ctx: typer.Context) -> WikiClient:
    """Return the request-scoped WikiClient, building it from env on first access.

    Lazy so ``--help`` (which never runs a command body) needs no creds; cached on
    ``ctx.obj`` so multiple accesses within one invocation share the session.

    Example:
        >>> wiki_client(ctx)  # doctest: +SKIP
    """
    if ctx.obj is None:
        ctx.obj = WikiClient.from_env()
    return ctx.obj
