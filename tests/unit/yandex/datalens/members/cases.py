"""Contract cases for DataLens members (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect

# The keys of a live reply (2026-10-06). The people are made up.
ANN = {
    "sub": "user-1",
    "subType": "USER_ACCOUNT",
    "subStatus": "ACTIVE",
    "name": "Ann Example",
    "email": "ann@example.com",
    "givenName": "Ann",
    "familyName": "Example",
    "preferredUsername": "ann",
    "lastAuthenticatedAt": None,
}
ANNA = {**ANN, "sub": "user-2", "name": "Anna Example", "email": "anna@example.com"}

CASES = [
    Case(
        "datalens.members.list",
        kwargs={"search": "ann", "limit": 45},
        cli=["datalens", "members", "list", "--search", "ann", "--limit", "45"],
        mcp=("datalens_members_list", {"search": "ann", "limit": 45}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/batchListMembers", json={"search": "ann"}),
                Reply(json={"members": [ANN], "nextPageToken": "t2"}),
            ),
            (
                Sent("POST", "rpc/batchListMembers", json={"search": "ann", "pageToken": "t2"}),
                # The last page carries an empty token, not a missing one.
                Reply(json={"members": [ANNA], "nextPageToken": ""}),
            ),
        ],
    ),
    Case(
        "datalens.members.list",
        kwargs={"limit": 45, "language": "en", "tab_id": "GROUP", "filter": "name:fin"},
        cli=[
            *("datalens", "members", "list", "--limit", "45", "--language", "en"),
            *("--tab-id", "GROUP", "--filter", "name:fin"),
        ],
        mcp=(
            "datalens_members_list",
            {"limit": 45, "language": "en", "tab_id": "GROUP", "filter": "name:fin"},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/batchListMembers",
                    json={"language": "en", "tabId": "GROUP", "filter": "name:fin"},
                ),
                Reply(json={"members": [], "nextPageToken": ""}),
            )
        ],
    ),
]
