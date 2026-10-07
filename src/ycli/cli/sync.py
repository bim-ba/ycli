"""``ycli sync``: the content of Yandex 360 as files of a git repository.

The engine is ``ycli.yandex.sync``; a resource declares itself a kind of file to it.
"""

from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Annotated

import typer

from ycli.cli.exit_codes import ExitCode
from ycli.cli.output import ExitWith
from ycli.yandex.models import ItemList
from ycli.yandex.registry import SERVICES
from ycli.yandex.registry import kinds as declared_kinds
from ycli.yandex.sync.files import FileState, State, examine
from ycli.yandex.sync.git import uncommitted
from ycli.yandex.sync.kind import KindSummary, summary_of
from ycli.yandex.sync.pull import Action, Pulled, ScopeError, Sender
from ycli.yandex.sync.pull import pull as pull_objects

app = typer.Typer(name="sync", help="Yandex 360 content as files in git.", no_args_is_help=True)

Paths = Annotated[
    list[Path] | None,
    typer.Argument(help="Files or directories to look at; every service's directory by default."),
]
Kinds = Annotated[
    list[str] | None,
    typer.Option("--kind", help="Keep the files of this kind, e.g. wiki/page (repeatable)."),
]


def _examined(paths: list[Path] | None, only: list[str] | None) -> list[FileState]:
    """What each file under ``paths`` is now; the summary line goes to stderr."""
    scopes = [PurePosixPath(path.as_posix()) for path in paths or []]
    found = examine(Path.cwd(), scopes, declared_kinds())
    kept = [file for file in found if not only or file.kind in only or file.kind is None]
    counted = Counter(file.state for file in kept)
    typer.echo(", ".join(f"{counted[state]} {state}" for state in State), err=True)
    return kept


@app.command()
def kinds() -> ItemList[KindSummary]:
    """List the kinds of object that can be kept as files, and what guards a write of each."""
    return ItemList[KindSummary]([summary_of(kind) for kind in declared_kinds()])


@app.command()
def status(
    paths: Paths = None,
    kind: Kinds = None,
    show_unchanged: Annotated[
        bool, typer.Option("--show-unchanged", help="Also list the files that were not edited.")
    ] = False,
    exit_code: Annotated[
        bool,
        typer.Option("--exit-code", help="Exit with 7 when a file was edited or is new."),
    ] = False,
) -> ItemList[FileState] | ExitWith:
    """Say which files were edited since they were read from the server; uses no network.

    A file is edited when its content no longer has the fingerprint in its `hash` key, and
    new when it has no `hash`: it was written by hand.
    """
    kept = _examined(paths, kind)
    listed = ItemList[FileState](
        [file for file in kept if show_unchanged or file.state is not State.UNCHANGED]
    )
    if any(file.state is State.UNREADABLE for file in kept):
        # A file that cannot be read is an error, which is more than a change.
        return ExitWith(listed, exit_code=ExitCode.FAILURE)
    changed = any(file.state is not State.UNCHANGED for file in kept)
    return ExitWith(listed, exit_code=ExitCode.CHANGES) if exit_code and changed else listed


@app.command()
def validate(paths: Paths = None, kind: Kinds = None) -> ItemList[FileState] | ExitWith:
    """Check that every file reads as a file of its kind and lies where it should; no network.

    Prints the files that do not, each with its line and the reason, and exits non-zero if
    there is one. Fit for a pre-commit hook.
    """
    unreadable = [file for file in _examined(paths, kind) if file.state is State.UNREADABLE]
    listed = ItemList[FileState](unreadable)
    return ExitWith(listed) if unreadable else listed


@app.command()
def pull(
    context: typer.Context,
    path: Annotated[
        Path,
        typer.Argument(
            help="What to pull: wiki/<page> with the pages under it, tracker/queues/<queue>."
        ),
    ],
    kind: Kinds = None,
    show_unchanged: Annotated[
        bool, typer.Option("--show-unchanged", help="Also list the files that were the same.")
    ] = False,
) -> ItemList[Pulled]:
    """Read the objects under PATH from the server and write each as its file.

    A file is written over whatever is there: commit your edits first, git is what protects
    them. With --dry-run nothing is written, and a file that holds uncommitted work is named.
    An object no kind keeps (a grid among Wiki pages) is listed as skipped.
    """
    application = context.find_root().obj
    clients = {service.name: service.client_class for service in SERVICES}

    def sender(service: str) -> Sender:
        return application.resolve(clients[service]())

    dry_run = bool(application.options.get("dry_run"))
    kinds = [one for one in declared_kinds() if not kind or one.name in kind]
    try:
        found = pull_objects(
            Path.cwd(), PurePosixPath(path.as_posix()), kinds, sender, write=not dry_run
        )
    except ScopeError as refusal:
        raise typer.BadParameter(str(refusal), param_hint="PATH") from None
    if dry_run:
        changed = [PurePosixPath(one.path) for one in found if one.action is Action.WOULD_WRITE]
        at_risk = {str(one) for one in uncommitted(Path.cwd(), changed)}
        found = [
            one.model_copy(update={"detail": "would overwrite uncommitted work"})
            if one.path in at_risk
            else one
            for one in found
        ]
    counted = Counter(one.action for one in found)
    # A run says what it did: one that writes nothing counts no file as written.
    unsaid = Action.WRITTEN if dry_run else Action.WOULD_WRITE
    said = [action for action in Action if action is not unsaid]
    typer.echo(", ".join(f"{counted[action]} {action}" for action in said), err=True)
    return ItemList[Pulled](
        [one for one in found if show_unchanged or one.action is not Action.UNCHANGED]
    )
