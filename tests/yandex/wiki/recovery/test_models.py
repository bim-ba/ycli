"""PageIdentity parses the restore response — populated and empty branches."""

from ycli.yandex.wiki.models import PageIdentity


def test_recovered_page_parses_id_and_slug():
    page = PageIdentity.model_validate({"id": 42, "slug": "data/x"})
    assert page.id == 42 and page.slug == "data/x"


def test_recovered_page_defaults_to_none():
    page = PageIdentity.model_validate({})
    assert page.id is None and page.slug is None
