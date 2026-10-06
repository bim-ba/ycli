"""CLI options several DataLens resources share (ARCH-5: defined once)."""

from typing import Annotated

import typer

PermissionsOption = Annotated[
    bool | None,
    typer.Option(
        "--include-permissions-info/--no-include-permissions-info",
        help="Also say what you may do with it.",
    ),
]
DeltaOption = Annotated[
    list[str],
    typer.Option(
        "--delta",
        help='A role to add or remove, as a JSON object of the API docs: {"action": "ADD", '
        '"accessBinding": {"roleId": ..., "subject": {"id": ..., "type": ...}}} (repeatable).',
    ),
]
EntryIDArg = Annotated[str, typer.Argument(metavar="ENTRY_ID", help="Entry id.")]
