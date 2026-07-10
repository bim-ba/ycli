"""``ycli`` root CLI — mounts each domain's sub-app. Domain logic lives in <domain>/cli.py.

Run a subcommand directly: ``uv run ycli wiki pages get <slug>`` (or ``python -m ycli.cli``).
"""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import OutputFormat
from ycli.log import configure
from ycli.mcp.cli import app as mcp_app
from ycli.settings import AppConfig
from ycli.yandex.forms.cli import app as forms_app
from ycli.yandex.status import app as auth_app
from ycli.yandex.tracker.cli import app as tracker_app
from ycli.yandex.wiki.cli import app as wiki_app

app = typer.Typer(
    name="ycli",
    help="ycli — Yandex 360 API SDK CLI.",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)


def _version_callback(value: bool) -> None:
    """Eager ``--version``: print the installed version and exit before any command runs."""
    if value:
        from ycli import __version__

        typer.echo(__version__)
        raise typer.Exit


@app.callback()
def _main(
    ctx: typer.Context,
    output_format: Annotated[
        OutputFormat,
        typer.Option(
            "--format", "-o", help="Output format (auto = pretty on a TTY, JSON when piped)."
        ),
    ] = OutputFormat.auto,
    version: Annotated[  # consumed by the eager _version_callback, not this body
        bool,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show the installed ycli version and exit.",
        ),
    ] = False,
) -> None:
    """Declare the global ``--format`` option, configure logging, build the AppContext."""
    configure(level=AppConfig().log_level)
    ctx.obj = AppContext(output_format=output_format)


app.add_typer(auth_app)
app.add_typer(wiki_app)
app.add_typer(tracker_app)
app.add_typer(forms_app)

app.add_typer(mcp_app)


def main() -> None:  # pragma: no cover
    """Console-script entry point (``ycli`` / ``yandex-cli``)."""
    import typer
    from pydantic import ValidationError

    from ycli.cli.errors import format_cli_error
    from ycli.yandex.errors import YandexError

    try:
        app()
    except (YandexError, ValidationError) as exc:
        typer.secho(format_cli_error(exc), fg=typer.colors.RED, err=True)
        raise SystemExit(1) from exc
