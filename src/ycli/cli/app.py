"""``ycli`` root CLI — mounts each domain's sub-app. Domain logic lives in <domain>/cli.py.

Run a subcommand directly: ``uv run ycli wiki pages get <slug>`` (or ``python -m ycli.cli``).
"""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.inject import inject_dependencies
from ycli.cli.output import OutputFormat, render
from ycli.log import configure
from ycli.mcp.cli import app as mcp_app
from ycli.settings import AppConfig
from ycli.yandex.registry import SERVICES
from ycli.yandex.status.cli import app as auth_app


def _render(result: object, output_format: OutputFormat, verbose: int, version: bool) -> None:
    """Print whatever the command returned; Click passes the root options alongside it."""
    render(result, output_format)


app = typer.Typer(
    name="ycli",
    help="ycli — Yandex 360 API SDK CLI.",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    rich_markup_mode="rich",
    result_callback=_render,
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
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose",
            "-v",
            count=True,
            help="Log to stderr: -v shows HTTP requests, -vv adds debug detail.",
        ),
    ] = 0,
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
    """Declare the global options, configure logging, build the AppContext."""
    # A caller (a test, an embedding app) may hand in its own context; otherwise build one.
    if ctx.obj is None:
        ctx.obj = AppContext(config=AppConfig())
    logging_config = ctx.obj.config.logging
    level = {0: logging_config.level, 1: "INFO"}.get(verbose, "DEBUG")
    configure(level=level, log_format=logging_config.format)


app.add_typer(auth_app)
for service in SERVICES:
    app.add_typer(service.cli_app(), help=service.help)
app.add_typer(mcp_app)
inject_dependencies(app)


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
