"""``ycli`` root CLI — mounts each domain's sub-app. Domain logic lives in <domain>/cli.py.

Run a subcommand directly: ``uv run ycli wiki pages get <slug>`` (or ``python -m ycli.cli``).
"""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.exit_codes import exit_codes_summary
from ycli.cli.formats import OutputFormat
from ycli.cli.lazy import RootGroup, SubApp
from ycli.yandex.registry import SERVICES


class _Ycli(RootGroup):
    """The root group: every service, then the tooling sub-apps, each imported on first use."""

    sub_apps = (
        *(SubApp(service.name, service.help, service.cli) for service in SERVICES),
        SubApp("auth", "Inspect and obtain Yandex 360 credentials.", "ycli.yandex.status.cli:app"),
        SubApp("mcp", "MCP server control (reads + writes).", "ycli.mcp.cli:app"),
    )


def _render(result: object, output_format: OutputFormat, verbose: int, version: bool) -> None:
    """Print whatever the command returned; Click passes the root options alongside it."""
    from ycli.cli.output import render

    render(result, output_format)


app = typer.Typer(
    cls=_Ycli,
    name="ycli",
    help="ycli — Yandex 360 API SDK CLI.",
    epilog=f"Exit codes: {exit_codes_summary()} (see the README).",
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
    from ycli.cli.context import AppContext
    from ycli.log import configure
    from ycli.settings import AppConfig

    # A caller (a test, an embedding app) may hand in its own context; otherwise build one.
    if ctx.obj is None:
        ctx.obj = AppContext(config=AppConfig())
    logging_config = ctx.obj.config.logging
    level = {0: logging_config.level, 1: "INFO"}.get(verbose, "DEBUG")
    configure(level=level, log_format=logging_config.format)


def main() -> None:
    """Console-script entry point (``ycli`` / ``yandex-cli``): a failure exits by its kind."""
    from pydantic import ValidationError

    from ycli.cli.errors import exit_code_for, format_cli_error
    from ycli.yandex.errors import YandexError

    try:
        app()
    except (YandexError, ValidationError) as exc:
        typer.secho(format_cli_error(exc), fg=typer.colors.RED, err=True)
        raise SystemExit(exit_code_for(exc)) from exc
