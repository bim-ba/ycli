"""TDD for the queues models — aliases, nested refs, and the flat QueueList."""

from ycli.yandex.tracker.queues.models import (
    IssueTypeConfig,
    Queue,
    QueueList,
    QueueUser,
    QueueVersion,
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
