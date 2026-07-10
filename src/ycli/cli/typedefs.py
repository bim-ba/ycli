"""Shared CLI option type aliases reused across domain command modules.

The ``limit`` / ``--all`` pair recurs on every paginated ``list`` command; defining the
:data:`LimitOption` / :data:`AllOption` ``Annotated`` aliases once keeps the caps consistent
(pair with :func:`ycli.yandex.pagination.resolve_cap` to turn them into a concrete cap).
"""

from __future__ import annotations

from typing import Annotated

import typer

LimitOption = Annotated[int, typer.Option(help="Max items to fetch; 0 uses the default cap.")]
AllOption = Annotated[bool, typer.Option("--all", help="Fetch everything, ignoring the cap.")]
