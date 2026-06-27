"""Post-build smoke test for the distribution.

Run against a freshly built wheel/sdist in CI to catch a packaging mistake (a
missing module, a broken entry point) before publishing:

    uv run --isolated --no-project --with dist/*.whl smoke_test.py

Lives at the repo root (not under ``tests/``) so the coverage-gated pytest suite
does not collect it, and it is excluded from the published distribution.
"""

import ycli
from ycli import cli, mcp

# The console-script entry points (`ycli`, `ycli-mcp`) resolve to these callables.
assert callable(cli.main), "ycli entry point missing"
assert callable(mcp.main), "ycli-mcp entry point missing"

print(f"smoke test OK — {ycli.__name__} imports and exposes both entry points")
