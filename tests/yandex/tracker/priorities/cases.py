"""Contract cases for Tracker ``/priorities`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.models import LocalizedName
from ycli.yandex.tracker.priorities.models import PriorityCreate, PriorityUpdate

CASES = [
    Case(
        "tracker.priorities.list",
        cli=["tracker", "priorities", "list"],
        mcp=("tracker_priorities_list", {}),
        exchanges=[
            (Sent("GET", "priorities"), Reply(json=[{"key": "normal", "display": "Normal"}]))
        ],
    ),
    Case(
        "tracker.priorities.create",
        args=(
            PriorityCreate(
                key="one",
                name=LocalizedName(ru="Низкий", en="Low"),
                order=60,
                description="Lowest of all",
            ),
        ),
        cli=[
            "tracker",
            "priorities",
            "create",
            "--key",
            "one",
            "--name-ru",
            "Низкий",
            "--name-en",
            "Low",
            "--order",
            "60",
            "--description",
            "Lowest of all",
        ],
        mcp=(
            "tracker_priorities_create",
            {
                "body": {
                    "key": "one",
                    "name": {"ru": "Низкий", "en": "Low"},
                    "order": 60,
                    "description": "Lowest of all",
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "priorities/",
                    json={
                        "key": "one",
                        "name": {"ru": "Низкий", "en": "Low"},
                        "order": 60,
                        "description": "Lowest of all",
                    },
                ),
                Reply(json={"key": "one"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.priorities.edit",
        args=(
            "blocker",
            PriorityUpdate(name=LocalizedName(ru="Блокер", en="Blocker"), description="Stops all"),
        ),
        kwargs={"version": 7},
        cli=[
            "tracker",
            "priorities",
            "update",
            "blocker",
            "--name-ru",
            "Блокер",
            "--name-en",
            "Blocker",
            "--description",
            "Stops all",
            "--version",
            "7",
        ],
        mcp=(
            "tracker_priorities_update",
            {
                "priority_id": "blocker",
                "body": {"name": {"ru": "Блокер", "en": "Blocker"}, "description": "Stops all"},
                "version": 7,
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "priorities/blocker",
                    {"version": "7"},
                    {"name": {"ru": "Блокер", "en": "Blocker"}, "description": "Stops all"},
                ),
                Reply(json={"key": "blocker"}),
            )
        ],
    ),
    # Without a name option no name key is sent; without --version no ?version=.
    Case(
        "tracker.priorities.edit",
        args=("minor", PriorityUpdate(description="Small")),
        cli=["tracker", "priorities", "update", "minor", "--description", "Small"],
        mcp=None,
        exchanges=[
            (
                Sent("PATCH", "priorities/minor", json={"description": "Small"}),
                Reply(json={"key": "minor"}),
            )
        ],
    ),
]

CASES += [
    # Not localized, a priority carries its name in every language.
    Case(
        "tracker.priorities.list",
        kwargs={"localized": False},
        cli=["tracker", "priorities", "list", "--no-localized"],
        mcp=("tracker_priorities_list", {"localized": False}),
        exchanges=[
            (
                Sent("GET", "priorities", {"localized": "false"}),
                Reply(json=[{"key": "trivial", "name": {"en": "Trivial", "ru": "Незначительный"}}]),
            )
        ],
    ),
]
