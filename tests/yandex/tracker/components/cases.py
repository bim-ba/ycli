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
        "tracker.components.edit",
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
            "edit",
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
            "tracker_components_edit",
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
        "tracker.components.edit",
        args=(222, ComponentUpdate(assign_auto=True)),
        cli=["tracker", "components", "edit", "222", "--assign-auto"],
        mcp=None,
        exchanges=[
            (
                Sent("PATCH", "components/222", json={"assignAuto": True}),
                Reply(json={"id": 222, "assignAuto": True}),
            )
        ],
    ),
]
