"""`datalens entrylocks` commands."""

from typing import Annotated

import typer

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.entrylocks.models import (
    Lock,
    LockCreated,
    LockExtension,
    LockRelease,
    LockTerms,
)
from ycli.yandex.datalens.typedefs import EntryIDArg

app = typer.Typer(name="entrylocks", help="Locks on DataLens entries.", no_args_is_help=True)


@app.command()
def create(
    entry_id: EntryIDArg,
    data: Annotated[
        str,
        typer.Option(
            "--data",
            help='The terms of the lock, as a JSON object: {"duration": 300000, "force": false} '
            "(the duration in milliseconds).",
        ),
    ],
    *,
    datalens: DataLensClient,
) -> LockCreated:
    """Lock an entry for editing; keep the token the reply holds, releasing the lock takes it.

    --data is required; -F adds a field it does not name (-F 'data[force]=true'). An entry
    that is already locked answers 423 with who holds the lock and until when.
    """
    return datalens.entrylocks.create(entry_id, data=LockTerms.model_validate_json(data))


@app.command()
def extend(
    entry_id: EntryIDArg,
    data: Annotated[
        str,
        typer.Option(
            "--data",
            help='The lock and its new terms, as a JSON object: {"lockToken": "...", '
            '"duration": 600000}.',
        ),
    ],
    *,
    datalens: DataLensClient,
) -> Lock:
    """Hold a lock longer."""
    return datalens.entrylocks.extend(entry_id, data=LockExtension.model_validate_json(data))


@app.command()
def delete(
    entry_id: EntryIDArg,
    params: Annotated[
        str,
        typer.Option(
            "--params",
            help='Which lock to release, as a JSON object: {"lockToken": "..."}, or '
            '{"force": true} for a lock held by another.',
        ),
    ],
    *,
    datalens: DataLensClient,
) -> Lock:
    """Release a lock; an entry that is not locked answers 404."""
    return datalens.entrylocks.delete(entry_id, params=LockRelease.model_validate_json(params))
