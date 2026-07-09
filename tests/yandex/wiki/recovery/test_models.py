"""RecoveredPage parses the restore response — populated and empty branches."""

from ycli.yandex.wiki.recovery.models import RecoveredPage


def test_recovered_page_parses_id_and_slug():
    page = RecoveredPage.model_validate({"id": 42, "slug": "data/x"})
    assert page.id == 42 and page.slug == "data/x"


def test_recovered_page_defaults_to_none():
    page = RecoveredPage.model_validate({})
    assert page.id is None and page.slug is None
