"""`tracker filters` commands."""

from __future__ import annotations

import json
from typing import Annotated, Any

import typer

from ycli.yandex.models import Ack
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.filters.models import Filter, FilterCreate, FilterUpdate

app = typer.Typer(name="filters", help="Tracker saved filters.", no_args_is_help=True)


def _parse_filter(raw: str | None) -> Any:
    """Parse the ``--filter`` JSON; ``None`` when the option is not given."""
    if raw is None:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        # violation(arch-9): --filter is JSON; text that does not parse gives no value for the body
        raise typer.BadParameter(f"--filter must be valid JSON: {exc}") from exc
    return parsed


@app.command()
def get(
    filter_id: Annotated[
        str, typer.Argument(metavar="FILTER_ID", help="Identifier of the saved filter.")
    ],
    *,
    tracker: TrackerClient,
) -> Filter:
    """Get parameters of one saved filter by FILTER_ID."""
    return tracker.filters.get(filter_id=filter_id)


@app.command()
def create(
    name: Annotated[str, typer.Option(help="Display name of the new filter.")],
    query: Annotated[
        str | None, typer.Option(help="Filtering conditions in Tracker query language.")
    ] = None,
    filter_: Annotated[
        str | None, typer.Option("--filter", help="Filtering conditions as a JSON object.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Filter:
    """Create a saved filter (POST /filters/)."""
    body = FilterCreate(name=name, query=query, filter=_parse_filter(filter_))
    return tracker.filters.create(body)


@app.command()
def update(
    filter_id: Annotated[
        str, typer.Argument(metavar="FILTER_ID", help="Identifier of the saved filter.")
    ],
    name: Annotated[str | None, typer.Option(help="New display name of the filter.")] = None,
    query: Annotated[
        str | None, typer.Option(help="New filtering conditions in query language.")
    ] = None,
    filter_: Annotated[
        str | None,
        typer.Option("--filter", help="Replacement filtering conditions as a JSON object."),
    ] = None,
    *,
    tracker: TrackerClient,
) -> Filter:
    """Edit filter FILTER_ID (PATCH /filters/{id}) — no version lock; filter is replaced whole."""
    body = FilterUpdate(name=name, query=query, filter=_parse_filter(filter_))
    return tracker.filters.update(filter_id, body)


@app.command()
def delete(
    filter_id: Annotated[
        str, typer.Argument(metavar="FILTER_ID", help="Identifier of the saved filter.")
    ],
    *,
    tracker: TrackerClient,
) -> Ack:
    """Delete saved filter FILTER_ID (DELETE /filters/{id})."""
    tracker.filters.delete(filter_id)
    return Ack.deleted("filter", filter_id)
