"""``ycli`` root CLI — mounts each domain's sub-app. Domain logic lives in <domain>/cli.py.

Run a subcommand directly: ``uv run ycli wiki pages get <slug>`` (or ``python -m ycli.cli``).
"""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.context import AppContext
from ycli.log import configure
from ycli.mcp_launcher import launch_mcp_server
from ycli.output import OutputFormat
from ycli.yandex.auth import app as auth_app
from ycli.yandex.forms.cli import app as forms_app
from ycli.yandex.settings import AppConfig
from ycli.yandex.tracker.cli import app as tracker_app
from ycli.yandex.wiki.cli import app as wiki_app

app = typer.Typer(
    name="ycli",
    help="ycli — Yandex 360 API SDK CLI.",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)


@app.callback()
def _main(
    ctx: typer.Context,
    output_format: Annotated[
        OutputFormat,
        typer.Option(
            "--format", "-o", help="Output format (auto = pretty on a TTY, JSON when piped)."
        ),
    ] = OutputFormat.auto,
) -> None:
    """Declare the global ``--format`` option, configure logging, build the AppContext."""
    configure(level=AppConfig().log_level)
    ctx.obj = AppContext(output_format=output_format)


app.add_typer(auth_app)
app.add_typer(wiki_app)
app.add_typer(tracker_app)
app.add_typer(forms_app)

app.command(name="mcp")(launch_mcp_server)


def main() -> None:  # pragma: no cover
    """Console-script entry point (``ycli`` / ``yandex-cli``)."""
    import typer
    from pydantic import ValidationError

    from ycli.yandex.errors import YandexError

    try:
        app()
    except (YandexError, ValidationError) as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1) from exc


if __name__ == "__main__":  # pragma: no cover
    main()
