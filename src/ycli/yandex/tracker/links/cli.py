"""`tracker links` commands."""

from __future__ import annotations

import enum
from typing import Annotated

import typer

from ycli.yandex.models import Ack
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.entities.models import LinkList
from ycli.yandex.tracker.links.models import Link, LinkCreate
from ycli.yandex.tracker.typedefs import (
    KeyArg,
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
def list_(key: KeyArg, *, tracker: TrackerClient) -> LinkList:
    """List links for issue KEY."""
    return tracker.links.list(key)


@app.command()
def add(
    key: KeyArg,
    relationship: Annotated[Relationship, typer.Argument(help="Relationship verb.")],
    target: Annotated[str, typer.Argument(help="Target issue key, e.g. DATAENGINEERING-2.")],
    *,
    tracker: TrackerClient,
) -> Link:
    """Link issue KEY to TARGET with RELATIONSHIP."""
    body = LinkCreate(relationship=relationship.value, issue=target).model_dump(exclude_none=True)
    return tracker.links.add(key, body=body)


@app.command()
def delete(
    key: KeyArg,
    link_id: Annotated[str, typer.Argument(metavar="LINK_ID", help="Link id to remove.")],
    *,
    tracker: TrackerClient,
) -> Ack:
    """Delete link LINK_ID from issue KEY."""
    tracker.links.delete(key, link_id)
    return Ack.deleted("link", link_id, on=key)
