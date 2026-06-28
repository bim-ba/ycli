"""Post-build smoke test for the distribution.

Run against a freshly built wheel/sdist in CI to catch a packaging mistake (a
missing module, a broken entry point) before publishing:

    uv run --isolated --no-project --with dist/*.whl smoke_test.py

Lives at the repo root (not under ``tests/``) so the coverage-gated pytest suite
does not collect it, and it is excluded from the published distribution.
"""

from importlib import resources

import ycli
from ycli import cli

# Verify the BASE install (no 'mcp' extra): the package and the CLI entry point
# import without pulling in fastmcp. The `ycli mcp` subcommand is registered here
# but only imports the server lazily, so this must not require the extra.
assert callable(cli.main), "ycli entry point missing"
assert any(c.name == "mcp" for c in cli.app.registered_commands), "mcp subcommand missing"

# The PEP 561 marker must survive the build into the installed package, or
# downstream type checkers won't see ycli's types.
assert resources.files("ycli").joinpath("py.typed").is_file(), "py.typed not shipped in the dist"

print(
    f"smoke test OK — {ycli.__name__} {ycli.__version__} imports; CLI + mcp subcommand + py.typed present"
)
