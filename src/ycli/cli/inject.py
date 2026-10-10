"""Dependency injection for Typer commands — Typer has none, so this adds the small piece needed.

A command declares what it needs as keyword-only parameters typed with an injectable class
(any SDK domain client, or :class:`~ycli.settings.AppConfig`)::

    @app.command()
    def get(survey_id: SurveyIDArg, *, forms: FormsClient) -> Survey:
        return forms.surveys.get(survey_id)

:func:`inject_dependencies` rewrites each such command so Typer never sees those parameters
(they would otherwise become CLI options) and fills them from the invocation's
:class:`~ycli.cli.context.AppContext` when the command runs. A command stays a plain function,
so a test can call it with a fake client directly. Commands run under the ``ycli`` root,
which applies the injection; a sub-app used on its own needs ``inject_dependencies(app)`` first.

The same rewrite gives each command the global options of :mod:`ycli.cli.global_options`, so
they are accepted after the subcommand as well as before it, and ends a ``--dry-run`` command
at its first write (:class:`~ycli.yandex.core.guard.RequestPlanned`), returning the planned
request.

Kill-criterion: delete this module when Typer ships its own dependency injection.
"""

from __future__ import annotations

import functools
import inspect
import shlex
from typing import TYPE_CHECKING, Any, get_type_hints

import typer

from ycli.cli.context import AppContext
from ycli.cli.global_options import (
    NO_BODY,
    apply_leaf_values,
    leaf_name,
    leaf_parameters,
    refuse_fields,
)
from ycli.cli.output import Continuable, Declared
from ycli.yandex.core.continuation import HANDLES, NOTHING_ELSE
from ycli.yandex.core.guard import RequestPlanned
from ycli.yandex.core.listing import Listing

if TYPE_CHECKING:
    from collections.abc import Callable

_CONTEXT = "_ycli_typer_context"
# What a command with its own ``-F`` says to the common one given before the subcommand.
OWN_FIELD = "this command has a --field of its own; the common one before it has no use"


def inject_dependencies(app: typer.Typer) -> None:
    """Rewrite every command of ``app`` and of its sub-apps, recursively, in place."""
    for command in app.registered_commands:
        if command.callback is not None:
            command.callback = _rewritten(command.callback)
    for group in app.registered_groups:
        if group.typer_instance is not None:
            inject_dependencies(group.typer_instance)


class _Deferred:
    """Stands in for a dependency and builds it on first attribute access.

    Building a client reads the credentials. Deferring it lets a command's own argument checks
    (``typer.BadParameter``, exit 2) run first, so a usage error is reported as one even when
    no credentials are set.
    """

    def __init__(self, build: Callable[[], object]) -> None:
        self._build = build
        self._built: object | None = None

    def __getattr__(self, name: str) -> Any:
        if self._built is None:
            self._built = self._build()
        return getattr(self._built, name)


def _typed(context: typer.Context, name: str | None) -> bool:
    """Whether the caller gave the parameter ``name`` on the command line."""
    source = context.get_parameter_source(name) if name else None
    return source is not None and source.name == "COMMANDLINE"


def _only_the_limit(context: typer.Context, global_options: set[str]) -> None:
    """Refuse an option given beside ``--next`` that the token already decides.

    A token carries its listing, so a filter given anew would be passed over without a word,
    and so would a field of the body (``-F``, ``--body-file``): the body is the token's.
    What a command cannot be called without (its arguments, a required option) is still given.
    """
    root = context.find_root().params
    given = [
        max(parameter.opts, key=len)
        for parameter in context.command.params
        if parameter.param_type_name == "option"
        and not parameter.required
        and parameter.name not in global_options
        and (parameter.name or "").rstrip("_") not in HANDLES
        and _typed(context, parameter.name)
    ]
    given += ["-F"] if root.get("field") else []
    given += ["--body-file"] if root.get("body_file") is not None else []
    if given:
        # violation(arch-9): what the token decides cannot be decided twice in one call
        raise typer.BadParameter(f"{NOTHING_ELSE} (given: {', '.join(given)})", param_hint="--next")


def _again(context: typer.Context) -> str:
    """This command as a call that goes on gives it: its name and what it cannot go without.

    ``ycli tracker issues search 'Queue: DE' --scroll-type sorted`` -> ``ycli tracker issues
    search 'Queue: DE'``: a ready line for ``--next``, since the rest is the token's. The
    profile the listing was asked under is in it: run without it, the line would go on in
    another account.
    """
    program, *path = context.command_path.split()
    profile = context.find_root().params.get("profile")
    words = [program, *(["--profile", profile] if profile else []), *path]
    for parameter in context.command.params:
        given = context.params.get(parameter.name or "")
        if not parameter.required or given is None:
            continue
        for value in given if isinstance(given, list | tuple) else [given]:
            if parameter.param_type_name == "option":
                words.append(max(parameter.opts, key=len))
            words.append(str(value))
    return shlex.join(words)


def _rewritten(command: Callable[..., Any]) -> Callable[..., Any]:
    """``command`` with injectable parameters hidden from Typer and the global options added.

    The injectable parameters are filled at call time.
    """
    signature = inspect.signature(command, eval_str=True)
    if _CONTEXT in signature.parameters:  # already rewritten: an app's commands load once per root
        return command
    hints = get_type_hints(command)
    injected = {
        name: hints[name]
        for name in signature.parameters
        if name in hints and AppContext.provides(hints[name])
    }
    # Typer fills only one ``typer.Context`` parameter: a command that declares its own gets
    # the same context the rewrite receives.
    own_context = next((name for name in hints if hints[name] is typer.Context), None)
    visible = [
        parameter
        for name, parameter in signature.parameters.items()
        if name not in injected and name != own_context
    ]
    leaf = leaf_parameters(visible)
    own_field = leaf_name("field") not in {parameter.name for parameter in leaf}
    # A command given a client or the fields can send a body; one that takes the context builds
    # what it needs itself and answers for the fields itself.
    can_send = own_context is not None or any(map(AppContext.sends, injected.values()))

    @functools.wraps(command)
    def run(*args: Any, **kwargs: Any) -> Any:
        context = kwargs.pop(_CONTEXT)
        if own_context is not None:
            kwargs[own_context] = context
        root = context.find_root()
        if own_field and root.params.get("field"):
            # violation(arch-9): this command has a -F of its own, and one call cannot give
            # the name two meanings
            raise typer.BadParameter(OWN_FIELD, param_hint="-F")
        apply_leaf_values(kwargs, root.params)
        if kwargs.get("next_") is not None:
            _only_the_limit(context, {parameter.name for parameter in leaf})
        if not can_send:
            refuse_fields(context)
        app_context: AppContext = root.obj
        dependencies = {
            name: _Deferred(functools.partial(app_context.resolve, kind))
            for name, kind in injected.items()
        }
        try:
            result = command(*args, **kwargs, **dependencies)
        except RequestPlanned as planned:  # --dry-run: the first write became its plan
            return planned.plan
        fields = app_context.caller_fields
        if fields.given and not fields.taken:
            # violation(arch-9): the command sent no body at all, so the fields went nowhere
            raise typer.BadParameter(NO_BODY, param_hint="-F / --body-file")
        if isinstance(result, Listing):
            result = Continuable(result, _again(context))
        return Declared(result, hints.get("return"))

    context = inspect.Parameter(_CONTEXT, inspect.Parameter.KEYWORD_ONLY, annotation=typer.Context)
    run.__signature__ = signature.replace(  # ty: ignore[unresolved-attribute]
        parameters=[*visible, *leaf, context]
    )
    return run
