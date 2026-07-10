"""TDD for the macros models — refs, the issueUpdate asymmetry, and write bodies."""

from ycli.yandex.tracker.macros.models import (
    Macro,
    MacroCreate,
    MacroList,
    MacroUpdate,
)


def test_macro_parses_full_payload():
    m = Macro.model_validate(
        {
            "self": "https://api.tracker.yandex.net/v3/queues/TEST/macros/3",
            "id": 3,
            "queue": {"id": "1", "key": "TEST", "display": "My queue"},
            "name": "My macro",
            "body": "Hi {{issue.author}}",
            "issueUpdate": [
                {"field": {"id": "tags", "display": "Tags"}, "update": {"add": ["tag 1"]}}
            ],
        }
    )
    assert m.id == 3 and m.name == "My macro" and m.queue.key == "TEST"  # ty: ignore[unresolved-attribute]
    assert m.issue_update[0].field.id == "tags"  # ty: ignore[unresolved-attribute]
    assert m.issue_update[0].update == {"add": ["tag 1"]}


def test_macro_defaults_issue_update_empty():
    m = Macro.model_validate({"id": 3, "name": "x"})
    assert m.issue_update == []


def test_macro_list_root_model():
    ml = MacroList.model_validate([{"id": 3, "name": "a"}, {"id": 4, "name": "b"}])
    assert [m.name for m in ml.root] == ["a", "b"]


def test_macro_create_body_serializes_issue_update_alias():
    body = MacroCreate(
        name="Test macro",
        body="Hi",
        issue_update={"tags": {"add": "Новый тег"}, "resolution": None},
    ).model_dump(by_alias=True, exclude_none=True)
    assert body["name"] == "Test macro" and body["body"] == "Hi"
    assert body["issueUpdate"] == {"tags": {"add": "Новый тег"}, "resolution": None}


def test_macro_update_only_supplied_fields():
    assert MacroUpdate(name="Renamed").model_dump(by_alias=True, exclude_none=True) == {
        "name": "Renamed"
    }
