"""Contract cases for Tracker issue ``/remotelinks`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.remotelinks.models import RemoteLinkCreate

CASES = [
    Case(
        "tracker.remotelinks.list",
        args=("JUNE-2",),
        cli=["tracker", "remotelinks", "list", "JUNE-2"],
        mcp=("tracker_remotelinks_list", {"issue_key": "JUNE-2"}),
        exchanges=[
            (
                Sent("GET", "issues/JUNE-2/remotelinks"),
                Reply(json=[{"id": 51, "object": {"key": "TEST-17"}}]),
            )
        ],
    ),
    Case(
        "tracker.remotelinks.create",
        args=(
            "JUNE-3",
            RemoteLinkCreate.model_validate(
                {"relationship": "BLOCKS", "key": "TEST-18", "origin": "ru.yandex.bitbucket"}
            ),
        ),
        kwargs={"backlink": "true"},
        cli=[
            "tracker",
            "remotelinks",
            "create",
            "JUNE-3",
            "--key",
            "TEST-18",
            "--origin",
            "ru.yandex.bitbucket",
            "--relationship",
            "BLOCKS",
            "--backlink",
        ],
        mcp=(
            "tracker_remotelinks_create",
            {
                "issue_key": "JUNE-3",
                "body": {
                    "relationship": "BLOCKS",
                    "key": "TEST-18",
                    "origin": "ru.yandex.bitbucket",
                },
                "backlink": "true",
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/JUNE-3/remotelinks",
                    {"backlink": "true"},
                    {"relationship": "BLOCKS", "key": "TEST-18", "origin": "ru.yandex.bitbucket"},
                ),
                Reply(json={"id": 52, "object": {"key": "TEST-18"}}, status=201),
            )
        ],
    ),
    # --no-backlink is sent as backlink=false.
    Case(
        "tracker.remotelinks.create",
        args=(
            "JUNE-4",
            RemoteLinkCreate.model_validate(
                {"relationship": "RELATES", "key": "TEST-19", "origin": "ru.yandex.lunapark"}
            ),
        ),
        kwargs={"backlink": False},
        cli=[
            "tracker",
            "remotelinks",
            "create",
            "JUNE-4",
            "--relationship",
            "RELATES",
            "--no-backlink",
            "--key",
            "TEST-19",
            "--origin",
            "ru.yandex.lunapark",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/JUNE-4/remotelinks",
                    {"backlink": "false"},
                    {"relationship": "RELATES", "key": "TEST-19", "origin": "ru.yandex.lunapark"},
                ),
                Reply(json={"id": 53, "object": {"key": "TEST-19"}}, status=201),
            )
        ],
    ),
    # Without a backlink no query is sent at all.
    Case(
        "tracker.remotelinks.create",
        args=(
            "JUNE-5",
            RemoteLinkCreate.model_validate(
                {"relationship": "RELATES", "key": "TEST-20", "origin": "ru.yandex.jenkins"}
            ),
        ),
        cli=None,
        mcp=(
            "tracker_remotelinks_create",
            {
                "issue_key": "JUNE-5",
                "body": {
                    "relationship": "RELATES",
                    "key": "TEST-20",
                    "origin": "ru.yandex.jenkins",
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/JUNE-5/remotelinks",
                    json={
                        "relationship": "RELATES",
                        "key": "TEST-20",
                        "origin": "ru.yandex.jenkins",
                    },
                ),
                Reply(json={"id": 54, "object": {"key": "TEST-20"}}, status=201),
            )
        ],
    ),
    Case(
        "tracker.remotelinks.delete",
        args=("JUNE-6", "55"),
        cli=["tracker", "remotelinks", "delete", "JUNE-6", "55"],
        mcp=("tracker_remotelinks_delete", {"issue_key": "JUNE-6", "link_id": "55"}),
        exchanges=[(Sent("DELETE", "issues/JUNE-6/remotelinks/55"), Reply(status=204))],
    ),
]
