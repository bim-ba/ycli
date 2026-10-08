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
from ycli.yandex.sync.files import OFFLINE, FileState, State, examine
from ycli.yandex.sync.git import uncommitted
from ycli.yandex.sync.kind import KindSummary, summary_of
from ycli.yandex.sync.plan import Planned, plan
from ycli.yandex.sync.pull import Action, Pulled, ScopeError, Sender
from ycli.yandex.sync.pull import pull as pull_objects
from ycli.yandex.sync.push import OnError, Pushed, Result, prunable
from ycli.yandex.sync.push import prune as prune_objects
from ycli.yandex.sync.push import push as push_files

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
    typer.echo(", ".join(f"{counted[state]} {state}" for state in OFFLINE), err=True)
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
        typer.Option("--exit-code", help="Exit with 7 when there is something to push."),
    ] = False,
) -> ItemList[FileState] | ExitWith:
    """Say what `push` would do with each file, as far as the files alone say; uses no network.

    A file is to `update` when its content no longer has the fingerprint in its `hash` key. One
    with no `hash` was written by hand: to `create` when it names no object, `untracked` when
    it names one. Whether the object changed on the server meanwhile, only `diff` can say.
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


@app.command()
def diff(
    context: typer.Context,
    paths: Paths = None,
    kind: Kinds = None,
    show_unchanged: Annotated[
        bool, typer.Option("--show-unchanged", help="Also list the files with nothing to push.")
    ] = False,
    show_secrets: Annotated[
        bool, typer.Option("--show-secrets", help="Show secrets as they are, not masked.")
    ] = False,
    exit_code: Annotated[
        bool,
        typer.Option(
            "--exit-code",
            help="Exit with 7 when there is something to push, 8 when a file and its object "
            "went apart.",
        ),
    ] = False,
) -> ItemList[Planned] | ExitWith:
    """Show what `push` would change: each file against its object on the server, as it is now.

    The difference runs from the server to the file. Under a directory that names a container
    (wiki/team, tracker/queues/DE) an object with no file is listed too. Where the object
    changed since the file was read, the difference is the file against the server now: the
    file keeps no copy of what was read, so whose change a line is cannot be said.
    """
    application = context.find_root().obj
    clients = {service.name: service.client_class for service in SERVICES}

    def sender(service: str) -> Sender:
        return application.resolve(clients[service]())

    scopes = [PurePosixPath(path.as_posix()) for path in paths or []]
    kinds = [one for one in declared_kinds() if not kind or one.name in kind]
    found = plan(Path.cwd(), scopes, kinds, sender, show_secrets=show_secrets)
    counted = Counter(one.state for one in found)
    # Every state but the one only `push --prune` plans.
    said = [state for state in State if state is not State.DELETE]
    typer.echo(", ".join(f"{counted[state]} {state}" for state in said), err=True)
    listed = ItemList[Planned](
        [one for one in found if show_unchanged or one.state is not State.UNCHANGED]
    )
    if counted[State.UNREADABLE]:
        return ExitWith(listed, exit_code=ExitCode.FAILURE)
    if not exit_code:
        return listed
    apart = {State.CHANGED_ON_SERVER, State.UNTRACKED, State.GONE}
    if any(counted[state] for state in apart):
        return ExitWith(listed, exit_code=ExitCode.DIVERGED)
    to_push = counted[State.UPDATE] + counted[State.CREATE]
    return ExitWith(listed, exit_code=ExitCode.CHANGES) if to_push else listed


@app.command()
def push(
    context: typer.Context,
    paths: Paths = None,
    kind: Kinds = None,
    show_unchanged: Annotated[
        bool, typer.Option("--show-unchanged", help="Also list the files with nothing to push.")
    ] = False,
    prune: Annotated[
        str | None,
        typer.Option(
            "--prune",
            metavar="COMMIT",
            help="Also delete the objects whose files were deleted since this commit.",
        ),
    ] = None,
    on_error: Annotated[
        OnError,
        typer.Option("--on-error", help="After a file fails: go on to the next, or end the run."),
    ] = OnError.FAIL,
) -> ItemList[Pushed] | ItemList[Planned] | ExitWith:
    """Send the files that differ from their objects, each write read back and compared.

    A file is sent only when its object is as the file was read: one whose object changed on
    the server, is gone, or was never read is stopped (exit 8) until a `pull`. After a write
    the object is read again: the file gets its new link, and a value the server did not keep
    fails the file and is named. A new file gets the identity of what was created. With
    --dry-run nothing is sent and the plan is printed; `diff` shows it with the differences.
    """
    application = context.find_root().obj
    clients = {service.name: service.client_class for service in SERVICES}

    def sender(service: str) -> Sender:
        return application.resolve(clients[service]())

    root = Path.cwd()
    scopes = [PurePosixPath(path.as_posix()) for path in paths or []]
    kinds = [one for one in declared_kinds() if not kind or one.name in kind]
    try:
        doomed = prunable(root, prune, scopes, kinds) if prune else []
    except ScopeError as refusal:
        raise typer.BadParameter(str(refusal), param_hint="--prune") from None
    if application.options.get("dry_run"):
        planned = [
            one.model_copy(update={"diff": None}) for one in plan(root, scopes, kinds, sender)
        ]
        planned += [one for one, _, _ in doomed]
        counted = Counter(one.state for one in planned)
        typer.echo(", ".join(f"{counted[state]} {state}" for state in State), err=True)
        return ItemList[Planned](
            [one for one in planned if show_unchanged or one.state is not State.UNCHANGED]
        )
    done = list(push_files(root, scopes, kinds, sender, on_error=on_error))
    aborted = on_error is OnError.ABORT and any(one.result is Result.FAILED for one in done)
    if not aborted:
        done += prune_objects(doomed, sender)
    results = Counter(one.result for one in done)
    summed = ", ".join(f"{results[result]} {result}" for result in Result)
    added = sum(one.added for one in done)
    # Said only when it happened: most runs add nothing.
    holds = {0: "", 1: "; 1 file now holds what the service added"}.get(
        added, f"; {added} files now hold what the service added"
    )
    typer.echo(summed + holds, err=True)
    listed = ItemList[Pushed](
        [one for one in done if show_unchanged or one.result is not Result.UNCHANGED]
    )
    if results[Result.FAILED]:
        return ExitWith(listed, exit_code=ExitCode.FAILURE)
    return ExitWith(listed, exit_code=ExitCode.DIVERGED) if results[Result.STOPPED] else listed
