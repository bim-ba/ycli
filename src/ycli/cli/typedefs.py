"""Shared CLI option type aliases reused across domain command modules.

The ``limit`` / ``--all`` pair recurs on every paginated ``list`` command; defining the
:data:`LimitOption` / :data:`AllOption` ``Annotated`` aliases once keeps the caps consistent
(pair with :meth:`ycli.settings.HTTPConfig.cap` to turn them into a concrete cap).

The global options (``--format``, ``--jq``, ``--yes``) are declared here too, once, and reused
by the root callback and every leaf command (see :mod:`ycli.cli.global_options`).
"""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.formats import OutputFormat

LimitOption = Annotated[
    int, typer.Option(min=0, help="Max items to fetch; 0 uses the default cap.")
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
        help="Filter the JSON result through a jq expression; strings print raw, like `jq -r`.",
    ),
]
YesOption = Annotated[
    bool,
    typer.Option("--yes", "-y", help="Do not ask before an operation that deletes data."),
]
