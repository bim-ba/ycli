"""Model parsing for Tracker workflows: the doc reply and the request bodies."""

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.models import LocalizedName
from ycli.yandex.tracker.workflows.models import (
    QueueWorkflows,
    Workflow,
    WorkflowActionInput,
    WorkflowCreate,
    WorkflowStepInput,
)

SAMPLE = {
    "self": "https://api.tracker.yandex.net/v3/workflows/W21",
    "id": "W21",
    "name": "Design",
    "version": 1,
    "steps": [
        {
            "status": {"id": "1", "key": "open", "display": "Open"},
            "actions": [
                {
                    "id": "inProgress",
                    "name": "Start progress",
                    "target": {"id": "3", "key": "inProgress", "display": "In progress"},
                }
            ],
        },
        {"status": {"id": "8", "key": "closed", "display": "Closed"}},
    ],
    "initialAction": {"id": "open", "name": "Open", "target": {"id": "1", "key": "open"}},
    "queue": {"id": "4", "key": "DESIGN", "display": "DESIGN"},
    "created": "2026-08-11T14:37:06.356+0000",
    "updated": "2026-08-11T14:37:06.356+0000",
    "createdBy": {"id": "11", "display": "Ann", "cloudUid": "ajeppa7dgp53", "passportUid": 1100},
    "deleted": False,
    "type": "visual",
}


def test_workflow_parses_the_doc_sample():
    workflow = Workflow.model_validate(SAMPLE)
    assert (workflow.id, workflow.version, workflow.type) == ("W21", 1, "visual")
    assert workflow.steps[0].actions[0].target is not None
    assert workflow.steps[0].actions[0].target.key == "inProgress"
    assert workflow.steps[1].actions == []  # the last step has no actions
    assert workflow.initial_action is not None and workflow.initial_action.id == "open"
    assert workflow.queue is not None and workflow.queue.key == "DESIGN"
    assert workflow.created_by is not None and workflow.created_by.passport_uid == 1100
    assert workflow.updated_by is None  # unfilled optional fields are absent from the reply


def test_workflow_without_queue_or_type_parses():
    workflow = Workflow.model_validate({"id": "W1", "name": "Shared", "version": 2})
    assert workflow.queue is None and workflow.type is None and workflow.steps == []


def test_workflow_list_is_a_flat_array():
    assert [w.id for w in ItemList[Workflow].model_validate([{"id": "A"}, {"id": "B"}]).root] == [
        "A",
        "B",
    ]


def test_queue_workflows_maps_workflow_ids_to_issue_types():
    mapping = QueueWorkflows.model_validate({"dev": [{"id": "1", "key": "task"}], "ops": []})
    assert mapping.root["dev"][0].key == "task" and mapping.root["ops"] == []


def test_request_bodies_use_the_api_names_and_drop_unset_fields():
    body = WorkflowCreate(
        name="Design",
        initial_action=WorkflowActionInput(
            name=LocalizedName(ru="Открыть", en="Open"), target="open"
        ),
        steps=[WorkflowStepInput(status="open", status_type="NEW")],
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {
        "name": "Design",
        "initialAction": {"name": {"ru": "Открыть", "en": "Open"}, "target": "open"},
        "steps": [{"status": "open", "statusType": "NEW"}],
    }


def test_request_bodies_accept_the_docs_json_as_is():
    step = WorkflowStepInput.model_validate(
        {"status": {"key": "open"}, "metaAction": {"name": {}, "target": 1}}
    )
    assert step.meta_action is not None and step.meta_action.target == 1


def test_every_request_field_has_a_description():
    from ycli.yandex.tracker.workflows import models

    for name in (
        "RefSelector",
        "LocalizedName",
        "WorkflowActionInput",
        "WorkflowActionUpdate",
        "WorkflowStepInput",
        "IssueTypeResolutions",
        "WorkflowCreate",
        "WorkflowUpdate",
        "Workflow",
    ):
        for field_name, field in getattr(models, name).model_fields.items():
            assert field.description, f"{name}.{field_name} is missing Field(description=…)"


def test_an_action_name_in_english_only_is_refused_before_sending():
    """Tracker answers 422 "action.name" for a name without its Russian text."""
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="Russian text"):
        WorkflowActionInput.model_validate({"name": {"en": "Close"}, "target": "closed"})
