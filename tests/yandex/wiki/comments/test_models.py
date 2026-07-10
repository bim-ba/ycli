"""Wiki Comment author flattens to a bare scalar — populated and None branches."""

import pytest
from pydantic import ValidationError

from ycli.yandex.wiki.comments.models import (
    Comment,
    CommentCreate,
    CommentCreated,
    CommentDeleteResult,
)


def test_author_flattens_to_scalar():
    assert Comment.model_validate({"author": {"display_name": "Сава"}}).author == "Сава"
    assert Comment.model_validate({"body": "ok"}).author is None


def test_content_reads_body_key():
    assert Comment.model_validate({"body": "hello"}).content == "hello"


def test_comment_create_drops_none_placement_fields():
    assert CommentCreate(body="hi").model_dump(exclude_none=True) == {"body": "hi"}


def test_comment_create_keeps_supplied_placement_fields():
    payload = CommentCreate(body="hi", inline_text="quote", parent_id=1, thread_id=2)
    assert payload.model_dump(exclude_none=True) == {
        "body": "hi",
        "inline_text": "quote",
        "parent_id": 1,
        "thread_id": 2,
    }


def test_comment_create_rejects_empty_body():
    with pytest.raises(ValidationError):
        CommentCreate(body="")


def test_comment_created_parses_id():
    assert CommentCreated.model_validate({"id": 5, "body": "LGTM"}).id == 5


def test_comment_delete_result_parses_count():
    assert CommentDeleteResult.model_validate({"comments_count": 4}).comments_count == 4
