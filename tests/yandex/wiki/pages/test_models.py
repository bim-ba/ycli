"""Property accessor on the PageDetails model — populated and None branches."""

import pytest
from pydantic import ValidationError

from ycli.yandex.wiki.pages.models import (
    GridRef,
    GridRefList,
    PageAppendContent,
    PageAppendContentAnchor,
    PageAppendContentBody,
    PageAppendContentSection,
    PageClone,
    PageCloneOperation,
    PageDeleteResult,
    PageDetails,
)


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


def test_page_delete_result_parses_recovery_token():
    assert (
        PageDeleteResult.model_validate({"recovery_token": "tok-uuid"}).recovery_token == "tok-uuid"
    )


def test_append_content_minimal_dumps_only_content():
    assert PageAppendContent(content="hi").model_dump(exclude_none=True) == {"content": "hi"}


def test_append_content_full_nested_dump():
    payload = PageAppendContent(
        content="body",
        body=PageAppendContentBody(location="bottom"),
        section=PageAppendContentSection(id=3, location="top"),
        anchor=PageAppendContentAnchor(name="Roadmap", fallback=True, regex=True),
    )
    assert payload.model_dump(exclude_none=True) == {
        "content": "body",
        "body": {"location": "bottom"},
        "section": {"id": 3, "location": "top"},
        "anchor": {"name": "Roadmap", "fallback": True, "regex": True},
    }


def test_append_content_rejects_empty_content():
    with pytest.raises(ValidationError):
        PageAppendContent(content="")


def test_append_content_body_rejects_invalid_location():
    with pytest.raises(ValidationError):
        PageAppendContentBody(location="middle")  # ty: ignore[invalid-argument-type]


def test_page_clone_dumps_only_set_fields():
    assert PageClone(target="data/y", subscribe_me=True).model_dump(exclude_none=True) == {
        "target": "data/y",
        "subscribe_me": True,
    }


def test_page_clone_rejects_empty_title():
    with pytest.raises(ValidationError):
        PageClone(target="data/y", title="")


def test_page_clone_operation_parses_identity():
    op = PageCloneOperation.model_validate(
        {"operation": {"type": "clone", "id": "task-1"}, "status_url": "u"}
    )
    assert op.operation is not None and op.operation.id == "task-1"
    assert op.status_url == "u"


def test_page_details_keeps_the_access_fields_a_page_returns():
    page = PageDetails.model_validate(
        {
            "id": 42,
            "slug": "data/x",
            "title": "X",
            "owner": {"user": {"id": 1, "username": "ivan", "display_name": "Ivan"}, "group": None},
            "access_policy": {"access_type": "custom", "all_staff_role": "reader"},
            "access_lists": {
                "direct": [{"id": "9", "role": "author", "inheritance": "inherited"}],
                "by_link": [],
                "inherited": [],
            },
        }
    )
    assert page.owner_username == "ivan"
    assert page.access_policy is not None and page.access_policy.access_type == "custom"
    assert page.access_lists is not None and page.access_lists.direct[0].id == "9"


def test_a_page_without_access_fields_leaves_them_unset():
    page = PageDetails.model_validate({"id": 42, "slug": "data/x", "title": "X"})
    assert page.access_policy is None and page.access_lists is None


def test_clone_operation_identity_accepts_every_operation_kind():
    for kind in ("move", "clone", "clone_inline_grid"):
        reply = PageCloneOperation.model_validate({"operation": {"type": kind, "id": "t"}})
        assert reply.operation is not None and reply.operation.type == kind
