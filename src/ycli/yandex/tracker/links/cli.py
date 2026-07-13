"""`tracker links` commands."""

from __future__ import annotations

import enum
from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.models import Ack
from ycli.yandex.tracker.links.models import LinkCreate
from ycli.yandex.tracker.typedefs import (
    KeyArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)

app = typer.Typer(name="links", help="Tracker issue links.", no_args_is_help=True)


class Relationship(enum.StrEnum):
    """Link relationship verbs accepted by ``POST /issues/{key}/links``."""

    DEPENDS_ON = "depends on"
    IS_DEPENDENT_BY = "is dependent by"
    RELATES = "relates"
    DUPLICATES = "duplicates"
    IS_DUPLICATED_BY = "is duplicated by"
    SUBTASK = "subtask"
    PARENT = "parent"


@app.command("list")
def list_(ctx: typer.Context, key: KeyArg) -> None:
    """List links for issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.links.list(key), app_ctx.strategy, app_ctx.console)


@app.command()
def add(
    ctx: typer.Context,
    key: KeyArg,
    relationship: Annotated[Relationship, typer.Argument(help="Relationship verb.")],
    target: Annotated[str, typer.Argument(help="Target issue key, e.g. DATAENGINEERING-2.")],
) -> None:
    """Link issue KEY to TARGET with RELATIONSHIP."""
    body = LinkCreate(relationship=relationship.value, issue=target).model_dump(exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.links.add(key, body=body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def delete(
    ctx: typer.Context,
    key: KeyArg,
    link_id: Annotated[str, typer.Argument(metavar="LINK_ID", help="Link id to remove.")],
) -> None:
    """Delete link LINK_ID from issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.tracker.links.delete(key, link_id)
    Serializer.serialize(Ack.deleted("link", link_id, on=key), app_ctx.strategy, app_ctx.console)
