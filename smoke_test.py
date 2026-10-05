"""Post-build smoke test for the distribution.

Run against a freshly built wheel/sdist in CI to catch a packaging mistake (a
missing module, a broken entry point) before publishing:

    uv run --isolated --no-project --with dist/*.whl smoke_test.py

Lives at the repo root (not under ``tests/``) so the coverage-gated pytest suite
does not collect it, and it is excluded from the published distribution.
"""

from importlib import resources

import typer
import typer.main
from typer.core import TyperGroup

import ycli
import ycli.cli.app as cli

# Verify the BASE install (no 'mcp' extra): the package and the CLI entry point
# import without pulling in fastmcp. The `ycli mcp` subcommand is listed by the root and
# loaded on first use; loading it must not require the extra either.
assert callable(cli.main), "ycli entry point missing"
root = typer.main.get_group(cli.app)
context = typer.Context(root)
for name in ("tracker", "wiki", "forms", "auth", "mcp"):
    assert name in root.list_commands(context), f"{name} subcommand missing"
mcp_group = root.get_command(context, "mcp")
assert isinstance(mcp_group, TyperGroup), "mcp is not a command group"
assert "start" in mcp_group.list_commands(context), "mcp start missing"

# Building every domain client imports its whole SDK, so a runtime dependency the base install
# lacks fails here; no request is sent.
from ycli.yandex.registry import SERVICES  # noqa: E402

for service in SERVICES:
    with service.client_class()(
        oauth_token="smoke", organization_id="smoke", cloud_organization_id="smoke"
    ):
        pass

# The MCP guides are links to the plugin's skills in the repository: the distribution must
# hold the text itself, not a dangling link or a one-line path.
for package in ("ycli.mcp", *(f"ycli.yandex.{service.name}.mcp" for service in SERVICES)):
    guide = resources.files(package).joinpath("guide.md").read_text(encoding="utf-8")
    assert guide.startswith("---\nname: yandex-360"), f"{package}: guide.md is not the skill"

# The PEP 561 marker must survive the build into the installed package, or
# downstream type checkers won't see ycli's types.
assert resources.files("ycli").joinpath("py.typed").is_file(), "py.typed not shipped in the dist"

print(
    f"smoke test OK — {ycli.__name__} {ycli.__version__} imports; "
    "CLI + mcp subcommand + domain clients + py.typed present"
)
