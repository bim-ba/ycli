"""A file as a document of a kind: its link, its content, its fingerprint."""

from pathlib import PurePosixPath
from typing import Annotated

import pytest
from pydantic import BaseModel, Field

from ycli.yandex.models import NoDropNull, RequestBody
from ycli.yandex.sync.document import (
    Body,
    Document,
    Link,
    Parts,
    UnreadableFile,
    as_sent,
    body_field,
    document_of,
    fingerprint,
    parts_of,
)
from ycli.yandex.sync.formats import YAMLFile

PAGE = PurePosixPath("wiki/team/onboarding.md")
TRIGGER = PurePosixPath("tracker/queues/DE/triggers/16.yaml")


class PageLink(Link):
    """A kind names its version by the service's word for it."""

    id: int | None = None
    revision: int | None = None


class PageUpdate(RequestBody):
    """The body of a request stands in for the content of a file."""

    title: str | None = None
    content: Annotated[str | None, Body()] = None
    owner: str | None = None


class TriggerLink(Link):
    id: int | None = None
    version: int | None = None


class TriggerUpdate(RequestBody):
    name: str | None = None
    active: bool | None = None
    actions: list[dict[str, object]] | None = None
    before_id: int | None = Field(default=None, alias="beforeId")


def test_the_link_keys_go_to_the_link_and_the_rest_to_the_content():
    keys = {"id": 4821, "revision": 9917, "hash": "9f2c", "title": "Onboarding"}
    document = document_of(
        Parts(PAGE, "wiki/page", keys, "# First day\n"), link=PageLink, content=PageUpdate
    )
    assert document.link == PageLink(id=4821, revision=9917, hash="9f2c")
    assert document.content == PageUpdate(title="Onboarding", content="# First day\n")
    assert document.path == PAGE


def test_a_document_goes_back_to_the_parts_it_came_from():
    """Link keys first, the content in its model's order, the body apart, no empty key."""
    keys = {"id": 4821, "revision": 9917, "hash": "9f2c", "title": "Onboarding"}
    parts = Parts(PAGE, "wiki/page", keys, "# First day\n")
    document = document_of(parts, link=PageLink, content=PageUpdate)
    back = parts_of(document, kind="wiki/page")
    assert back == Parts(PAGE, "wiki/page", {"hash": "9f2c", **keys}, "# First day\n")
    assert list(back.keys) == ["hash", "id", "revision", "title"]
    assert document_of(back, link=PageLink, content=PageUpdate) == document


def test_a_kind_with_no_body_keeps_every_key_in_the_mapping():
    keys = {"id": 16, "version": 3, "name": "Assign", "beforeId": 4, "actions": [{"type": "X"}]}
    document = document_of(
        Parts(TRIGGER, "tracker/trigger", keys), link=TriggerLink, content=TriggerUpdate
    )
    assert document.content.before_id == 4
    back = parts_of(document, kind="tracker/trigger")
    assert back.text is None
    assert dict(back.keys) == keys  # the API's own names, as the file had them
    assert list(back.keys)[:2] == ["id", "version"]


def test_a_file_written_by_hand_for_a_new_object_has_no_link_yet():
    document = document_of(
        Parts(PAGE, "wiki/page", {"title": "New"}, "Text\n"), link=PageLink, content=PageUpdate
    )
    assert document.link == PageLink()
    assert parts_of(document, kind="wiki/page") == Parts(
        PAGE, "wiki/page", {"title": "New"}, "Text\n"
    )


def test_a_page_with_no_text_is_written_with_an_empty_body():
    document = Document(path=PAGE, link=PageLink(id=1), content=PageUpdate(title="Empty"))
    assert parts_of(document, kind="wiki/page").text == ""


@pytest.mark.parametrize(
    ("keys", "text", "link", "content", "line", "reason"),
    [
        # A key the content model does not have: the model names it, the line is the key's.
        ({"title": "T", "keywords": ["a"]}, "", PageLink, PageUpdate, 5, "keywords: Extra inputs"),
        # A link key of the wrong type.
        ({"id": "not a number"}, "", PageLink, PageUpdate, 3, "id: Input should be a valid int"),
        # A key the file does not say the line of points at the first line.
        ({"name": 7}, None, TriggerLink, TriggerUpdate, 1, "name: Input should be a valid str"),
        # Text under the header of a kind that keeps none.
        ({"name": "x"}, "words", TriggerLink, TriggerUpdate, 1, "keeps no text under its header"),
    ],
)
def test_a_key_that_does_not_fit_its_model_is_refused_with_its_line(
    keys, text, link, content, line, reason
):
    lines = {"id": 3, "title": 4, "keywords": 5}
    parts = Parts(PAGE, "wiki/page", keys, text, lines)
    with pytest.raises(UnreadableFile) as refusal:
        document_of(parts, link=link, content=content)
    assert (refusal.value.path, refusal.value.line) == (PAGE, line)
    assert reason in refusal.value.reason
    assert str(refusal.value).startswith(f"{PAGE}:{line}: ")


def test_a_refusal_does_not_repeat_the_value_it_refused():
    """A file may hold a secret: the error names the key, not what stood under it."""
    parts = Parts(PAGE, "wiki/page", {"id": "S3cret-value"}, "")
    with pytest.raises(UnreadableFile) as refusal:
        document_of(parts, link=PageLink, content=PageUpdate)
    assert "S3cret-value" not in str(refusal.value)


def test_the_fingerprint_follows_the_values_and_nothing_else():
    one = TriggerUpdate(name="Assign", active=True, actions=[{"type": "X", "to": {"a": 1, "b": 2}}])
    same = TriggerUpdate(
        actions=[{"to": {"b": 2, "a": 1}, "type": "X"}], active=True, name="Assign"
    )
    assert fingerprint(one) == fingerprint(same)
    assert len(fingerprint(one)) == 64
    # A field with no value is a field left out; any other difference is a difference.
    assert fingerprint(TriggerUpdate(name="Assign")) == fingerprint(
        TriggerUpdate(name="Assign", active=None)
    )
    assert fingerprint(one) != fingerprint(one.model_copy(update={"active": False}))
    assert fingerprint(one) != fingerprint(
        one.model_copy(update={"actions": [{"type": "X", "to": {"a": 1, "b": 3}}]})
    )
    # The body counts: it is content like any other field.
    assert fingerprint(PageUpdate(content="a")) != fingerprint(PageUpdate(content="b"))


def test_one_field_at_most_is_the_body():
    class Two(BaseModel):
        first: Annotated[str, Body()]
        second: Annotated[str, Body()]

    with pytest.raises(TypeError, match="more than one field"):
        body_field(Two)
    assert body_field(TriggerUpdate) is None


class DashboardSettings(RequestBody):
    """A field the API requires and lets be null (`NoDropNull`, #461)."""

    interval: Annotated[int | None, NoDropNull()] = None
    title: str | None = None


def test_a_null_the_api_requires_lives_through_the_file_and_counts_in_the_fingerprint():
    """A file is the body of a request: it is dumped the one way a body is, `null` and all."""
    asked = Document(path=TRIGGER, link=TriggerLink(id=1), content=DashboardSettings())
    parts = parts_of(asked, kind="datalens/dashboard")
    assert dict(parts.keys) == {"id": 1, "interval": None}  # `title` has no value: left out
    text = YAMLFile().write(parts)
    assert "interval: null\n" in text
    back = document_of(YAMLFile().read(TRIGGER, text), link=TriggerLink, content=DashboardSettings)
    assert back == asked
    assert as_sent(back.content) == {"interval": None}
    assert fingerprint(DashboardSettings()) != fingerprint(DashboardSettings(interval=5))
    # What a request leaves out does not count, set to nothing or never set.
    assert fingerprint(DashboardSettings()) == fingerprint(DashboardSettings(title=None))
