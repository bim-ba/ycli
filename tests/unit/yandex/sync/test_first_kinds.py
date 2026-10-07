"""The two first kinds: what their declarations and the marks of their operations say."""

from pathlib import PurePosixPath

from ycli.yandex.core.endpoint import Endpoint, Paged
from ycli.yandex.sync.document import body_field, document_of, fingerprint, parts_of
from ycli.yandex.sync.kind import Arguments, CheckedVersion, Operation, arguments_of
from ycli.yandex.tracker.triggers.sync import TRIGGER
from ycli.yandex.wiki.pages.sync import PAGE

PAGE_TEXT = """\
---
ycli: wiki/page
id: 4821
revision: 9917
title: Onboarding
---
# First day
"""
TRIGGER_TEXT = """\
ycli: tracker/trigger
id: 16
version: 3
name: Assign on create
actions:
- type: Transition
  status:
    key: inProgress
conditions:
- type: Event.create
active: true
"""


def _marks(operation: Operation | None) -> Arguments:
    assert operation is not None
    return arguments_of(operation)


def test_a_page_file_is_read_by_the_declaration_of_its_kind():
    path = PurePosixPath("wiki/team/onboarding.md")
    document = document_of(PAGE.layout.read(path, PAGE_TEXT), link=PAGE.link, content=PAGE.content)
    assert (document.link.id, document.link.revision) == (4821, 9917)
    assert (document.content.title, document.content.content) == ("Onboarding", "# First day\n")
    assert body_field(PAGE.content) == "content"
    assert PAGE.layout.write(parts_of(document, kind=PAGE.name)) == PAGE_TEXT


def test_a_trigger_file_is_read_by_the_declaration_of_its_kind():
    path = PurePosixPath("tracker/queues/DE/triggers/16.yaml")
    parts = TRIGGER.layout.read(path, TRIGGER_TEXT)
    document = document_of(parts, link=TRIGGER.link, content=TRIGGER.content)
    assert (document.link.id, document.link.version) == (16, 3)
    # What the API's own keys hold inside an action is kept as written; the keys of the
    # content come in the order of the request model.
    assert TRIGGER.layout.write(parts_of(document, kind=TRIGGER.name)) == TRIGGER_TEXT
    assert len(fingerprint(document.content)) == 64


def test_the_marks_of_the_operations_say_what_the_engine_passes_where():
    in_a_queue, one = ("queue_id",), ("trigger_id",)
    assert _marks(TRIGGER.read) == Arguments(identity=one, container=in_a_queue)
    assert _marks(TRIGGER.find) == Arguments(container=in_a_queue)
    assert _marks(TRIGGER.create) == Arguments(container=in_a_queue, body="body")
    assert _marks(TRIGGER.update) == Arguments(
        identity=one, container=in_a_queue, version="version", body="body"
    )
    assert TRIGGER.delete is None  # the API has no such operation
    assert _marks(PAGE.read) == Arguments(
        identity=("page_id",), left_out=("revision_id", "raise_on_redirect")
    )
    assert _marks(PAGE.find) == Arguments(container=("slug",), left_out=("actuality", "show_all"))
    assert _marks(PAGE.create) == Arguments(body="body", left_out=("fields", "is_silent"))
    assert _marks(PAGE.update) == Arguments(
        identity=("page_id",), body="body", left_out=("fields", "is_silent", "allow_merge")
    )
    assert _marks(PAGE.delete) == Arguments(identity=("page_id",), left_out=("recursive",))
    assert isinstance(PAGE.version, CheckedVersion)
    assert _marks(PAGE.version.newest) == Arguments(identity=("page_id",), left_out=("ids",))


def test_a_declaration_sets_only_what_the_kind_always_gives():
    """`read` of a page asks for the content; what it does not name goes out as nothing."""
    left_out = dict.fromkeys(_marks(PAGE.read).left_out)
    request = PAGE.read(4821, **left_out)
    assert isinstance(request, Endpoint)
    assert request.params == {"fields": "content", "revision_id": None, "raise_on_redirect": None}
    assert PAGE.find is not None
    listing = PAGE.find("team", **dict.fromkeys(_marks(PAGE.find).left_out))
    assert isinstance(listing, Paged) and listing.endpoint.params["include_self"] is True
