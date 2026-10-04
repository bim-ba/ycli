"""Shared CLI option type aliases reused across domain command modules.

The ``limit`` / ``--all`` pair recurs on every paginated ``list`` command; defining the
:data:`LimitOption` / :data:`AllOption` ``Annotated`` aliases once keeps the caps consistent
(pair with :meth:`ycli.settings.HTTPConfig.cap` to turn them into a concrete cap).

The global options (``--format``, ``--jq``, ``--yes``, ``--dry-run``, ``--profile``) are declared
here too, once, and reused by the root callback and every leaf command (see
:mod:`ycli.cli.global_options`).
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, get_args, get_origin

import typer

from ycli.cli.formats import OutputFormat

LimitOption = Annotated[
    int | None, typer.Option(min=1, help="Max items to fetch (default: the configured cap).")
]
AllOption = Annotated[bool, typer.Option("--all", help="Fetch everything, ignoring the cap.")]

FormatOption = Annotated[
    OutputFormat | None,
    typer.Option("--format", "-o", help="Output format (auto = pretty on a TTY, JSON when piped)."),
]
JqOption = Annotated[
    str | None,
    typer.Option(
        "--jq",
        metavar="EXPR",
        help="Filter the JSON result through a jq expression; strings print raw, like `jq -r`. "
        "Needs the `jq` extra.",
    ),
]
YesOption = Annotated[
    bool,
    typer.Option("--yes", "-y", help="Do not ask before an operation that deletes data."),
]
ProfileOption = Annotated[
    str | None,
    typer.Option(
        "--profile",
        metavar="NAME",
        help="Use the credentials saved as this profile (YCLI_PROFILE); the environment's and "
        ".env's are then not read. `ycli auth profiles` lists them.",
    ),
]
DryRunOption = Annotated[
    bool,
    typer.Option(
        "--dry-run",
        help="Do not send a write: print the request it would send instead. Reads still run, "
        "and only the first write of a command is shown.",
    ),
]


def known_values(value_set: Any) -> tuple[str, ...]:
    """The values a soft set names: ``Literal["asc", "desc"] | str`` -> ``("asc", "desc")``.

    Args:
        value_set: A set of values as it is defined, ``Literal[...] | str``.

    Returns:
        The known values, in the order of the definition.

    Examples:
        >>> from typing import Literal
        >>> known_values(Literal["asc", "desc"] | str)
        ('asc', 'desc')
    """
    return tuple(
        str(value)
        for member in get_args(value_set)
        if get_origin(member) is Literal
        for value in get_args(member)
    )


def values_option(value_set: Any, *names: str, help: str) -> Any:  # noqa: A002
    """A string option that knows a set's values: they are in its help and its completion.

    Typer has no "one of these or any string" type, so the option stays a string: another
    value goes to the API, which answers for it.

    Args:
        value_set: The set of values as it is defined, ``Literal[...] | str``.
        *names: The option's names, as for ``typer.Option``.
        help: What the option does, without the values.

    Returns:
        The ``typer.Option`` to put in ``Annotated[str | None, ...]``.

    Examples:
        >>> from typing import Literal
        >>> values_option(Literal["asc", "desc"] | str, "--order", help="Sort direction.").help
        'Sort direction. One of: asc, desc.'
    """
    values = known_values(value_set)

    def complete(incomplete: str) -> list[str]:
        return [value for value in values if value.startswith(incomplete)]

    return typer.Option(
        *names, help=f"{help} One of: {', '.join(values)}.", autocompletion=complete
    )
