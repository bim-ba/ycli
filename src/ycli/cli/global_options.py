"""Global options that work on either side of the subcommand.

``ycli -o json tracker issues get K`` and ``ycli tracker issues get K -o json`` are the same.

The root callback declares each option (that is where ``--help`` lists it); every leaf command
gets the same option too, added by :func:`~ycli.cli.inject.inject_dependencies`, and writes what
it was given into the invocation's root state, which the result callback and the
:class:`~ycli.cli.context.AppContext` read. A value on the leaf wins over one on the root. An
option a command already declares under one of the same names (``forms answers export --format``,
``auth login --yes``) is left to that command.

Each option is declared once, as an alias in :mod:`ycli.cli.typedefs`, and listed in
:data:`GLOBAL_OPTIONS` under the name of the root callback parameter that holds it.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any

from typer.models import ArgumentInfo, OptionInfo

from ycli.cli.formats import OutputFormat
from ycli.cli.typedefs import FormatOption, JqOption

if TYPE_CHECKING:
    from collections.abc import Iterable, MutableMapping

# root callback parameter name -> (the option's alias, its default on a leaf: "not given")
GLOBAL_OPTIONS: dict[str, tuple[Any, object]] = {
    "output_format": (FormatOption, None),
    "jq": (JqOption, None),
}
_PREFIX = "_ycli_global_"


def option_names(name: str, annotation: Any, default: Any) -> set[str]:
    """The option names (``--long``, ``-s``) Typer gives ``name``; none for an argument.

    Inside ``Annotated`` the first argument of ``typer.Option`` is a declaration, outside it the
    default value.

    Example:
        >>> sorted(option_names("format", FormatOption, None))
        ['--format', '-o']
        >>> option_names("survey_id", str, inspect.Parameter.empty)
        set()
    """
    infos = [*getattr(annotation, "__metadata__", ()), default]
    if any(isinstance(info, ArgumentInfo) for info in infos):
        return set()
    derived = f"--{name.replace('_', '-')}"
    declarations = [
        (info.default, *info.param_decls)
        if isinstance(info.default, str) and info is not default
        else info.param_decls
        for info in infos
        if isinstance(info, OptionInfo)
    ]
    if not declarations:  # no ``typer.Option``: a plain default makes an option, none an argument
        return set() if default is inspect.Parameter.empty else {derived}
    return {
        part
        for declared in declarations
        for declaration in declared or (derived,)
        for part in declaration.split("/")
    }


def leaf_parameters(taken: Iterable[inspect.Parameter]) -> list[inspect.Parameter]:
    """The global options a command with the parameters ``taken`` can still be given."""
    declared = {
        option
        for parameter in taken
        for option in option_names(parameter.name, parameter.annotation, parameter.default)
    }
    return [
        inspect.Parameter(
            _PREFIX + name, inspect.Parameter.KEYWORD_ONLY, annotation=alias, default=default
        )
        for name, (alias, default) in GLOBAL_OPTIONS.items()
        if not option_names(name, alias, default) & declared
    ]


def apply_leaf_values(arguments: dict[str, Any], root_params: MutableMapping[str, Any]) -> None:
    """Move the global options a leaf received out of ``arguments`` and into the root state.

    A value equal to the leaf default means "not given" and leaves the root's value alone. Then
    the combination is checked, before the command can change anything on the server.
    """
    for name, (_, default) in GLOBAL_OPTIONS.items():
        if (key := _PREFIX + name) in arguments and (value := arguments.pop(key)) != default:
            root_params[name] = value
    if (expression := root_params.get("jq")) is not None:
        from ycli.cli.output import check_jq

        check_jq(expression, root_params.get("output_format") or OutputFormat.auto)
