"""Property accessor on the PageDetails model — populated and None branches."""
from ycli.yandex.wiki.pages.models import PageDetails


def test_owner_username_populated():
    page = PageDetails.model_validate(
        {"id": 42, "slug": "data/x", "title": "X", "owner": {"user": {"username": "ivan"}}}
    )
    assert page.owner_username == "ivan"


def test_owner_username_none_when_owner_missing():
    page = PageDetails.model_validate({"id": 42, "slug": "data/x", "title": "X"})
    assert page.owner_username is None
