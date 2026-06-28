"""cliformat.output_format resolves the root --format option from any nested command."""
import typer
from typer.testing import CliRunner

from ycli.cliformat import output_format
from ycli.output import OutputFormat

app = typer.Typer()
sub = typer.Typer()
app.add_typer(sub, name="sub")


@app.callback()
def _root(output_format: OutputFormat = typer.Option(OutputFormat.auto, "--format")):
    pass


@sub.command()
def go(ctx: typer.Context):
    typer.echo(output_format(ctx).value)


def test_resolves_explicit_format():
    res = CliRunner().invoke(app, ["--format", "json", "sub", "go"])
    assert res.stdout.strip() == "json"


def test_defaults_to_auto():
    res = CliRunner().invoke(app, ["sub", "go"])
    assert res.stdout.strip() == "auto"
