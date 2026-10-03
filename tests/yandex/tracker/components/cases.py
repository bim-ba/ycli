"""Contract cases for Tracker ``/components`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.components.models import ComponentCreate, ComponentUpdate

CASES = [
    Case(
        "tracker.components.list",
        cli=["tracker", "components", "list"],
        mcp=("tracker_components_list", {}),
        exchanges=[
            (
                Sent("GET", "components"),
                Reply(json=[{"id": 1, "name": "Backend", "queue": {"key": "DEV"}}]),
            )
        ],
    ),
    Case(
        "tracker.components.create",
        args=(
            ComponentCreate(
                name="UI", queue="WEB", description="Frontend", lead="ui-lead", assign_auto=True
            ),
        ),
        cli=[
            "tracker",
            "components",
            "create",
            "--name",
            "UI",
            "--queue",
            "WEB",
            "--description",
            "Frontend",
            "--lead",
            "ui-lead",
            "--assign-auto",
        ],
        mcp=(
            "tracker_components_create",
            {
                "body": {
                    "name": "UI",
                    "queue": "WEB",
                    "description": "Frontend",
                    "lead": "ui-lead",
                    "assign_auto": True,
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "components",
                    json={
                        "name": "UI",
                        "queue": "WEB",
                        "description": "Frontend",
                        "lead": "ui-lead",
                        "assignAuto": True,
                    },
                ),
                Reply(json={"id": 111175, "name": "UI"}, status=201),
            )
        ],
    ),
    # `--no-assign-auto` sends false; empty options are left out.
    Case(
        "tracker.components.create",
        args=(ComponentCreate(name="API", queue="SRV", assign_auto=False),),
        cli=[
            "tracker",
            "components",
            "create",
            "--name",
            "API",
            "--queue",
            "SRV",
            "--no-assign-auto",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "components",
                    json={"name": "API", "queue": "SRV", "assignAuto": False},
                ),
                Reply(json={"id": 111176, "name": "API"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.components.update",
        args=(
            111175,
            ComponentUpdate(
                name="Web UI", description="Renamed", lead="new-lead", assign_auto=False
            ),
        ),
        kwargs={"version": 4},
        cli=[
            "tracker",
            "components",
            "update",
            "111175",
            "--name",
            "Web UI",
            "--description",
            "Renamed",
            "--lead",
            "new-lead",
            "--no-assign-auto",
            "--version",
            "4",
        ],
        mcp=(
            "tracker_components_update",
            {
                "component_id": 111175,
                "body": {
                    "name": "Web UI",
                    "description": "Renamed",
                    "lead": "new-lead",
                    "assign_auto": False,
                },
                "version": 4,
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "components/111175",
                    {"version": "4"},
                    {
                        "name": "Web UI",
                        "description": "Renamed",
                        "lead": "new-lead",
                        "assignAuto": False,
                    },
                ),
                Reply(json={"id": 111175, "version": 5}),
            )
        ],
    ),
    Case(
        "tracker.components.update",
        args=(222, ComponentUpdate(assign_auto=True)),
        cli=["tracker", "components", "update", "222", "--assign-auto"],
        mcp=None,
        exchanges=[
            (
                Sent("PATCH", "components/222", json={"assignAuto": True}),
                Reply(json={"id": 222, "assignAuto": True}),
            )
        ],
    ),
    Case(
        "tracker.components.list_for_queue",
        args=("COMPQ",),
        kwargs={"fields": "version,description"},
        cli=["tracker", "components", "list-for-queue", "COMPQ", "--fields", "version,description"],
        mcp=(
            "tracker_components_list_for_queue",
            {"queue_id": "COMPQ", "fields": "version,description"},
        ),
        exchanges=[
            (
                Sent("GET", "queues/COMPQ/components", {"fields": "version,description"}),
                Reply(
                    json=[
                        {
                            "self": "https://api.tracker.yandex.net/v3/components/123",
                            "id": 123,
                            "name": "Frontend",
                            "queue": {"id": "1", "key": "COMPQ", "display": "Components queue"},
                            "version": 3,
                            "description": "UI work",
                        }
                    ]
                ),
            )
        ],
    ),
    Case(
        "tracker.components.list_for_queue",
        args=("PLAINQ",),
        cli=["tracker", "components", "list-for-queue", "PLAINQ"],
        mcp=None,
        exchanges=[
            (Sent("GET", "queues/PLAINQ/components"), Reply(json=[{"id": 124, "name": "A"}]))
        ],
    ),
    Case(
        "tracker.components.get",
        args=(125,),
        kwargs={"fields": "name,lead,assignAuto"},
        cli=["tracker", "components", "get", "125", "--fields", "name,lead,assignAuto"],
        mcp=("tracker_components_get", {"component_id": 125, "fields": "name,lead,assignAuto"}),
        exchanges=[
            (
                Sent("GET", "components/125", {"fields": "name,lead,assignAuto"}),
                Reply(
                    json={
                        "self": "https://api.tracker.yandex.net/v3/components/125",
                        "id": 125,
                        "version": 1,
                        "name": "Backend",
                        "description": "Services",
                        "queue": {"id": "1", "key": "TEST", "display": "Test queue"},
                        "lead": {"id": "11", "display": "Carol"},
                        "assignAuto": True,
                    }
                ),
            )
        ],
    ),
    Case(
        "tracker.components.get",
        args=(126,),
        cli=["tracker", "components", "get", "126"],
        mcp=None,
        exchanges=[(Sent("GET", "components/126"), Reply(json={"id": 126, "name": "Plain"}))],
    ),
    Case(
        "tracker.components.delete",
        args=(127,),
        cli=["tracker", "components", "delete", "127"],
        mcp=("tracker_components_delete", {"component_id": 127}),
        exchanges=[(Sent("DELETE", "components/127"), Reply(status=204))],
    ),
    Case(
        "tracker.components.user_permissions_get",
        args=(128, "dan"),
        cli=["tracker", "components", "user-permissions-get", "128", "dan"],
        mcp=("tracker_components_user_permissions_get", {"component_id": 128, "user_id": "dan"}),
        exchanges=[
            (
                Sent("GET", "components/128/permissions/users/dan"),
                Reply(
                    json={
                        "user": {"id": "12", "display": "Dan", "passportUid": 1200},
                        "component": {
                            "id": 128,
                            "version": 2,
                            "name": "Component 128",
                            "queue": {"id": "1", "key": "TEST", "display": "Test queue"},
                            "lead": {"id": "11", "display": "Carol"},
                            "assignAuto": False,
                        },
                        "permissions": {
                            "CREATE": {"groups": [{"id": "5", "display": "All users"}]},
                            "DENY": {"users": [{"id": "13", "display": "Eve"}]},
                        },
                    }
                ),
            )
        ],
    ),
    Case(
        "tracker.components.group_permissions_get",
        args=(129, 88),
        cli=["tracker", "components", "group-permissions-get", "129", "88"],
        mcp=("tracker_components_group_permissions_get", {"component_id": 129, "group_id": 88}),
        exchanges=[
            (
                Sent("GET", "components/129/permissions/groups/88"),
                Reply(
                    json={
                        "group": {"id": "88", "display": "Reviewers"},
                        "component": {"id": 129, "name": "Component 129"},
                        "permissions": {"READ": {"groups": [{"id": "88", "display": "Reviewers"}]}},
                    }
                ),
            )
        ],
    ),
]
