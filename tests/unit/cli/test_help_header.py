"""`ycli --help` says of each service what the MCP server's instructions say of it."""

from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.full_server import mcp
from tests.snapshots._surface import cli_tree
from ycli.yandex.registry import SERVICES, about, start_command


def _plain(text: str) -> str:
    return " ".join(text.split())


def test_the_help_and_the_instructions_say_the_same_of_a_service():
    """One text, from one place: the registry. A new service is in both by being registered."""
    shown = _plain(CliRunner().invoke(cli.app, ["--help"], env={"COLUMNS": "200"}).output)
    told = mcp.instructions or ""
    for service in SERVICES:
        said = about(service)
        assert f"{service.name} — {said}; start with `{start_command(service)}`." in shown
        assert f"{service.name}_* — {said}; start with {service.start}." in told


def test_the_command_to_begin_with_is_the_tool_to_begin_with():
    """A tool and its command are one name: the start of a service exists on both surfaces."""
    commands = set(cli_tree())
    for service in SERVICES:
        command = start_command(service).removeprefix("ycli ")
        assert command in commands
        assert command.replace(" ", "_").replace("-", "_") == service.start
