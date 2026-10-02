"""Contract cases for Tracker ``/workflows`` (see tests/contract.py)."""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.workflows.models import (
    IssueTypeResolutions,
    LocalizedText,
    RefSelector,
    WorkflowActionInput,
    WorkflowActionUpdate,
    WorkflowCreate,
    WorkflowStepInput,
    WorkflowUpdate,
)

OPEN = {"self": "https://api.tracker.yandex.net/v3/statuses/1", "id": "1", "key": "open"}
CLOSED = {"self": "https://api.tracker.yandex.net/v3/statuses/8", "id": "8", "key": "closed"}
WORKFLOW = {
    "self": "https://api.tracker.yandex.net/v3/workflows/W21",
    "id": "W21",
    "name": "Design",
    "version": 1,
    "steps": [
        {
            "status": {**OPEN, "display": "Open"},
            "actions": [
                {"id": "close", "name": "Close", "target": {**CLOSED, "display": "Closed"}}
            ],
        },
        {"status": CLOSED},
    ],
    "initialAction": {"id": "open", "name": "Open", "target": OPEN},
    "queue": {
        "self": "https://api.tracker.yandex.net/v3/queues/DESIGN",
        "id": "4",
        "key": "DESIGN",
    },
    "created": "2026-08-11T14:37:06.356+0000",
    "updated": "2026-08-11T14:37:06.356+0000",
    "createdBy": {"id": "11", "display": "Ann", "cloudUid": "ajeppa7dgp53", "passportUid": 1100},
    "updatedBy": {"id": "12", "display": "Bob"},
    "deleted": False,
    "type": "visual",
}

# The initial action and steps of the create cases, as the CLI gets them and as the API wants them.
INITIAL = {"id": "open", "name": {"ru": "Открыть", "en": "Open"}, "target": "open"}
STEP_OPEN = {
    "status": "open",
    "description": {"en": "Issue is open"},
    "actions": [
        {
            "id": "start",
            "name": {"ru": "Начать", "en": "Start"},
            "description": {"ru": "Взять в работу"},
            "target": 3,
            "screen": {"fields": ["assignee"]},
            "conditions": [{"type": "Role", "role": "assignee"}],
            "functions": [{"type": "SetResolution"}],
        }
    ],
    "metaAction": {"name": {"ru": "Авто", "en": "Auto"}, "target": {"key": "inProgress"}},
    "statusType": "NEW",
}
STEP_CLOSED = {"status": {"key": "closed"}, "actions": []}
RESOLUTIONS = {"issueType": "task", "resolutions": ["fixed", 2]}

CASES = [
    Case(
        "tracker.workflows.list",
        cli=["tracker", "workflows", "list"],
        mcp=("tracker_workflows_list", {}),
        exchanges=[
            (Sent("GET", "workflows"), Reply(json=[WORKFLOW, {"id": "W22", "name": "Bare"}]))
        ],
    ),
    Case(
        "tracker.workflows.get",
        args=("W21",),
        cli=["tracker", "workflows", "get", "W21"],
        mcp=("tracker_workflows_get", {"workflow_id": "W21"}),
        exchanges=[(Sent("GET", "workflows/W21"), Reply(json=WORKFLOW))],
    ),
    Case(
        "tracker.workflows.for_queue",
        args=("WFQ",),
        cli=["tracker", "workflows", "for-queue", "WFQ"],
        mcp=("tracker_workflows_for_queue", {"queue_id": "WFQ"}),
        exchanges=[
            (
                Sent("GET", "queues/WFQ/workflows"),
                Reply(
                    json={
                        "dev": [{"self": "https://x.test/issuetypes/1", "id": "1", "key": "task"}],
                        "ops": [{"id": "2", "key": "bug", "display": "Bug"}],
                    }
                ),
            )
        ],
    ),
    Case(
        "tracker.workflows.create",
        args=(
            WorkflowCreate(
                id="design-flow",
                name="Design",
                queue="DESIGN",
                type="VISUAL",
                initial_action=WorkflowActionInput(
                    id="open", name=LocalizedText(ru="Открыть", en="Open"), target="open"
                ),
                steps=[
                    WorkflowStepInput(
                        status="open",
                        description=LocalizedText(en="Issue is open"),
                        actions=[
                            WorkflowActionInput(
                                id="start",
                                name=LocalizedText(ru="Начать", en="Start"),
                                description=LocalizedText(ru="Взять в работу"),
                                target=3,
                                screen={"fields": ["assignee"]},
                                conditions=[{"type": "Role", "role": "assignee"}],
                                functions=[{"type": "SetResolution"}],
                            )
                        ],
                        meta_action=WorkflowActionInput(
                            name=LocalizedText(ru="Авто", en="Auto"),
                            target=RefSelector(key="inProgress"),
                        ),
                        status_type="NEW",
                    ),
                    WorkflowStepInput(status=RefSelector(key="closed"), actions=[]),
                ],
                issue_type_resolutions=[
                    IssueTypeResolutions(issue_type="task", resolutions=["fixed", 2])
                ],
            ),
        ),
        cli=[
            "tracker",
            "workflows",
            "create",
            "--name",
            "Design",
            "--initial-action",
            json.dumps(INITIAL),
            "--step",
            json.dumps(STEP_OPEN),
            "--step",
            json.dumps(STEP_CLOSED),
            "--id",
            "design-flow",
            "--queue",
            "DESIGN",
            "--visual",
            "--issue-type-resolution",
            json.dumps(RESOLUTIONS),
        ],
        mcp=(
            "tracker_workflows_create",
            {
                "body": {
                    "id": "design-flow",
                    "name": "Design",
                    "queue": "DESIGN",
                    "type": "VISUAL",
                    "initialAction": INITIAL,
                    "steps": [STEP_OPEN, STEP_CLOSED],
                    "issueTypeResolutions": [RESOLUTIONS],
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "workflows",
                    json={
                        "id": "design-flow",
                        "name": "Design",
                        "queue": "DESIGN",
                        "type": "VISUAL",
                        "initialAction": INITIAL,
                        "steps": [STEP_OPEN, STEP_CLOSED],
                        "issueTypeResolutions": [RESOLUTIONS],
                    },
                ),
                Reply(json={**WORKFLOW, "id": "design-flow"}, status=201),
            )
        ],
    ),
    # Only the required parts: no id, queue, type or resolutions are sent.
    Case(
        "tracker.workflows.create",
        args=(
            WorkflowCreate(
                name="Bare",
                initial_action=WorkflowActionInput(
                    name=LocalizedText(ru="Создать", en="Create"), target="new"
                ),
                steps=[WorkflowStepInput(status="new")],
            ),
        ),
        cli=[
            "tracker",
            "workflows",
            "create",
            "--name",
            "Bare",
            "--initial-action",
            '{"name": {"ru": "Создать", "en": "Create"}, "target": "new"}',
            "--step",
            '{"status": "new"}',
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "workflows",
                    json={
                        "name": "Bare",
                        "initialAction": {
                            "name": {"ru": "Создать", "en": "Create"},
                            "target": "new",
                        },
                        "steps": [{"status": "new"}],
                    },
                ),
                Reply(json={"id": "W30", "name": "Bare", "version": 1}, status=201),
            )
        ],
    ),
    Case(
        "tracker.workflows.edit",
        args=(
            "W21",
            WorkflowUpdate(
                name="QA process",
                type="VISUAL",
                initial_action=WorkflowActionInput(
                    id="new", name=LocalizedText(ru="Создать", en="Create"), target="new"
                ),
                steps=[WorkflowStepInput(status="new", status_type="NEW")],
                issue_type_resolutions=[
                    IssueTypeResolutions(issue_type="task", resolutions=["fixed", 2])
                ],
            ),
        ),
        kwargs={"version": 3},
        cli=[
            "tracker",
            "workflows",
            "update",
            "W21",
            "--version",
            "3",
            "--name",
            "QA process",
            "--initial-action",
            '{"id": "new", "name": {"ru": "Создать", "en": "Create"}, "target": "new"}',
            "--step",
            '{"status": "new", "statusType": "NEW"}',
            "--visual",
            "--issue-type-resolution",
            json.dumps(RESOLUTIONS),
        ],
        mcp=(
            "tracker_workflows_update",
            {
                "workflow_id": "W21",
                "version": 3,
                "body": {
                    "name": "QA process",
                    "type": "VISUAL",
                    "initialAction": {
                        "id": "new",
                        "name": {"ru": "Создать", "en": "Create"},
                        "target": "new",
                    },
                    "steps": [{"status": "new", "statusType": "NEW"}],
                    "issueTypeResolutions": [RESOLUTIONS],
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "workflows/W21",
                    {"version": "3"},
                    {
                        "name": "QA process",
                        "type": "VISUAL",
                        "initialAction": {
                            "id": "new",
                            "name": {"ru": "Создать", "en": "Create"},
                            "target": "new",
                        },
                        "steps": [{"status": "new", "statusType": "NEW"}],
                        "issueTypeResolutions": [RESOLUTIONS],
                    },
                ),
                Reply(json={**WORKFLOW, "name": "QA process", "version": 4}),
            )
        ],
    ),
    # Only the supplied fields are sent.
    Case(
        "tracker.workflows.edit",
        args=("W22", WorkflowUpdate(name="Renamed")),
        kwargs={"version": 7},
        cli=["tracker", "workflows", "update", "W22", "--version", "7", "--name", "Renamed"],
        mcp=None,
        exchanges=[
            (
                Sent("PATCH", "workflows/W22", {"version": "7"}, {"name": "Renamed"}),
                Reply(json={"id": "W22", "name": "Renamed", "version": 8}),
            )
        ],
    ),
    Case(
        "tracker.workflows.edit_action",
        args=(
            "W23",
            "inProgress",
            "close",
            WorkflowActionUpdate(
                id="finish",
                name=LocalizedText(ru="Завершить", en="Complete"),
                description=LocalizedText(en="Move issue to Closed"),
                target=RefSelector(id=8),
                screen={"fields": ["resolution"]},
                conditions=[{"type": "Role", "role": "author"}],
                functions=[{"type": "SetResolution"}],
            ),
        ),
        kwargs={"version": 2},
        cli=[
            "tracker",
            "workflows",
            "update-action",
            "W23",
            "inProgress",
            "close",
            "--version",
            "2",
            "--action",
            json.dumps(
                {
                    "id": "finish",
                    "name": {"ru": "Завершить", "en": "Complete"},
                    "description": {"en": "Move issue to Closed"},
                    "target": {"id": 8},
                    "screen": {"fields": ["resolution"]},
                    "conditions": [{"type": "Role", "role": "author"}],
                    "functions": [{"type": "SetResolution"}],
                }
            ),
        ],
        mcp=(
            "tracker_workflows_update_action",
            {
                "workflow_id": "W23",
                "status": "inProgress",
                "action_id": "close",
                "version": 2,
                "body": {
                    "id": "finish",
                    "name": {"ru": "Завершить", "en": "Complete"},
                    "description": {"en": "Move issue to Closed"},
                    "target": {"id": 8},
                    "screen": {"fields": ["resolution"]},
                    "conditions": [{"type": "Role", "role": "author"}],
                    "functions": [{"type": "SetResolution"}],
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "workflows/W23/steps/inProgress/actions/close",
                    {"version": "2"},
                    {
                        "id": "finish",
                        "name": {"ru": "Завершить", "en": "Complete"},
                        "description": {"en": "Move issue to Closed"},
                        "target": {"id": 8},
                        "screen": {"fields": ["resolution"]},
                        "conditions": [{"type": "Role", "role": "author"}],
                        "functions": [{"type": "SetResolution"}],
                    },
                ),
                Reply(json={**WORKFLOW, "id": "W23", "version": 3}),
            )
        ],
    ),
    Case(
        "tracker.workflows.delete",
        args=("W24",),
        cli=["tracker", "workflows", "delete", "W24"],
        mcp=("tracker_workflows_delete", {"workflow_id": "W24"}),
        exchanges=[(Sent("DELETE", "workflows/W24"), Reply(status=204))],
    ),
]
