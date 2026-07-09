"""Property accessor on the PageDetails model — populated and None branches."""

from ycli.yandex.wiki.pages.models import GridRef, GridRefList, PageDetails


def test_owner_username_populated():
    page = PageDetails.model_validate(
        {"id": 42, "slug": "data/x", "title": "X", "owner": {"user": {"username": "ivan"}}}
    )
    assert page.owner_username == "ivan"


def test_owner_username_none_when_owner_missing():
    page = PageDetails.model_validate({"id": 42, "slug": "data/x", "title": "X"})
    assert page.owner_username is None


def test_grid_ref_parses_uuid_id_and_optional_fields():
    grid = GridRef.model_validate({"id": "abc-uuid", "title": "Roadmap"})
    assert grid.id == "abc-uuid" and grid.title == "Roadmap"
    assert grid.created_at is None


def test_grid_ref_list_wraps_flat_root():
    lst = GridRefList([GridRef(id="g1", title="T")])
    assert lst.root[0].id == "g1"
