"""Property accessor on the PageDetails model — populated and None branches."""

import pytest
from pydantic import ValidationError

from ycli.yandex.models import ItemList
from ycli.yandex.wiki.models import AsyncOperation, CursorPage
from ycli.yandex.wiki.pages.models import (
    GridRef,
    PageAppendContent,
    PageAppendContentAnchor,
    PageAppendContentBody,
    PageAppendContentSection,
    PageClone,
    PageDeleteResult,
    PageDetails,
    PageMove,
    PageMoveStep,
    PageRevision,
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
    lst = ItemList[GridRef]([GridRef(id="g1", title="T")])
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
    op = AsyncOperation.model_validate(
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
        reply = AsyncOperation.model_validate({"operation": {"type": kind, "id": "t"}})
        assert reply.operation is not None and reply.operation.type == kind


def test_a_move_always_states_whether_to_copy_inherited_access():
    """The API answers 400 INHERITANCE_BEHAVIOR_IS_NOT_SPECIFIED for a missing value."""
    step = PageMoveStep(source="eng/a", target="eng/b")
    assert PageMove(operations=[step]).model_dump(exclude_none=True) == {
        "operations": [{"source": "eng/a", "target": "eng/b"}],
        "copy_inherited_access": False,
    }


def test_a_move_needs_at_least_one_step():
    with pytest.raises(ValidationError):
        PageMove(operations=[])


def test_a_move_step_refuses_an_unknown_position():
    with pytest.raises(ValidationError):
        PageMoveStep.model_validate({"source": "a", "target": "b", "position": "inside"})


def test_a_move_reply_names_the_task_to_poll():
    reply = AsyncOperation.model_validate(
        {
            "operation": {"type": "move", "id": "0807ca4b"},
            "status_url": "/v1/operations/move/0807ca4b",
            "dry_run": True,
        }
    )
    assert reply.operation is not None and reply.operation.id == "0807ca4b"
    assert reply.dry_run is True


def test_a_revision_parses_as_the_api_sends_it():
    """Shape taken from a live ``GET /pages/{id}/revisions`` reply (2026-10-02)."""
    reply = CursorPage[PageRevision].model_validate(
        {
            "results": [
                {
                    "id": 76188809,
                    "author": {
                        "id": 80496450,
                        "identity": {"uid": "101523906", "cloud_uid": "ajen8nffceu4rqs0i39r"},
                        "username": "znatnov-sava",
                        "display_name": "Sava",
                        "is_dismissed": False,
                        "affiliation": "",
                    },
                    "created_at": "2026-10-02T18:30:32.721Z",
                    "page_type": "wysiwyg",
                    "revision_draft": {
                        "id": 5,
                        "created_at": "2026-10-02T18:30:00Z",
                        "modified_at": "2026-10-02T18:30:30Z",
                    },
                    "publication": {"status": "pending_publication"},
                }
            ],
            "next_cursor": None,
        }
    )
    revision = reply.results[0]
    assert revision.author is not None and revision.author.username == "znatnov-sava"
    assert revision.revision_draft is not None and revision.revision_draft.id == 5
    assert revision.publication is not None
    assert revision.publication.status == "pending_publication"
    assert ItemList[PageRevision]([revision]).root[0].id == 76188809


def test_a_revision_without_draft_or_publication_parses():
    revision = PageRevision.model_validate({"id": 7, "revision_draft": None, "publication": None})
    assert revision.revision_draft is None and revision.publication is None
