"""Global options work before and after the subcommand; a command's own option wins its name."""

import inspect
from typing import Annotated

import pytest
import typer
from typer.testing import CliRunner

from tests.hosts import TRACKER_BASE
from ycli.cli.app import app as ycli_app
from ycli.cli.context import AppContext
from ycli.cli.formats import OutputFormat
from ycli.cli.global_options import option_names
from ycli.cli.inject import inject_dependencies
from ycli.cli.typedefs import FormatOption, JqOption

runner = CliRunner()


def _issue(api) -> None:
    api.add("GET", f"{TRACKER_BASE}/myself", json={"login": "alice"})


@pytest.mark.parametrize(
    "args",
    [
        ["-o", "yaml", "tracker", "me", "get"],
        ["tracker", "me", "get", "-o", "yaml"],
        ["tracker", "me", "get", "--format", "yaml"],
        ["-o", "json", "tracker", "me", "get", "-o", "yaml"],  # the leaf wins
    ],
)
def test_the_format_is_accepted_on_either_side_of_the_subcommand(api, args):
    _issue(api)
    result = runner.invoke(ycli_app, args)
    assert result.exit_code == 0, result.output
    assert "login: alice" in result.stdout  # YAML, not the JSON of the root


def test_the_root_value_stands_when_the_leaf_gives_none(api):
    _issue(api)
    result = runner.invoke(ycli_app, ["-o", "json", "tracker", "me", "get"])
    assert '"login":"alice"' in result.stdout


@pytest.mark.parametrize(
    "args",
    [
        ["--jq", ".login", "tracker", "me", "get"],
        ["tracker", "me", "get", "--jq", ".login"],
    ],
)
def test_jq_is_accepted_on_either_side_of_the_subcommand(api, args):
    _issue(api)
    result = runner.invoke(ycli_app, args)
    assert result.stdout == "alice\n"


def test_a_bad_combination_is_refused_before_the_command_runs(api):
    result = runner.invoke(ycli_app, ["tracker", "me", "get", "-o", "yaml", "--jq", ".login"])
    assert result.exit_code == 2
    assert api.calls == []  # the check ran ahead of the request


def test_every_leaf_of_the_real_cli_lists_the_global_options():
    result = runner.invoke(ycli_app, ["tracker", "issues", "get", "--help"])
    assert "--format" in result.stdout
    assert "--jq" in result.stdout


# --- a synthetic app: a command that owns one of the names keeps it -------------------------


def _app() -> typer.Typer:
    calls: typer.Typer = typer.Typer(
        result_callback=lambda result, output_format, jq: typer.echo(
            f"{result} | {output_format} {jq}"
        )
    )

    @calls.callback()
    def root(output_format: FormatOption = OutputFormat.auto, jq: JqOption = None) -> None:
        """The root declares the aliases, as ycli's own root does."""

    @calls.command()
    def export(
        export_format: Annotated[str, typer.Option("--format", help="Its own format.")] = "xlsx",
    ) -> str:
        return f"own format {export_format}"

    @calls.command()
    def plain(survey: str, retries: int = 3) -> str:
        return f"{survey} {retries}"

    inject_dependencies(calls)
    return calls


def test_a_command_that_declares_format_keeps_it_and_gets_no_short_o():
    app = _app()
    kept = runner.invoke(app, ["export", "--format", "csv"], obj=AppContext())
    assert "own format csv" in kept.stdout
    refused = runner.invoke(app, ["export", "-o", "json"], obj=AppContext())
    assert refused.exit_code == 2
    assert "No such option" in refused.output


def test_a_command_without_a_clash_gets_every_global_option():
    result = runner.invoke(_app(), ["plain", "S-1", "--jq", ".x", "-o", "json"], obj=AppContext())
    assert result.exit_code == 0, result.output
    assert "| json .x" in result.stdout


def test_injecting_twice_does_not_add_the_options_twice():
    app = _app()
    inject_dependencies(app)
    callback = app.registered_commands[1].callback
    assert callback is not None
    names = list(inspect.signature(callback).parameters)
    assert len(names) == len(set(names))
    assert runner.invoke(app, ["plain", "S-1"], obj=AppContext()).exit_code == 0


@pytest.mark.parametrize(
    ("name", "annotation", "default", "names"),
    [
        ("format", Annotated[str, typer.Option("--format", "-o")], "x", {"--format", "-o"}),
        ("flag", Annotated[bool, typer.Option("--yes/--no-yes")], False, {"--yes", "--no-yes"}),
        ("limit", Annotated[int, typer.Option(help="no declaration")], 0, {"--limit"}),
        ("read_only", bool, typer.Option(False, "--read-only", "-r"), {"--read-only", "-r"}),
        ("retries", int, 3, {"--retries"}),
        ("survey_id", Annotated[str, typer.Argument()], inspect.Parameter.empty, set()),
        ("survey_id", str, inspect.Parameter.empty, set()),
        ("survey_id", str, typer.Argument(), set()),
    ],
)
def test_option_names_follow_how_typer_names_a_parameter(name, annotation, default, names):
    assert option_names(name, annotation, default) == names
