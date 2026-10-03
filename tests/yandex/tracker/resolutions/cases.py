"""Contract cases for Tracker ``/resolutions`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.models import LocalizedName
from ycli.yandex.tracker.resolutions.models import ResolutionCreate, ResolutionUpdate

CASES = [
    Case(
        "tracker.resolutions.list",
        cli=["tracker", "resolutions", "list"],
        mcp=("tracker_resolutions_list", {}),
        exchanges=[(Sent("GET", "resolutions"), Reply(json=[{"id": 1, "key": "fixed"}]))],
    ),
    Case(
        "tracker.resolutions.create",
        args=(ResolutionCreate(key="wontFix", name=LocalizedName(ru="Отклонено", en="Won't fix")),),
        cli=[
            "tracker",
            "resolutions",
            "create",
            "--key",
            "wontFix",
            "--name-ru",
            "Отклонено",
            "--name-en",
            "Won't fix",
        ],
        mcp=(
            "tracker_resolutions_create",
            {"body": {"key": "wontFix", "name": {"ru": "Отклонено", "en": "Won't fix"}}},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "resolutions/",
                    json={"key": "wontFix", "name": {"ru": "Отклонено", "en": "Won't fix"}},
                ),
                Reply(json={"id": 9, "key": "wontFix"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.resolutions.update",
        args=(
            "9",
            ResolutionUpdate(
                name=LocalizedName(ru="Отложено", en="Never"),
                description="Won't be fixed",
                order=90,
            ),
        ),
        kwargs={"version": 3},
        cli=[
            "tracker",
            "resolutions",
            "update",
            "9",
            "--name-ru",
            "Отложено",
            "--name-en",
            "Never",
            "--description",
            "Won't be fixed",
            "--order",
            "90",
            "--version",
            "3",
        ],
        mcp=(
            "tracker_resolutions_update",
            {
                "resolution_id": "9",
                "body": {
                    "name": {"ru": "Отложено", "en": "Never"},
                    "description": "Won't be fixed",
                    "order": 90,
                },
                "version": 3,
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "resolutions/9",
                    {"version": "3"},
                    {
                        "name": {"ru": "Отложено", "en": "Never"},
                        "description": "Won't be fixed",
                        "order": 90,
                    },
                ),
                Reply(json={"id": 9, "version": 4}),
            )
        ],
    ),
    Case(
        "tracker.resolutions.update",
        args=("duplicate", ResolutionUpdate(order=15)),
        cli=["tracker", "resolutions", "update", "duplicate", "--order", "15"],
        mcp=None,
        exchanges=[
            (
                Sent("PATCH", "resolutions/duplicate", json={"order": 15}),
                Reply(json={"key": "duplicate"}),
            )
        ],
    ),
]
