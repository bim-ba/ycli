"""The README Coverage tables are generated from the code and never drift by hand.

Mirrors ``tests/test_snapshots.py``: instead of a committed snapshot file, the source of
truth is ``scripts/gen_coverage.py`` (which introspects the live domain clients). The block
embedded in ``README.md`` between the ``COVERAGE:START`` / ``COVERAGE:END`` markers must equal
the generator's output, so the tables cannot silently fall out of sync with the code.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HINT = "run `uv run python scripts/gen_coverage.py --write` to regenerate the README tables"


def _load_generator():
    spec = importlib.util.spec_from_file_location(
        "gen_coverage", ROOT / "scripts" / "gen_coverage.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses needs the module registered to resolve fields
    spec.loader.exec_module(module)
    return module


gen = _load_generator()


def test_readme_coverage_block_matches_generator():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert gen.START in readme and gen.END in readme, "README is missing the COVERAGE markers"
    committed = readme[readme.index(gen.START) : readme.index(gen.END) + len(gen.END)]
    assert committed == gen.build_block(), f"README coverage block is stale; {HINT}"


def test_generator_check_mode_passes():
    assert gen.main(["--check"]) == 0, f"gen_coverage --check reported drift; {HINT}"
