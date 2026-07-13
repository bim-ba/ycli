"""The README Coverage tables are generated from the code and never drift by hand.

Mirrors ``tests/test_snapshots.py``: instead of a committed snapshot file, the source of
truth is ``scripts/gen_coverage.py`` (which introspects the live domain clients). The block
embedded in ``README.md`` between the ``COVERAGE:START`` / ``COVERAGE:END`` markers must equal
the generator's output, so the tables cannot silently fall out of sync with the code.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HINT = "run `uv run python scripts/gen_coverage.py --write` to regenerate the README tables"
DOCS_BASE = "https://yandex.ru/support/"
LINK = re.compile(r"\[[^\]]+\]\((https?://[^)]+)\)")

# The one resource/operation with no public API-reference page. Pinned so a *new* gap
# (e.g. a resource added without a doc link) fails loudly instead of slipping in silently.
EXPECTED_LINK_GAPS = ("tracker.linktypes", "tracker.linktypes.list")


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


def test_generated_doc_links_are_well_formed():
    """Every deep link points at the Yandex api-ref and cannot break a Markdown table cell."""
    urls = LINK.findall(gen.build_block())
    assert urls, "no documentation links were generated"
    for url in urls:
        assert url.startswith(DOCS_BASE), url
        assert "/api-ref/" in url and not url.endswith(".md"), url
        assert " " not in url and "|" not in url, url


def test_link_gaps_are_pinned():
    """The only unlinked (plain-text) items are the known ones — new gaps must be explicit."""
    stats = gen.link_stats(gen._reports())
    assert stats.gaps == EXPECTED_LINK_GAPS


def test_link_stats_totals_are_consistent():
    stats = gen.link_stats(gen._reports())
    assert stats.specific_ops + stats.fallback_ops + stats.plain_ops == stats.operations
    assert stats.linked_resources <= stats.resources
    # The vast majority of operations deep-link to their own endpoint page.
    assert stats.specific_ops > stats.fallback_ops + stats.plain_ops
    assert stats.plain_ops == 1 and stats.linked_resources == stats.resources - 1


def test_link_map_keys_reference_real_resources_and_operations():
    """Guard against typos: every key in coverage_urls.toml maps to a live resource/op."""
    real: dict[tuple[str, str], set[str]] = {}
    for report in gen._reports():
        for _heading, rows in report.groups:
            for row in rows:
                real[(report.slug, row.display)] = set(row.operations)
    for slug, resources in gen._load_link_map().items():
        for resource, entry in resources.items():
            assert (slug, resource) in real, f"unknown resource {slug}.{resource} in link map"
            for operation in entry.get("operations", {}):
                assert operation in real[(slug, resource)], (
                    f"link map references unknown operation {slug}.{resource}.{operation}"
                )


def test_unlinked_resource_renders_as_plain_text():
    line = next(row for row in gen.build_block().splitlines() if row.startswith("| linktypes "))
    assert "](" not in line, "linktypes has no public doc page and must stay plain text"


def test_check_mode_surfaces_link_gaps_on_stderr(capsys):
    assert gen.main(["--check"]) == 0
    err = capsys.readouterr().err
    assert "operations → their own page" in err
    assert "Gaps (no public link): tracker.linktypes" in err
