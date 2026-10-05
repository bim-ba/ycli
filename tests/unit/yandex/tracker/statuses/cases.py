"""Contract cases for Tracker ``/statuses`` (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.models import LocalizedName
from ycli.yandex.tracker.statuses.models import StatusCreate, StatusUpdate

CASES = [
    Case(
        "tracker.statuses.list",
        cli=["tracker", "statuses", "list"],
        mcp=("tracker_statuses_list", {}),
        exchanges=[(Sent("GET", "statuses"), Reply(json=[{"id": 1, "key": "open"}]))],
    ),
    Case(
        "tracker.statuses.create",
        args=(
            StatusCreate(key="pause", name=LocalizedName(ru="Пауза", en="Paused"), type="paused"),
        ),
        cli=[
            "tracker",
            "statuses",
            "create",
            "--key",
            "pause",
            "--name-ru",
            "Пауза",
            "--name-en",
            "Paused",
            "--type",
            "paused",
        ],
        mcp=(
            "tracker_statuses_create",
            {"body": {"key": "pause", "name": {"ru": "Пауза", "en": "Paused"}, "type": "paused"}},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "statuses/",
                    json={
                        "key": "pause",
                        "name": {"ru": "Пауза", "en": "Paused"},
                        "type": "paused",
                    },
                ),
                Reply(json={"id": 29, "key": "pause"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.statuses.create",
        args=(StatusCreate(key="fresh", name=LocalizedName(ru="Новый"), type="new"),),
        cli=[
            "tracker",
            "statuses",
            "create",
            "--key",
            "fresh",
            "--name-ru",
            "Новый",
            "--type",
            "new",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "statuses/",
                    json={"key": "fresh", "name": {"ru": "Новый"}, "type": "new"},
                ),
                Reply(json={"id": 30, "key": "fresh"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.statuses.update",
        args=(
            "29",
            StatusUpdate(
                name=LocalizedName(ru="Ожидание", en="Waiting"),
                description="Issue is paused",
                order=350,
                type="inProgress",
            ),
        ),
        kwargs={"version": 5},
        cli=[
            "tracker",
            "statuses",
            "update",
            "29",
            "--name-ru",
            "Ожидание",
            "--name-en",
            "Waiting",
            "--description",
            "Issue is paused",
            "--order",
            "350",
            "--type",
            "inProgress",
            "--version",
            "5",
        ],
        mcp=(
            "tracker_statuses_update",
            {
                "status_id": "29",
                "body": {
                    "name": {"ru": "Ожидание", "en": "Waiting"},
                    "description": "Issue is paused",
                    "order": 350,
                    "type": "inProgress",
                },
                "version": 5,
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "statuses/29",
                    {"version": "5"},
                    {
                        "name": {"ru": "Ожидание", "en": "Waiting"},
                        "description": "Issue is paused",
                        "order": 350,
                        "type": "inProgress",
                    },
                ),
                Reply(json={"id": 29, "version": 6}),
            )
        ],
    ),
    Case(
        "tracker.statuses.update",
        args=("closed", StatusUpdate(order=900)),
        cli=["tracker", "statuses", "update", "closed", "--order", "900"],
        mcp=None,
        exchanges=[
            (
                Sent("PATCH", "statuses/closed", json={"order": 900}),
                Reply(json={"key": "closed"}),
            )
        ],
    ),
]
