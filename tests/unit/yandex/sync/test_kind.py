"""A kind: the declaration of a resource, and what the marks of its operations say."""

from functools import partial
from http import HTTPMethod
from typing import Annotated, Any

import pytest

import ycli.yandex.sync as queues  # stands in for the package of a resource
from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.models import RequestBody
from ycli.yandex.sync.document import Link
from ycli.yandex.sync.formats import MarkdownWithHeader, YAMLFile
from ycli.yandex.sync.kind import (
    Arguments,
    CheckedVersion,
    Kind,
    NoVersion,
    SentVersion,
    arguments_of,
    summary_of,
)
from ycli.yandex.sync.marks import Container, Identity, Version

REQUEST: Endpoint[Any] = Endpoint(HTTPMethod.GET, "anything")
InQueue = Annotated[str, Container(queues)]
One = Annotated[int, Identity()]


class TriggerUpdate(RequestBody):
    name: str | None = None


# The operations of a resource as its `endpoints.py` describes them: marked arguments, and
# keyword arguments with no default.
def list_(queue_id: InQueue, *, page_size: int = 50) -> Endpoint[Any]:
    return REQUEST


def get(queue_id: InQueue, trigger_id: One) -> Endpoint[Any]:
    return REQUEST


def create(queue_id: InQueue, body: TriggerUpdate) -> Endpoint[Any]:
    return REQUEST


def update(
    queue_id: InQueue,
    trigger_id: One,
    body: TriggerUpdate,
    *,
    version: Annotated[int | None, Version()],
    notify: bool | None,
) -> Endpoint[Any]:
    return REQUEST


def access_update(
    page: Annotated[str, Identity()], subject: Annotated[str, Identity()]
) -> Endpoint[Any]:
    return REQUEST


def settings_get() -> Endpoint[Any]:
    return REQUEST


def search(text: Annotated[str, "what to look for"], *, fields: str | None) -> Endpoint[Any]:
    return REQUEST


def test_the_marks_say_which_argument_is_what():
    assert arguments_of(update) == Arguments(
        identity=("trigger_id",),
        container=("queue_id",),
        version="version",
        body="body",
        left_out=("notify",),
    )
    assert arguments_of(list_) == Arguments(container=("queue_id",))  # a default decides
    assert arguments_of(create) == Arguments(container=("queue_id",), body="body")
    # An object addressed by several arguments has several; a singleton has none.
    assert arguments_of(access_update).identity == ("page", "subject")
    assert arguments_of(settings_get) == Arguments()


def test_an_argument_nobody_names_is_left_out_or_is_undecided():
    """What may be `None` and is not named is not sent; what must have a value is a gap."""
    # A note of another sort beside a type is not a mark: `text` has no decision.
    assert arguments_of(search) == Arguments(left_out=("fields",), undecided=("text",))
    # A kind decides an argument by setting it in its declaration.
    assert arguments_of(partial(search, "words")) == Arguments(left_out=("fields",))
    assert arguments_of(partial(search, "words", fields="content")) == Arguments()


def test_an_operation_has_one_version_and_one_body_at_most():
    def two_versions(a: Annotated[int, Version()], b: Annotated[int, Version()]) -> Endpoint[Any]:
        return REQUEST

    def two_bodies(a: TriggerUpdate, b: TriggerUpdate) -> Endpoint[Any]:
        return REQUEST

    with pytest.raises(TypeError, match="more than one Version"):
        arguments_of(two_versions)
    with pytest.raises(TypeError, match="more than one BaseModel"):
        arguments_of(two_bodies)


def test_a_kind_names_its_operations_and_leaves_out_the_ones_the_api_lacks():
    trigger = Kind(
        name="tracker/trigger",
        layout=YAMLFile(),
        link=Link,
        content=TriggerUpdate,
        find=list_,
        read=get,
        create=create,
        update=update,
        version=SentVersion(),
    )
    assert trigger.delete is None  # the API has no such operation: said by its absence
    # The names are those of the fields that hold an operation; nothing lists them twice.
    assert trigger.operations() == {"read": get, "find": list_, "create": create, "update": update}


def test_a_kind_is_listed_with_what_guards_a_write_of_it():
    declared = Kind(
        name="tracker/trigger",
        layout=YAMLFile(),
        link=Link,
        content=TriggerUpdate,
        read=get,
        update=update,
        version=SentVersion(),
    )
    assert summary_of(declared).model_dump() == {
        "name": "tracker/trigger",
        "file": ".yaml",
        "operations": ["read", "update"],
        "version": "sent with the write: the server refuses a stale one",
        "about": "One file of a repository as the object it stands for: its link and its content.",
    }
    page = Kind(
        name="wiki/page",
        layout=MarkdownWithHeader(),
        link=Link,
        content=TriggerUpdate,
        read=get,
        version=CheckedVersion(newest=list_),
    )
    listed = summary_of(page)
    assert (listed.file, listed.version) == (".md", "read and compared before the write")


def test_every_way_to_prove_a_version_says_what_it_is():
    """One call for any of them: a new way is a new class, and nothing branches on its type."""
    bare = Kind(name="forms/survey", layout=YAMLFile(), link=Link, content=TriggerUpdate, read=get)
    assert bare.version == NoVersion()  # no version in the service: the fingerprint alone
    said = [way.describe() for way in (SentVersion(), CheckedVersion(newest=list_), NoVersion())]
    assert said == [
        "sent with the write: the server refuses a stale one",
        "read and compared before the write",
        "none: the fingerprint of the content alone",
    ]
    assert summary_of(bare).version == said[2]


def test_every_way_to_prove_a_version_says_the_version_of_an_object_now():
    """One call for any of them: the reply, the newest of a listing, or nothing at all."""

    class Revision(Link):
        id: Annotated[int, Version()]

    read = Revision(id=7)
    asked: list[Any] = []

    def ask(operation: Any) -> list[Revision]:
        asked.append(operation)
        return [Revision(id=9), Revision(id=8)]

    assert SentVersion().current(read, "id", ask) == 7
    assert NoVersion().current(read, "id", ask) is None
    assert asked == []  # neither asks the service again
    assert CheckedVersion(newest=list_).current(read, "id", ask) == 9
    assert asked == [list_]
    assert CheckedVersion(newest=list_).current(read, "id", lambda operation: []) is None
