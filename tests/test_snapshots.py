"""ARCH-6: the public surface changes only via an intentional snapshot update."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated

import pytest
import typer
import typer.main
from fastmcp import Client, FastMCP

from tests.snapshots._surface import (
    cli_signature,
    cli_signatures,
    mcp_output_schemas,
    mcp_prompts_and_resources,
    mcp_signature,
    mcp_signatures,
)

HERE = Path(__file__).resolve().parent / "snapshots"
HINT = "run `uv run python -m tests.snapshots --update` to accept the new surface"


@pytest.mark.parametrize(
    ("filename", "current"),
    [
        ("cli_signatures.txt", cli_signatures),
        ("mcp_signatures.txt", mcp_signatures),
        ("mcp_prompts_and_resources.txt", mcp_prompts_and_resources),
        ("mcp_output_schemas.txt", mcp_output_schemas),
    ],
)
def test_public_surface_matches_snapshot(filename, current):
    expected = (HERE / filename).read_text(encoding="utf-8").splitlines()
    assert current() == expected, f"public surface drifted ({filename}); {HINT}"


def test_the_cli_snapshot_sees_a_renamed_or_newly_required_parameter():
    """Prove-it: a parameter's name, type, default and requiredness are all in the line."""

    def line(command) -> str:
        app = typer.Typer(add_completion=False)
        app.command("probe")(command)
        return cli_signature("probe", typer.main.get_command(app))

    def before(key: str, limit: Annotated[int, typer.Option()] = 0) -> None: ...
    def renamed(key: str, top: Annotated[int, typer.Option()] = 0) -> None: ...
    def required(key: str, limit: Annotated[int, typer.Option()]) -> None: ...

    assert line(before) == "probe: --limit:INTEGER=0 KEY:TEXT!"
    assert line(renamed) == "probe: --top:INTEGER=0 KEY:TEXT!"
    assert line(required) == "probe: --limit:INTEGER! KEY:TEXT!"


def test_the_mcp_snapshot_sees_a_renamed_or_newly_required_parameter():
    def line(function) -> str:
        server = FastMCP("probe")
        server.tool(name="probe")(function)

        async def listed():
            async with Client(server) as client:
                return await client.list_tools()

        return mcp_signature(asyncio.run(listed())[0])

    def before(key: str, limit: int = 5) -> None: ...
    def renamed(key: str, top: int = 5) -> None: ...
    def required(key: str, limit: int) -> None: ...

    assert line(before) == "probe(key:string!, limit:integer=5)"
    assert line(renamed) == "probe(key:string!, top:integer=5)"
    assert line(required) == "probe(key:string!, limit:integer!)"
