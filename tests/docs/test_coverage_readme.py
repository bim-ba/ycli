"""The README Coverage tables are generated from the code and never drift by hand.

Mirrors ``architecture/test_snapshots.py``: instead of a committed snapshot file, the source of
truth is ``scripts/gen_coverage.py`` (which introspects the live domain clients). The block
embedded in ``README.md`` between the ``COVERAGE:START`` / ``COVERAGE:END`` markers must equal
the generator's output, so the tables cannot silently fall out of sync with the code.
"""

import importlib.util
import re
import sys
from pathlib import Path

from scripts import api_drift, api_surface

ROOT = Path(__file__).resolve().parents[2]
HINT = "run `uv run python scripts/gen_coverage.py --write` to regenerate the README tables"
LINK = re.compile(r"\[[^\]]+\]\((https?://[^)]+)\)")
# The published-API summary links each OpenAPI document, the one link outside the reference.
OPENAPI_URLS = frozenset(
    source.url for source in api_surface.SOURCES.values() if source.kind == "openapi"
)

# The resources and operations with no public API-reference page. Pinned so a *new* gap
# (e.g. a resource added without a doc link) fails loudly instead of slipping in silently.
EXPECTED_LINK_GAPS = (
    # The published reference has no page for the saved SQL queries (experimental, 2026-10-06).
    "datalens.sqlqueries",
    "datalens.sqlqueries.create",
    "datalens.sqlqueries.delete",
    "datalens.sqlqueries.get",
    "datalens.sqlqueries.run",
    "datalens.sqlqueries.update",
    "datalens.tenant",
    "datalens.tenant.details_get",
    "tracker.linktypes",
    "tracker.linktypes.list",
)


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
    """Every table link points at the Yandex API reference and cannot break a table cell."""
    table_rows = [line for line in gen.build_block().splitlines() if line.startswith("| ")]
    urls = [url for row in table_rows for url in LINK.findall(row)]
    assert urls, "no documentation links were generated"
    for url in urls:
        if url in OPENAPI_URLS:
            continue
        assert any(url.startswith(docs.format(path="")) for docs in gen.API_DOCS.values()), url
        assert not url.endswith(".md"), url
        assert " " not in url and "|" not in url, url


def test_committed_svg_matches_generator():
    committed = gen.COVERAGE_SVG.read_text(encoding="utf-8")
    assert committed == gen.render_svg(gen._reports()), f"coverage.svg is stale; {HINT}"


def test_check_mode_fails_on_a_stale_svg(tmp_path, monkeypatch, capsys):
    stale = tmp_path / "coverage.svg"
    stale.write_text("<svg/>", encoding="utf-8")
    monkeypatch.setattr(gen, "COVERAGE_SVG", stale)
    assert gen.main(["--check"]) == 1
    assert "stale: coverage.svg" in capsys.readouterr().err


def test_svg_shows_every_service_and_the_totals():
    svg = gen.render_svg(gen._reports())
    for report in gen._reports():
        assert f">{report.title}</text>" in svg
        assert f">{report.operation_count} operations · {report.mcp_tool_count} MCP tools<" in svg
    assert gen.COVERAGE_SVG_URL in gen.build_block()


def test_every_service_table_is_collapsible():
    """Each service's tables sit in one <details>, with the blank line GitHub needs after it."""
    block = gen.build_block()
    for report in gen._reports():
        heading = block.index(f"### {report.title}\n\n<details>\n<summary>")
        assert "</summary>\n\n**" in block[heading:]
    # One block of tables and one of differences from the published API per service.
    assert block.count("<details>") == block.count("</details>") == 2 * len(gen._reports())


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
    assert stats.plain_ops == 7 and stats.linked_resources == stats.resources - 3


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
    assert "Gaps (no public link): datalens.sqlqueries" in err


def test_the_russian_readme_carries_the_same_totals():
    readme = (ROOT / "README.ru.md").read_text(encoding="utf-8")
    block = readme[readme.index(gen.START) : readme.index(gen.END)]
    for report in gen._reports():
        assert f"— {report.operation_count}" in block
    assert gen.COVERAGE_SVG_URL in block
    assert "README.md#coverage" in block


def test_check_mode_fails_on_a_stale_russian_readme(tmp_path, monkeypatch, capsys):
    stale = tmp_path / "README.ru.md"
    stale.write_text(f"{gen.START}\nold\n{gen.END}\n", encoding="utf-8")
    monkeypatch.setattr(gen, "README_RU", stale)
    assert gen.main(["--check"]) == 1
    assert "stale: README.ru.md" in capsys.readouterr().err


def _drift(published: list[api_surface.Operation]) -> api_drift.Drift:
    """A Wiki drift over a fixture snapshot: ycli wraps ``pages.get`` and sends ``fields``."""
    sent = [
        api_drift.Call(
            "wiki.pages.get", "GET", "/pages/7", query=frozenset({"fields"}), response=None
        )
    ]
    return api_drift.compare("wiki", published, sent)


def test_an_operation_added_to_a_snapshot_shows_as_not_covered():
    """After a refresh the tables say what is new without a hand edit (#193)."""
    get = api_surface.Operation("GET", "/pages/{idx}", query=("fields",))
    assert gen._render_not_covered(_drift([get])) == []
    added = api_surface.Operation("POST", "/pages/{idx}/archive")
    assert gen._render_not_covered(_drift([get, added])) == [
        "",
        "**Not covered** (1)",
        "",
        f"- {gen.NOT_COVERED} `POST /pages/{{idx}}/archive`",
    ]


def test_a_parameter_added_to_a_snapshot_marks_the_operation_partial():
    get = api_surface.Operation("GET", "/pages/{idx}", query=("fields",))
    assert api_drift.partial([_drift([get])]) == {}
    grown = api_surface.Operation("GET", "/pages/{idx}", query=("fields", "depth"))
    gaps = api_drift.partial([_drift([grown])])
    assert gaps == {"wiki.pages.get": "differs-wiki-get-pages-idx"}

    class Pages:
        def get(self) -> None: ...

        def create(self) -> None: ...

    row = gen._make_row("wiki", "pages", Pages(), {}, [], [], gaps)
    assert row.operation_gaps == ("differs-wiki-get-pages-idx", None)
    table = "\n".join(gen._render_table([row]))
    assert f"get [{gen.PARTIAL}](#differs-wiki-get-pages-idx) · create |" in table
    assert Pages().get() is None and Pages().create() is None  # the stubs are only inspected


def test_every_partial_mark_links_to_a_row_that_exists():
    block = gen.build_block()
    targets = set(re.findall(rf"\[{gen.PARTIAL}\]\(#([a-z0-9-]+)\)", block))
    anchors = set(re.findall(r'<a id="(differs-[a-z0-9-]+)"></a>', block))
    assert targets and targets <= anchors
