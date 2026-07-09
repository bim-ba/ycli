"""TDD for the queues models — aliases, nested refs, and the flat QueueList."""

from ycli.yandex.tracker.queues.models import (
    IssueTypeConfig,
    IssueTypeConfigInput,
    Queue,
    QueueCreate,
    QueueField,
    QueueFieldList,
    QueueList,
    QueuePermissionScope,
    QueuePermissionSubjects,
    QueuePermissionsUpdate,
    QueueTagList,
    QueueTagRemove,
    QueueUser,
    QueueVersion,
    QueueVersionCreate,
    QueueVersionInfo,
    QueueVersionInfoList,
)


def test_queue_parses_full_payload_with_camelcase_aliases():
    q = Queue.model_validate(
        {
            "self": "https://api.tracker.yandex.net/v3/queues/TEST",
            "id": "3",
            "key": "TEST",
            "version": 5,
            "name": "Test",
            "description": "My queue",
            "lead": {"id": "11", "display": "Ivan", "passportUid": 11, "cloudUid": "abc"},
            "assignAuto": True,
            "defaultType": {"key": "task", "display": "Task"},
            "defaultPriority": {"key": "normal", "display": "Normal"},
            "teamUsers": [{"id": "11", "display": "Ivan"}],
            "issueTypes": [{"key": "task"}, {"key": "bug"}],
            "versions": [{"id": "4", "display": "My version"}],
            "workflows": {"dev": [{"key": "task"}]},
            "denyVoting": False,
            "issueTypesConfig": [
                {
                    "issueType": {"key": "task"},
                    "workflow": {"id": "dev", "display": "dev"},
                    "resolutions": [{"key": "wontFix", "display": "Won't fix"}],
                }
            ],
        }
    )
    assert q.self_url.endswith("/queues/TEST")  # ty: ignore[unresolved-attribute]
    assert q.assign_auto is True and q.deny_voting is False
    assert q.default_type is not None and q.default_priority is not None
    assert q.default_type.key == "task" and q.default_priority.key == "normal"
    assert q.lead is not None
    assert q.lead.passport_uid == 11 and q.lead.cloud_uid == "abc"
    assert [u.display for u in q.team_users] == ["Ivan"]
    assert [t.key for t in q.issue_types] == ["task", "bug"]
    assert q.versions[0].display == "My version"
    assert q.workflows["dev"][0].key == "task"
    cfg = q.issue_types_config[0]
    assert cfg.issue_type.key == "task"  # ty: ignore[unresolved-attribute]
    assert cfg.workflow.id == "dev"  # ty: ignore[unresolved-attribute]
    assert cfg.resolutions[0].key == "wontFix"


def test_queue_defaults_are_empty_not_none():
    q = Queue.model_validate({"key": "TEST"})
    assert q.team_users == [] and q.issue_types == [] and q.versions == []
    assert q.workflows == {} and q.issue_types_config == []
    assert q.lead is None and q.default_type is None


def test_queue_serializes_by_alias_roundtrip():
    q = Queue.model_validate({"key": "TEST", "assignAuto": True, "denyVoting": True})
    dumped = q.model_dump(by_alias=True)
    assert dumped["assignAuto"] is True and dumped["denyVoting"] is True
    assert "assign_auto" not in dumped


def test_nested_models_standalone():
    assert QueueUser.model_validate({"display": "Ivan"}).display == "Ivan"
    assert QueueVersion.model_validate({"id": "4", "display": "v4"}).display == "v4"
    cfg = IssueTypeConfig.model_validate({"issueType": {"key": "bug"}})
    assert cfg.issue_type.key == "bug" and cfg.resolutions == []  # ty: ignore[unresolved-attribute]


def test_queue_list_root_model():
    ql = QueueList.model_validate([{"key": "TEST"}, {"key": "DEMO"}])
    assert [q.key for q in ql.root] == ["TEST", "DEMO"]
    assert QueueList([Queue.model_validate({"key": "X"})]).root[0].key == "X"


def test_tag_list_root_model():
    tags = QueueTagList.model_validate(["a", "b"])
    assert tags.root == ["a", "b"]


def test_version_info_parses_full_payload():
    v = QueueVersionInfo.model_validate(
        {
            "self": "https://api.tracker.yandex.net/v3/versions/1",
            "id": 1,
            "version": 1,
            "queue": {"key": "TEST", "display": "Test"},
            "name": "v0.1",
            "description": "first",
            "startDate": "2023-10-03",
            "dueDate": "2024-06-03",
            "released": False,
            "archived": False,
        }
    )
    assert v.name == "v0.1" and v.start_date == "2023-10-03" and v.due_date == "2024-06-03"
    assert v.queue.key == "TEST" and v.released is False  # ty: ignore[unresolved-attribute]
    assert QueueVersionInfoList.model_validate([{"id": 1}]).root[0].id == 1


def test_queue_field_aliases_schema():
    f = QueueField.model_validate(
        {"id": "myfield", "name": "My field", "schema": {"type": "string"}, "order": 5}
    )
    assert f.field_schema == {"type": "string"} and f.order == 5
    assert QueueFieldList.model_validate([{"id": "x"}]).root[0].id == "x"


def test_queue_create_serializes_aliases():
    body = QueueCreate(
        key="DESIGN",
        name="Design",
        lead="u",
        default_type="task",
        default_priority="normal",
        issue_types_config=[IssueTypeConfigInput(issue_type="task", workflow="oicn")],  # ty: ignore[missing-argument, unknown-argument]
    ).model_dump(by_alias=True, exclude_none=True)
    assert body["defaultType"] == "task" and body["defaultPriority"] == "normal"
    assert body["issueTypesConfig"] == [{"issueType": "task", "workflow": "oicn"}]


def test_tag_remove_and_version_create_bodies():
    assert QueueTagRemove(tag="x").model_dump(by_alias=True, exclude_none=True) == {"tag": "x"}
    vc = QueueVersionCreate(queue="TEST", name="v1", start_date="2023-10-03").model_dump(
        by_alias=True, exclude_none=True
    )
    assert vc == {"queue": "TEST", "name": "v1", "startDate": "2023-10-03"}


def test_permissions_update_accepts_array_and_add_remove():
    subjects = QueuePermissionSubjects(add=["author"], remove=[12345])
    body = QueuePermissionsUpdate(
        create=QueuePermissionScope(users=["user1"]),
        grant=QueuePermissionScope(users=subjects),
    ).model_dump(by_alias=True, exclude_none=True)
    assert body["create"] == {"users": ["user1"]}
    assert body["grant"] == {"users": {"add": ["author"], "remove": [12345]}}
