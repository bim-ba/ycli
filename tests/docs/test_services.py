"""The service cards and overview pages of the site come from the registry (issue #383).

``scripts/gen_services.py`` writes the fragments the pages include; nothing countable on them
is typed by hand, and a service in the registry has a card, an emoji and an overview page.
"""

from __future__ import annotations

import dataclasses
import re
import tomllib
from pathlib import Path

import pytest
from scripts import gen_coverage, gen_services

from ycli.yandex.registry import SERVICES

ROOT = Path(__file__).resolve().parents[2]
NAMES = [service.name for service in SERVICES]
LINK = re.compile(r"\]\(([^)\s]+)\)")
INCLUDE = '--8<-- "docs/examples/services/{}"'


def _fact(name: str, **changes: object) -> gen_services.Facts:
    fact = gen_services.Facts(
        name=name,
        titles={"en": name.capitalize(), "ru": name.capitalize()},
        summaries={"en": "Things.", "ru": "Вещи."},
        emoji="📋",
        operations=7,
        wrapped=7,
        published=7,
        in_progress=False,
    )
    return dataclasses.replace(fact, **changes)


def test_the_generated_fragments_are_fresh():
    assert gen_services.main(["--check"]) == 0, "run: uv run scripts/gen_services.py"


@pytest.mark.parametrize("table", ["TITLES", "EMOJI", "SUMMARIES_RU"])
def test_every_registry_service_has_its_presentation(table):
    assert set(getattr(gen_coverage, table)) == set(NAMES)


def test_in_progress_is_derived_from_the_published_operations():
    """Left out on purpose is not pending: only an operation still to wrap makes it so."""
    drifts = {drift.service: drift for drift in gen_coverage.api_drifts()}
    tracker = drifts["tracker"]
    assert tracker.excluded, "the case needs a service that leaves an operation out on purpose"
    assert not gen_services.in_progress(tracker)
    one = tracker.published[:1]
    assert gen_services.in_progress(dataclasses.replace(tracker, pending=one))
    assert gen_services.in_progress(dataclasses.replace(tracker, not_wrapped=one))


def test_the_facts_follow_the_registry_and_the_coverage_counts():
    found = gen_services.facts()
    assert [fact.name for fact in found] == NAMES
    reports = {report.slug: report.operation_count for report in gen_coverage._reports()}
    drifts = {drift.service: drift for drift in gen_coverage.api_drifts()}
    for fact in found:
        assert fact.operations == reports[fact.name]
        assert (fact.wrapped, fact.published) == (
            drifts[fact.name].wrapped,
            len(drifts[fact.name].published),
        )
        assert fact.in_progress == gen_services.in_progress(drifts[fact.name])


@pytest.mark.parametrize("language", gen_services.LANGUAGES)
def test_a_card_per_service_links_to_its_overview(language):
    done = _fact("alpha")
    pending = _fact("beta", wrapped=2, published=9, in_progress=True)
    text = gen_services.cards([done, pending], language)
    first, second = text.split("-   ")[1:]
    assert "(services/alpha.md)" in first and "<mark>" not in first
    assert "7" in first and "9" not in first
    assert "(services/beta.md)" in second
    assert f"<mark>{gen_services.IN_PROGRESS[language]}</mark>" in second
    assert re.search(r"\b2\b.*\b9\b", second)
    assert text.count(gen_services.SURFACES) == 2


def test_the_slogan_names_every_service():
    found = [_fact("alpha"), _fact("beta"), _fact("gamma")]
    assert "** Alpha, Beta and Gamma from " in gen_services.slogan(found, "en")
    assert "** Alpha, Beta и Gamma из " in gen_services.slogan(found, "ru")


def test_the_heading_of_an_overview_carries_no_mark():
    """A mark in the heading would enter the page's title and the navigation."""
    text = gen_services.header(_fact("beta", wrapped=2, published=9, in_progress=True), "en")
    heading, rest = text.split("\n", 1)
    assert heading == "# 📋 Beta"
    assert "<mark>in progress</mark>" in rest and "2 of the 9 operations" in rest
    assert "<mark>" not in gen_services.header(_fact("alpha"), "en")


def test_the_one_line_is_the_help_without_the_service_name():
    service = dataclasses.replace(SERVICES[0], help="Yandex Things: one, two.")
    assert gen_services.summary(service) == "One, two."
    with pytest.raises(SystemExit, match="help has no"):
        gen_services.summary(dataclasses.replace(service, help="Things"))


@pytest.mark.parametrize("language", gen_services.LANGUAGES)
def test_signing_in_names_what_the_profile_takes(language):
    profiles = {service.name: service.profile for service in SERVICES}
    tracker = gen_services.sign_in(profiles["tracker"], language)
    assert "`YANDEX_ID_OAUTH_TOKEN`" in tracker and "`X-Org-Id`" in tracker
    datalens = gen_services.sign_in(profiles["datalens"], language)
    assert "`YANDEX_ID_OAUTH_TOKEN`" not in datalens and "`X-Org-Id`" not in datalens
    assert "`YANDEX_CLOUD_ORGANIZATION_ID`" in datalens and "`x-dl-org-id`" in datalens
    neither = dataclasses.replace(profiles["tracker"], org_header=None, cloud_org_header=None)
    assert "_ORGANIZATION_ID" not in gen_services.sign_in(neither, language)


@pytest.mark.parametrize("language", gen_services.LANGUAGES)
def test_every_service_has_an_overview_page_made_of_the_shared_blocks(language):
    for name in NAMES:
        page = (ROOT / "docs" / language / "services" / f"{name}.md").read_text(encoding="utf-8")
        for block in ("header", "sign-in", "links"):
            assert INCLUDE.format(f"{name}.{block}.{language}.md") in page
        assert '--8<-- "docs/examples/operations/' in page


@pytest.mark.parametrize("language", gen_services.LANGUAGES)
def test_the_home_page_shows_the_cards_right_under_the_buttons(language):
    page = (ROOT / "docs" / language / "index.md").read_text(encoding="utf-8")
    slogan = page.index(INCLUDE.format(f"slogan.{language}.md"))
    buttons = page.index("{ .md-button }")
    cards = page.index(INCLUDE.format(f"cards.{language}.md"))
    assert slogan < buttons < cards < page.index("\n## ")


def test_the_home_page_description_names_every_service():
    page = (ROOT / "docs" / "en" / "index.md").read_text(encoding="utf-8")
    description = page.split("\n")[1]
    assert description.startswith("description: ")
    assert [name for name in NAMES if gen_coverage.TITLES[name][0] not in description] == []


@pytest.mark.parametrize(("config", "title"), [("zensical.toml", 0), ("zensical.ru.toml", 1)])
def test_the_site_descriptions_name_every_service(config, title):
    """A site's configuration takes no generated value: its two descriptions are checked."""
    project = tomllib.loads((ROOT / config).read_text(encoding="utf-8"))["project"]
    titles = [gen_coverage.TITLES[name][title] for name in NAMES]
    for description in (
        project["site_description"],
        project["plugins"]["llmstxt"]["markdown_description"].split("\n\n")[0],
    ):
        assert [found for found in titles if found not in description] == [], description


def test_an_emoji_is_the_character_itself():
    """A ``:shortcode:`` would be rendered as an image loaded from a CDN."""
    for emoji in gen_coverage.EMOJI.values():
        assert ":" not in emoji and not emoji.isascii()
    built = gen_services.build()
    assert [path.name for path, text in built.items() if re.search(r":[a-z_]+:", text)] == []


@pytest.mark.parametrize("language", gen_services.LANGUAGES)
def test_every_relative_link_of_a_fragment_resolves(language):
    """A fragment's links are relative to the page that includes it."""
    docs = ROOT / "docs" / language
    for path, text in gen_services.build().items():
        if not path.name.endswith(f".{language}.md"):
            continue
        base = docs if path.name.startswith(("cards.", "slogan.")) else docs / "services"
        for target in LINK.findall(text):
            if target.startswith("https://"):
                continue
            assert (base / target.split("#", 1)[0]).resolve().is_file(), f"{path.name}: {target}"


def test_the_guide_a_service_links_to_exists():
    page = ROOT / "docs" / "en" / "reference" / "mcp" / "prompts-and-resources.md"
    text = page.read_text(encoding="utf-8")
    assert "## Guides" in text
    assert [name for name in NAMES if f"`ycli://{name}/guide`" not in text] == []


def test_the_check_bites(tmp_path, monkeypatch, capsys):
    """A stale fragment, a missing one and an unused one are each reported."""
    fragments = tmp_path / "docs" / "examples" / "services"
    monkeypatch.setattr(gen_services, "ROOT", tmp_path)
    monkeypatch.setattr(gen_services, "FRAGMENTS", fragments)
    assert gen_services.main(["--check"]) == 1
    assert "stale: docs/examples/services/cards.en.md" in capsys.readouterr().err
    assert gen_services.main([]) == 0
    assert gen_services.main(["--check"]) == 0
    (fragments / "cards.en.md").write_text("old\n", encoding="utf-8")
    (fragments / "unused.md").write_text("x\n", encoding="utf-8")
    assert gen_services.main(["--check"]) == 1
    err = capsys.readouterr().err
    assert "stale: docs/examples/services/cards.en.md" in err
    assert "stale: docs/examples/services/unused.md" in err
    assert gen_services.main([]) == 0
    assert not (fragments / "unused.md").exists()
    assert gen_services.main(["--check"]) == 0
