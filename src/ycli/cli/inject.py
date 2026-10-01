"""Dependency injection for Typer commands — Typer has none, so this adds the small piece needed.

A command declares what it needs as keyword-only parameters typed with an injectable class
(any SDK domain client, or :class:`~ycli.settings.AppConfig`)::

    @app.command()
    def get(survey_id: SurveyIdArg, *, forms: FormsClient) -> Survey:
        return forms.surveys.get(survey_id)

:func:`inject_dependencies` rewrites each such command so Typer never sees those parameters
(they would otherwise become CLI options) and fills them from the invocation's
:class:`~ycli.cli.context.AppContext` when the command runs. A command stays a plain function,
so a test can call it with a fake client directly.

Kill-criterion: delete this module when Typer ships its own dependency injection.
"""

from __future__ import annotations

import functools
import inspect
from typing import TYPE_CHECKING, Any, get_type_hints

import typer

from ycli.cli.context import AppContext

if TYPE_CHECKING:
    from collections.abc import Callable

_CONTEXT = "_ycli_typer_context"


def inject_dependencies(app: typer.Typer) -> None:
    """Rewrite every command of ``app`` and of its sub-apps, recursively, in place."""
    for command in app.registered_commands:
        if command.callback is not None:
            command.callback = _injecting(command.callback)
    for group in app.registered_groups:
        if group.typer_instance is not None:
            inject_dependencies(group.typer_instance)


def _injecting(command: Callable[..., Any]) -> Callable[..., Any]:
    """``command`` with its injectable parameters hidden from Typer and filled at call time."""
    hints = get_type_hints(command)
    signature = inspect.signature(command, eval_str=True)
    injected = {
        name: hints[name]
        for name in signature.parameters
        if name in hints and AppContext.provides(hints[name])
    }
    if not injected:
        return command

    @functools.wraps(command)
    def run(*args: Any, **kwargs: Any) -> Any:
        app_context: AppContext = kwargs.pop(_CONTEXT).find_root().obj
        dependencies = {name: app_context.resolve(kind) for name, kind in injected.items()}
        return command(*args, **kwargs, **dependencies)

    visible = [
        parameter for name, parameter in signature.parameters.items() if name not in injected
    ]
    context = inspect.Parameter(_CONTEXT, inspect.Parameter.KEYWORD_ONLY, annotation=typer.Context)
    run.__signature__ = signature.replace(parameters=[*visible, context])  # ty: ignore[unresolved-attribute]
    return run
