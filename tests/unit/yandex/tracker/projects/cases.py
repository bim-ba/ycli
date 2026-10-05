"""Contract cases for Tracker ``/projects`` (legacy Projects API v3; see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.projects.models import ProjectCreate, ProjectUpdate

PROJECT = {
    "self": "https://api.tracker.yandex.net/v3/projects/9",
    "id": "9",
    "version": 1,
    "key": "Project",
    "name": "Project",
    "description": "My project",
    "lead": {"self": "https://api.tracker.yandex.net/v3/users/11", "id": "11", "display": "Ann"},
    "status": "launched",
    "startDate": "2020-11-16",
    "endDate": "2020-12-16",
}

CASES = [
    Case(
        "tracker.projects.list",
        kwargs={"expand": "queues"},
        cli=["tracker", "projects", "list", "--expand", "queues"],
        mcp=("tracker_projects_list", {"expand": "queues"}),
        exchanges=[
            (
                Sent("GET", "projects", {"expand": "queues"}),
                Reply(json=[PROJECT, {**PROJECT, "id": "10", "queues": [{"key": "TEST"}]}]),
            )
        ],
    ),
    Case(
        "tracker.projects.list",
        cli=["tracker", "projects", "list"],
        mcp=None,
        exchanges=[(Sent("GET", "projects"), Reply(json=[{"id": "11", "name": "Plain"}]))],
    ),
    Case(
        "tracker.projects.get",
        args=(21,),
        kwargs={"expand": "queues"},
        cli=["tracker", "projects", "get", "21", "--expand", "queues"],
        mcp=("tracker_projects_get", {"project_id": 21, "expand": "queues"}),
        exchanges=[(Sent("GET", "projects/21", {"expand": "queues"}), Reply(json=PROJECT))],
    ),
    Case(
        "tracker.projects.get",
        args=(22,),
        cli=["tracker", "projects", "get", "22"],
        mcp=None,
        exchanges=[(Sent("GET", "projects/22"), Reply(json={"id": "22", "name": "Plain"}))],
    ),
    Case(
        "tracker.projects.queues_list",
        args=(23,),
        kwargs={"expand": "components,versions"},
        cli=["tracker", "projects", "queues-list", "23", "--expand", "components,versions"],
        mcp=("tracker_projects_queues_list", {"project_id": 23, "expand": "components,versions"}),
        exchanges=[
            (
                Sent("GET", "projects/23/queues", {"expand": "components,versions"}),
                Reply(json=[{"id": 1, "key": "ORG", "name": "Default"}, {"id": 3, "key": "TEST"}]),
            )
        ],
    ),
    Case(
        "tracker.projects.queues_list",
        args=(24,),
        cli=["tracker", "projects", "queues-list", "24"],
        mcp=None,
        exchanges=[(Sent("GET", "projects/24/queues"), Reply(json=[{"key": "ONE"}]))],
    ),
    Case(
        "tracker.projects.create",
        args=(
            ProjectCreate(
                name="Launch",
                queues="LAUNCH",
                description="Mobile app",
                lead="ann",
                status="IN_PROGRESS",
                start_date="2026-11-01",
                end_date="2026-12-01",
            ),
        ),
        cli=[
            "tracker",
            "projects",
            "create",
            "--name",
            "Launch",
            "--queues",
            "LAUNCH",
            "--description",
            "Mobile app",
            "--lead",
            "ann",
            "--status",
            "IN_PROGRESS",
            "--start-date",
            "2026-11-01",
            "--end-date",
            "2026-12-01",
        ],
        mcp=(
            "tracker_projects_create",
            {
                "body": {
                    "name": "Launch",
                    "queues": "LAUNCH",
                    "description": "Mobile app",
                    "lead": "ann",
                    "status": "IN_PROGRESS",
                    "start_date": "2026-11-01",
                    "end_date": "2026-12-01",
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "projects",
                    json={
                        "name": "Launch",
                        "queues": "LAUNCH",
                        "description": "Mobile app",
                        "lead": "ann",
                        "status": "IN_PROGRESS",
                        "startDate": "2026-11-01",
                        "endDate": "2026-12-01",
                    },
                ),
                Reply(json={**PROJECT, "name": "Launch"}, status=201),
            )
        ],
    ),
    # Only the required parts are sent.
    Case(
        "tracker.projects.create",
        args=(ProjectCreate(name="Bare", queues="BARE"),),
        cli=["tracker", "projects", "create", "--name", "Bare", "--queues", "BARE"],
        mcp=None,
        exchanges=[
            (
                Sent("POST", "projects", json={"name": "Bare", "queues": "BARE"}),
                Reply(json={"id": "30", "name": "Bare"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.projects.update",
        args=(
            31,
            ProjectUpdate(
                queues="EDITQ",
                name="Renamed",
                description="Changed",
                lead="bob",
                status="POSTPONED",
                start_date="2027-01-01",
                end_date="2027-02-01",
            ),
        ),
        kwargs={"version": 5, "expand": "queues"},
        cli=[
            "tracker",
            "projects",
            "update",
            "31",
            "--version",
            "5",
            "--queues",
            "EDITQ",
            "--name",
            "Renamed",
            "--description",
            "Changed",
            "--lead",
            "bob",
            "--status",
            "POSTPONED",
            "--start-date",
            "2027-01-01",
            "--end-date",
            "2027-02-01",
            "--expand",
            "queues",
        ],
        mcp=(
            "tracker_projects_update",
            {
                "project_id": 31,
                "version": 5,
                "expand": "queues",
                "body": {
                    "queues": "EDITQ",
                    "name": "Renamed",
                    "description": "Changed",
                    "lead": "bob",
                    "status": "POSTPONED",
                    "start_date": "2027-01-01",
                    "end_date": "2027-02-01",
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "PUT",
                    "projects/31",
                    {"version": "5", "expand": "queues"},
                    {
                        "queues": "EDITQ",
                        "name": "Renamed",
                        "description": "Changed",
                        "lead": "bob",
                        "status": "POSTPONED",
                        "startDate": "2027-01-01",
                        "endDate": "2027-02-01",
                    },
                ),
                Reply(json={**PROJECT, "id": "31", "version": 6}),
            )
        ],
    ),
    # Only the required queues and the lock go out.
    Case(
        "tracker.projects.update",
        args=(32, ProjectUpdate(queues="ONLYQ")),
        kwargs={"version": 2},
        cli=["tracker", "projects", "update", "32", "--version", "2", "--queues", "ONLYQ"],
        mcp=None,
        exchanges=[
            (
                Sent("PUT", "projects/32", {"version": "2"}, {"queues": "ONLYQ"}),
                Reply(json={"id": "32", "version": 3}),
            )
        ],
    ),
    Case(
        "tracker.projects.delete",
        args=(33,),
        cli=["tracker", "projects", "delete", "33"],
        mcp=("tracker_projects_delete", {"project_id": 33}),
        exchanges=[(Sent("DELETE", "projects/33"), Reply(status=204))],
    ),
]
