"""Contract cases for Tracker ``/boards`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.boards.models import BoardColumnInput, BoardCreate, BoardUpdate

CASES = [
    # The default cap (500) asks for full 100-row pages and walks id=<last board id> until an
    # empty page.
    Case(
        "tracker.boards.list",
        kwargs={"limit": 500},
        cli=["tracker", "boards", "list"],
        mcp=("tracker_boards_list", {}),
        exchanges=[
            (
                Sent("GET", "boards/_paginate", {"perPage": "100"}),
                Reply(json=[{"id": 11, "name": "Alpha"}, {"id": 12, "name": "Beta"}]),
            ),
            (
                Sent("GET", "boards/_paginate", {"perPage": "100", "id": "12"}),
                Reply(json=[{"id": 13, "name": "Gamma"}]),
            ),
            (Sent("GET", "boards/_paginate", {"perPage": "100", "id": "13"}), Reply(json=[])),
        ],
    ),
    # A small cap narrows the page to the cap and needs no second page.
    Case(
        "tracker.boards.list",
        kwargs={"limit": 2},
        cli=["tracker", "boards", "list", "--limit", "2"],
        mcp=("tracker_boards_list", {"limit": 2}),
        exchanges=[
            (
                Sent("GET", "boards/_paginate", {"perPage": "2"}),
                Reply(json=[{"id": 21, "name": "Delta"}, {"id": 22, "name": "Epsilon"}]),
            )
        ],
    ),
    # `--all` is uncapped; a last board without an id ends the walk.
    Case(
        "tracker.boards.list",
        kwargs={"limit": None},
        cli=["tracker", "boards", "list", "--all"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "boards/_paginate", {"perPage": "100"}),
                Reply(json=[{"id": None, "name": "Orphan"}]),
            )
        ],
    ),
    Case(
        "tracker.boards.get",
        args=(31,),
        cli=["tracker", "boards", "get", "31"],
        mcp=("tracker_boards_get", {"board_id": 31}),
        exchanges=[
            (
                Sent("GET", "boards/31"),
                Reply(json={"id": 31, "name": "Kanban", "estimateBy": {"display": "Story Points"}}),
            )
        ],
    ),
    Case(
        "tracker.boards.create",
        args=(
            BoardCreate(
                name="Release train",
                owner="alice",
                board_permissions_template="private",
                backlog_available=True,
                sprints_available=False,
            ),
        ),
        cli=[
            "tracker",
            "boards",
            "create",
            "--name",
            "Release train",
            "--owner",
            "alice",
            "--permissions",
            "private",
            "--backlog",
            "--no-sprints",
        ],
        mcp=(
            "tracker_boards_create",
            {
                "body": {
                    "name": "Release train",
                    "owner": "alice",
                    "board_permissions_template": "private",
                    "backlog_available": True,
                    "sprints_available": False,
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "liveBoards/",
                    json={
                        "name": "Release train",
                        "owner": "alice",
                        "boardPermissionsTemplate": "private",
                        "backlogAvailable": True,
                        "sprintsAvailable": False,
                    },
                ),
                Reply(json={"id": 41, "name": "Release train"}, status=201),
            )
        ],
    ),
    # Columns are an MCP/SDK-only field of the body.
    Case(
        "tracker.boards.create",
        args=(
            BoardCreate(
                name="Columned",
                columns=[BoardColumnInput(name="To do", statuses=["open", "new"], limit=7)],
            ),
        ),
        cli=None,
        mcp=(
            "tracker_boards_create",
            {
                "body": {
                    "name": "Columned",
                    "columns": [{"name": "To do", "statuses": ["open", "new"], "limit": 7}],
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "liveBoards/",
                    json={
                        "name": "Columned",
                        "columns": [{"name": "To do", "statuses": ["open", "new"], "limit": 7}],
                    },
                ),
                Reply(json={"id": 42, "name": "Columned"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.boards.edit",
        args=(
            51,
            BoardUpdate(name="Renamed board", backlog_available=False, sprints_available=True),
        ),
        cli=[
            "tracker",
            "boards",
            "edit",
            "51",
            "--name",
            "Renamed board",
            "--no-backlog",
            "--sprints",
        ],
        mcp=(
            "tracker_boards_edit",
            {
                "board_id": 51,
                "body": {
                    "name": "Renamed board",
                    "backlog_available": False,
                    "sprints_available": True,
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "boards/51",
                    json={
                        "name": "Renamed board",
                        "backlogAvailable": False,
                        "sprintsAvailable": True,
                    },
                ),
                Reply(json={"id": 51, "name": "Renamed board"}),
            )
        ],
    ),
    Case(
        "tracker.boards.edit",
        args=(52, BoardUpdate(columns=[BoardColumnInput(name="Done", statuses=["closed"])])),
        cli=None,
        mcp=(
            "tracker_boards_edit",
            {"board_id": 52, "body": {"columns": [{"name": "Done", "statuses": ["closed"]}]}},
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "boards/52",
                    json={"columns": [{"name": "Done", "statuses": ["closed"]}]},
                ),
                Reply(json={"id": 52, "name": "Board"}),
            )
        ],
    ),
    Case(
        "tracker.boards.delete",
        args=(61,),
        cli=["tracker", "boards", "delete", "61"],
        mcp=("tracker_boards_delete", {"board_id": 61}),
        exchanges=[(Sent("DELETE", "boards/61"), Reply(status=204))],
    ),
]
