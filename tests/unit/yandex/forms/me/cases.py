"""Contract cases for Forms ``/users/me`` (see tests/contract/)."""

from tests.contract import Case, Reply, Sent

CASES = [
    Case(
        "forms.me.get",
        cli=["forms", "me", "get"],
        mcp=("forms_me_get", {}),
        exchanges=[
            (
                Sent("GET", "users/me"),
                Reply(json={"id": 4, "login": "ann", "display": "Ann", "email": "ann@example.com"}),
            )
        ],
    ),
]
