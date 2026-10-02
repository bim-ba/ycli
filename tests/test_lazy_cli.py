"""The CLI root imports a service's commands only when that service runs (#92)."""

import subprocess
import sys

import typer
from typer.core import TyperGroup
from typer.main import get_command
from typer.testing import CliRunner

from ycli.cli.app import app
from ycli.cli.lazy import LazyGroup, SubApp


def _imported_after(argv: list[str]) -> set[str]:
    """Run ``ycli <argv>`` in a fresh interpreter and return the ycli modules it imported."""
    script = (
        "import sys\n"
        "from ycli.cli.app import app\n"
        "try:\n"
        f"    app({argv!r})\n"
        "except SystemExit:\n"
        "    pass\n"
        "print('\\n'.join(m for m in sys.modules if m.startswith('ycli')))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=True
    )
    return set(result.stdout.split())


def test_version_and_root_help_import_no_service():
    for argv in (["--version"], ["--help"]):
        modules = _imported_after(argv)
        assert not any(".client" in m or m.endswith(".cli") for m in modules if m != "ycli.cli")
        assert "ycli.yandex.tracker.cli" not in modules


def test_a_service_command_loads_only_that_service():
    modules = _imported_after(["forms", "surveys", "--help"])
    assert "ycli.yandex.forms.cli" in modules
    assert "ycli.yandex.tracker.cli" not in modules
    assert "ycli.yandex.wiki.cli" not in modules


def test_root_help_lists_every_sub_app_from_its_declaration():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    for name in ("tracker", "wiki", "forms", "auth", "mcp"):
        assert name in result.stdout


def test_lazy_group_loads_once_and_keeps_the_declared_help():
    group = LazyGroup(SubApp("mcp", "Declared help.", "ycli.mcp.cli:app"))
    loaded = group.load()
    assert group.load() is loaded
    assert loaded.help == "Declared help."
    assert "start" in group.list_commands(typer.Context(group))
    assert group.get_command(typer.Context(group), "methods") is not None


def test_unknown_command_is_still_an_error():
    root = get_command(app)
    assert root.get_command(typer.Context(root), "nope") is None  # ty: ignore[unresolved-attribute]


def test_a_lazy_command_loads_as_the_command_itself():
    group = LazyGroup(SubApp("api", "Declared help.", "ycli.cli.api:app", command=True))
    loaded = group.load()
    assert not isinstance(loaded, TyperGroup)
    assert loaded.help != "Declared help."  # the command keeps its own docstring
    assert group.list_commands(typer.Context(group)) == []
    assert group.get_command(typer.Context(group), "anything") is None
