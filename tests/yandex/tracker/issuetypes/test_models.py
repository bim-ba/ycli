"""Model-parse + Field-metadata coverage for the Tracker issuetypes write-body models."""

from ycli.yandex.tracker.issuetypes.models import (
    IssueType,
    IssueTypeCreate,
    IssueTypeList,
    IssueTypeUpdate,
    LocalizedName,
)


def test_issuetype_and_list_parse():
    # The live v3 API carries the display name in `name` (`display` stays null).
    it = IssueType.model_validate({"key": "task", "name": "Task"})
    assert it.key == "task" and it.name == "Task" and it.display is None
    lst = IssueTypeList.model_validate([{"key": "bug", "name": "Bug"}, {"key": "task"}])
    assert [x.key for x in lst.root] == ["bug", "task"]
    assert lst.root[0].name == "Bug"


def test_issuetype_create_body_serializes_localized_name():
    body = IssueTypeCreate(key="client", name=LocalizedName(ru="Клиент", en="Customer")).model_dump(
        by_alias=True, exclude_none=True
    )
    assert body == {"key": "client", "name": {"ru": "Клиент", "en": "Customer"}}


def test_issuetype_update_omits_unset_name():
    body = IssueTypeUpdate().model_dump(by_alias=True, exclude_none=True)
    assert body == {}


def test_every_write_body_field_has_description():
    for model in (LocalizedName, IssueTypeCreate, IssueTypeUpdate):
        for name, field in model.model_fields.items():
            assert field.description, f"{model.__name__}.{name} is missing Field(description=…)"
