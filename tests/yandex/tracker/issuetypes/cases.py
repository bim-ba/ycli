"""Contract cases for Tracker ``/issuetypes`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.issuetypes.models import IssueTypeCreate, IssueTypeUpdate, LocalizedName

CASES = [
    Case(
        "tracker.issuetypes.list",
        cli=["tracker", "issuetypes", "list"],
        mcp=("tracker_issuetypes_list", {}),
        exchanges=[(Sent("GET", "issuetypes"), Reply(json=[{"id": 1, "key": "bug"}]))],
    ),
    Case(
        "tracker.issuetypes.create",
        args=(IssueTypeCreate(key="client", name=LocalizedName(ru="Клиент", en="Client")),),
        cli=[
            "tracker",
            "issuetypes",
            "create",
            "--key",
            "client",
            "--name-ru",
            "Клиент",
            "--name-en",
            "Client",
        ],
        mcp=(
            "tracker_issuetypes_create",
            {"body": {"key": "client", "name": {"ru": "Клиент", "en": "Client"}}},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issuetypes/",
                    json={"key": "client", "name": {"ru": "Клиент", "en": "Client"}},
                ),
                Reply(json={"id": 23, "key": "client"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.issuetypes.edit",
        args=("23", IssueTypeUpdate(name=LocalizedName(ru="Покупатель", en="Buyer"))),
        kwargs={"version": 2},
        cli=[
            "tracker",
            "issuetypes",
            "edit",
            "23",
            "--name-ru",
            "Покупатель",
            "--name-en",
            "Buyer",
            "--version",
            "2",
        ],
        mcp=(
            "tracker_issuetypes_edit",
            {
                "issue_type_id": "23",
                "body": {"name": {"ru": "Покупатель", "en": "Buyer"}},
                "version": 2,
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "issuetypes/23",
                    {"version": "2"},
                    {"name": {"ru": "Покупатель", "en": "Buyer"}},
                ),
                Reply(json={"id": 23, "key": "client"}),
            )
        ],
    ),
    Case(
        "tracker.issuetypes.edit",
        args=("epic", IssueTypeUpdate(name=LocalizedName(en="Saga"))),
        cli=["tracker", "issuetypes", "edit", "epic", "--name-en", "Saga"],
        mcp=None,
        exchanges=[
            (
                Sent("PATCH", "issuetypes/epic", json={"name": {"en": "Saga"}}),
                Reply(json={"key": "epic"}),
            )
        ],
    ),
]
