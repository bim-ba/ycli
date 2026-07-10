"""TDD for Tracker remote-link models — full doc sample parse + typed create body."""

from ycli.yandex.tracker.remotelinks.models import (
    RemoteLink,
    RemoteLinkCreate,
    RemoteLinkList,
)

SAMPLE = {
    "self": "https://api.tracker.yandex.net/v3/issues/JUNE-2/remotelinks/51",
    "id": 51,
    "type": {
        "self": "…/linktypes/relates",
        "id": "relates",
        "inward": "Связана",
        "outward": "Связана",
    },
    "direction": "outward",
    "object": {
        "self": "…/applications/ru.yandex.bitbucket/objects/13570010",
        "id": "13570010",
        "key": "TEST-17",
        "application": {
            "self": "…/applications/25811000",
            "id": "25811000",
            "type": "app",
            "name": "test-app",
        },
    },
    "createdBy": {"id": "11", "display": "Full Name"},
    "updatedBy": {"id": "11", "display": "Full Name"},
    "createdAt": "2021-07-14T18:59:54.552+0000",
    "updatedAt": "2021-07-14T18:59:54.552+0000",
}


def test_remote_link_parses_all_fields():
    link = RemoteLink.model_validate(SAMPLE)
    assert link.id == 51
    assert link.type is not None and link.type.id == "relates"
    assert link.direction == "outward"
    assert link.object is not None
    assert link.object.key == "TEST-17"
    assert link.object.application is not None
    assert link.object.application.name == "test-app"
    assert link.object_key == "TEST-17"
    assert link.created_by == "Full Name"  # createdBy flattened to display
    assert link.self_url.endswith("/remotelinks/51")  # ty: ignore[unresolved-attribute]


def test_object_key_is_none_without_object():
    assert RemoteLink.model_validate({"id": 1}).object_key is None


def test_remote_link_list_parses_array():
    out = RemoteLinkList.model_validate([SAMPLE, {"direction": "inward"}])
    assert isinstance(out, RemoteLinkList)
    assert [link.direction for link in out.root] == ["outward", "inward"]


def test_create_body_defaults_relationship():
    body = RemoteLinkCreate(key="TEST-17", origin="ru.yandex.bitbucket").model_dump(
        exclude_none=True
    )
    assert body == {"relationship": "RELATES", "key": "TEST-17", "origin": "ru.yandex.bitbucket"}
