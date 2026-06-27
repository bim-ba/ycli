"""``ycli`` root CLI — mounts each domain's sub-app. Domain logic lives in <domain>/cli.py.

Run a subcommand directly: ``uv run ycli wiki pages get <slug>`` (or ``python -m ycli.cli``).
"""

from __future__ import annotations

from typing import Annotated

import typer

from ycli._group import SuggestGroup
from ycli.authcli import app as auth_app
from ycli.log import configure
from ycli.output import OutputFormat, set_format
from ycli.yandex.forms.cli import app as forms_app
from ycli.yandex.tracker.cli import app as tracker_app
from ycli.yandex.wiki.cli import app as wiki_app

app = typer.Typer(
    name="ycli",
    help="ycli — Yandex 360 API SDK CLI.",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    cls=SuggestGroup,
)


@app.callback()
def _main(
    output_format: Annotated[
        OutputFormat,
        typer.Option("--format", "-o", help="Output format (auto = pretty on a TTY, JSON when piped)."),
    ] = OutputFormat.auto,
) -> None:
    """Configure logging and the output format before any subcommand runs."""
    configure()
    set_format(output_format)


app.add_typer(auth_app)
app.add_typer(wiki_app)
app.add_typer(tracker_app)
app.add_typer(forms_app)


@app.command(name="mcp")
def mcp() -> None:
    """Run the read-only MCP server over stdio (requires the ``mcp`` extra).

    Tools are namespaced ``wiki_*``, ``tracker_*``, ``forms_*``. Point an MCP client
    at ``ycli mcp``.
    """
    try:
        from ycli.mcp import main as run_server
    except ModuleNotFoundError as exc:  # pragma: no cover - only without the 'mcp' extra
        raise typer.BadParameter(
            "The MCP server requires the 'mcp' extra. Install it with: "
            "uv add 'yandex-cli[mcp]'  (or: uv tool install 'yandex-cli[mcp]')."
        ) from exc
    run_server()


def main() -> None:  # pragma: no cover
    """Console-script entry point (``ycli`` / ``yandex-cli``)."""
    from ycli.yandex.errors import YandexError

    try:
        app()
    except YandexError as exc:
        import typer

        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1) from exc


if __name__ == "__main__":  # pragma: no cover
    main()
