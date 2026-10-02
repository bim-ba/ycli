"""Contract cases for Tracker ``/gaps`` (employee absences; see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.gaps.models import GapInput, GapsCreate, GapWorkflow

USER = {
    "self": "https://api.tracker.yandex.net/v3/users/1234567890123456",
    "uid": 1234567890123456,
    "login": "ann",
    "trackerUid": 1234567890123456,
    "passportUid": 1234567890,
    "cloudUid": "ajehs6sinuiii1234567",
    "firstName": "Ann",
    "lastName": "Lee",
    "display": "Ann Lee",
    "email": "ann@example.com",
    "external": False,
    "dismissed": False,
    "firstLoginDate": "2024-04-10T10:15:47.272+0000",
    "lastLoginDate": "2026-07-23T08:11:01.861+0000",
    "sources": ["directory"],
}
FIRST = {
    "id": "68340a1f2b4c1a3d5e7f9011",
    "user": "ann",
    "workflow": "vacation",
    "from": "2026-07-01T00:00:00.000Z",
    "to": "2026-07-15T00:00:00.000Z",
    "fullDay": True,
    "workInAbsence": False,
}
SECOND = {
    "user": "bob",
    "workflow": "trip",
    "from": "2026-07-10T00:00:00.000Z",
    "to": "2026-07-20T00:00:00.000Z",
}

CASES = [
    Case(
        "tracker.gaps.create",
        args=(
            GapsCreate(
                gaps=[
                    GapInput(
                        id="68340a1f2b4c1a3d5e7f9011",
                        user="ann",
                        workflow=GapWorkflow.VACATION,
                        date_from="2026-07-01T00:00:00.000Z",
                        date_to="2026-07-15T00:00:00.000Z",
                        full_day=True,
                        work_in_absence=False,
                    ),
                    GapInput(
                        user="bob",
                        workflow=GapWorkflow.TRIP,
                        date_from="2026-07-10T00:00:00.000Z",
                        date_to="2026-07-20T00:00:00.000Z",
                    ),
                ]
            ),
        ),
        cli=[
            "tracker",
            "gaps",
            "create",
            "--user",
            "ann",
            "--workflow",
            "vacation",
            "--from",
            "2026-07-01T00:00:00.000Z",
            "--to",
            "2026-07-15T00:00:00.000Z",
            "--id",
            "68340a1f2b4c1a3d5e7f9011",
            "--full-day",
            "--no-work-in-absence",
            "--gap",
            '{"user": "bob", "workflow": "trip", "from": "2026-07-10T00:00:00.000Z", '
            '"to": "2026-07-20T00:00:00.000Z"}',
        ],
        mcp=(
            "tracker_gaps_create",
            {
                "body": {
                    "gaps": [
                        {
                            "id": "68340a1f2b4c1a3d5e7f9011",
                            "user": "ann",
                            "workflow": "vacation",
                            "from": "2026-07-01T00:00:00.000Z",
                            "to": "2026-07-15T00:00:00.000Z",
                            "fullDay": True,
                            "workInAbsence": False,
                        },
                        SECOND,
                    ]
                }
            },
        ),
        exchanges=[
            (
                Sent("POST", "gaps", json={"gaps": [FIRST, SECOND]}),
                Reply(
                    json={
                        "gaps": [
                            {
                                "id": "68340a1f2b4c1a3d5e7f9011",
                                "user": USER,
                                "workflow": "vacation",
                                "from": "2026-07-01T00:00:00.000+0000",
                                "to": "2026-07-15T00:00:00.000+0000",
                                "fullDay": True,
                                "workInAbsence": False,
                            }
                        ]
                    }
                ),
            )
        ],
    ),
    # One absence from the flags alone: the optional parts are left out of the body.
    Case(
        "tracker.gaps.create",
        args=(
            GapsCreate(
                gaps=[
                    GapInput(
                        user="cy",
                        workflow=GapWorkflow.DUTY,
                        date_from="2026-08-01T00:00:00.000Z",
                        date_to="2026-08-02T00:00:00.000Z",
                    )
                ]
            ),
        ),
        cli=[
            "tracker",
            "gaps",
            "create",
            "--user",
            "cy",
            "--workflow",
            "duty",
            "--from",
            "2026-08-01T00:00:00.000Z",
            "--to",
            "2026-08-02T00:00:00.000Z",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "gaps",
                    json={
                        "gaps": [
                            {
                                "user": "cy",
                                "workflow": "duty",
                                "from": "2026-08-01T00:00:00.000Z",
                                "to": "2026-08-02T00:00:00.000Z",
                            }
                        ]
                    },
                ),
                Reply(json={"gaps": [{"id": "g-cy", "workflow": "duty", "fullDay": False}]}),
            )
        ],
    ),
    Case(
        "tracker.gaps.search",
        args=(["ann", "bob"],),
        kwargs={"date_from": "2026-07-01T00:00:00.000Z", "date_to": "2026-08-31T23:59:59.999Z"},
        cli=[
            "tracker",
            "gaps",
            "search",
            "ann",
            "bob",
            "--from",
            "2026-07-01T00:00:00.000Z",
            "--to",
            "2026-08-31T23:59:59.999Z",
        ],
        mcp=(
            "tracker_gaps_search",
            {
                "users": ["ann", "bob"],
                "date_from": "2026-07-01T00:00:00.000Z",
                "date_to": "2026-08-31T23:59:59.999Z",
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "gaps/_search",
                    {"page": "1", "perPage": "50"},
                    {
                        "users": ["ann", "bob"],
                        "from": "2026-07-01T00:00:00.000Z",
                        "to": "2026-08-31T23:59:59.999Z",
                    },
                ),
                Reply(
                    json={
                        "userGaps": [
                            {
                                "user": USER,
                                "gaps": [
                                    {
                                        "id": "g-ann",
                                        "workflow": "vacation",
                                        "from": "2026-07-01T00:00:00.000+0000",
                                        "to": "2026-07-15T00:00:00.000+0000",
                                        "fullDay": True,
                                        "workInAbsence": False,
                                    }
                                ],
                            },
                            {"user": {**USER, "login": "bob"}, "gaps": []},
                        ],
                        "hasMore": False,
                    }
                ),
            )
        ],
        effect="read",
    ),
    # Without a window only the users go out; --limit caps the users returned.
    Case(
        "tracker.gaps.search",
        args=(["dee", "eve"],),
        kwargs={"limit": 1},
        cli=["tracker", "gaps", "search", "dee", "eve", "--limit", "1"],
        mcp=("tracker_gaps_search", {"users": ["dee", "eve"], "limit": 1}),
        exchanges=[
            (
                Sent(
                    "POST",
                    "gaps/_search",
                    {"page": "1", "perPage": "50"},
                    {"users": ["dee", "eve"]},
                ),
                Reply(
                    json={
                        "userGaps": [
                            {"user": {"login": "dee"}, "gaps": []},
                            {"user": {"login": "eve"}, "gaps": []},
                        ],
                        "hasMore": False,
                    }
                ),
            )
        ],
        effect="read",
        output=[
            {
                "user": {
                    "self": None,
                    "uid": None,
                    "login": "dee",
                    "trackerUid": None,
                    "passportUid": None,
                    "cloudUid": None,
                    "firstName": None,
                    "lastName": None,
                    "display": None,
                    "email": None,
                    "external": None,
                    "dismissed": None,
                    "firstLoginDate": None,
                    "lastLoginDate": None,
                    "sources": [],
                },
                "gaps": [],
            }
        ],
    ),
    Case(
        "tracker.gaps.search",
        args=(["fay"],),
        kwargs={"limit": None},
        cli=["tracker", "gaps", "search", "fay", "--all"],
        mcp=None,
        exchanges=[
            (
                Sent("POST", "gaps/_search", {"page": "1", "perPage": "50"}, {"users": ["fay"]}),
                Reply(
                    json={"userGaps": [{"user": {"login": "fay"}, "gaps": []}], "hasMore": False}
                ),
            )
        ],
        effect="read",
    ),
    Case(
        "tracker.gaps.delete",
        args=(["68340a1f2b4c1a3d5e7f9011", "68340a1f2b4c1a3d5e7f9012"],),
        cli=[
            "tracker",
            "gaps",
            "delete",
            "68340a1f2b4c1a3d5e7f9011",
            "68340a1f2b4c1a3d5e7f9012",
        ],
        mcp=(
            "tracker_gaps_delete",
            {"gap_ids": ["68340a1f2b4c1a3d5e7f9011", "68340a1f2b4c1a3d5e7f9012"]},
        ),
        exchanges=[
            (
                Sent(
                    "DELETE",
                    "gaps",
                    {"gapIds": "68340a1f2b4c1a3d5e7f9011,68340a1f2b4c1a3d5e7f9012"},
                ),
                Reply(status=204),
            )
        ],
    ),
]
