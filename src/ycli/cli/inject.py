"""Dependency injection for Typer commands — Typer has none, so this adds the small piece needed.

A command declares what it needs as keyword-only parameters typed with an injectable class
(any SDK domain client, or :class:`~ycli.settings.AppConfig`)::

    @app.command()
    def get(survey_id: SurveyIdArg, *, forms: FormsClient) -> Survey:
        return forms.surveys.get(survey_id)

:func:`inject_dependencies` rewrites each such command so Typer never sees those parameters
(they would otherwise become CLI options) and fills them from the invocation's
:class:`~ycli.cli.context.AppContext` when the command runs. A command stays a plain function,
so a test can call it with a fake client directly. Commands run under the ``ycli`` root,
which applies the injection; a sub-app used on its own needs ``inject_dependencies(app)`` first.

The same rewrite gives each command the global options of :mod:`ycli.cli.global_options`, so
they are accepted after the subcommand as well as before it, and ends a ``--dry-run`` command
at its first write (:class:`~ycli.cli.guard.DryRunPlanned`), returning the planned request.

Kill-criterion: delete this module when Typer ships its own dependency injection.
"""

from __future__ import annotations

import functools
import inspect
from typing import TYPE_CHECKING, Any, get_type_hints

import typer

from ycli.cli.context import AppContext
from ycli.cli.global_options import apply_leaf_values, leaf_parameters
from ycli.cli.guard import DryRunPlanned

if TYPE_CHECKING:
    from collections.abc import Callable

_CONTEXT = "_ycli_typer_context"


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

    @functools.wraps(command)
    def run(*args: Any, **kwargs: Any) -> Any:
        context = kwargs.pop(_CONTEXT)
        if own_context is not None:
            kwargs[own_context] = context
        root = context.find_root()
        apply_leaf_values(kwargs, root.params)
        app_context: AppContext = root.obj
        dependencies = {
            name: _Deferred(functools.partial(app_context.resolve, kind))
            for name, kind in injected.items()
        }
        try:
            return command(*args, **kwargs, **dependencies)
        except DryRunPlanned as planned:  # --dry-run: the first write became its plan
            return planned.plan

    context = inspect.Parameter(_CONTEXT, inspect.Parameter.KEYWORD_ONLY, annotation=typer.Context)
    run.__signature__ = signature.replace(  # ty: ignore[unresolved-attribute]
        parameters=[*visible, *leaf_parameters(visible), context]
    )
    return run
