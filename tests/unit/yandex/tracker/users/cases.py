"""Contract cases for Tracker ``/users`` (see tests/contract/)."""

from tests.contract import Case, Reply, Sent

CASES = [
    Case(
        "tracker.users.get",
        args=("username",),
        kwargs={"expand": "groups"},
        cli=["tracker", "users", "get", "username", "--expand", "groups"],
        mcp=("tracker_users_get", {"login_or_id": "username", "expand": "groups"}),
        exchanges=[
            (
                Sent("GET", "users/username", {"expand": "groups"}),
                Reply(json={"uid": 12, "login": "username", "display": "Ivan Ivanov"}),
            )
        ],
    ),
    Case(
        "tracker.users.get",
        args=("login:12345",),
        cli=["tracker", "users", "get", "login:12345"],
        mcp=("tracker_users_get", {"login_or_id": "login:12345"}),
        exchanges=[
            (
                Sent("GET", "users/login%3A12345"),
                Reply(json={"uid": 13, "login": "12345"}),
            )
        ],
    ),
    # Each next page repeats with id=<uid of the last user>; an empty page ends the walk.
    Case(
        "tracker.users.list",
        kwargs={"limit": 500, "expand": "groups"},
        cli=["tracker", "users", "list", "--expand", "groups"],
        mcp=("tracker_users_list", {"expand": "groups"}),
        exchanges=[
            (
                Sent("GET", "users/_relative", {"perPage": "100", "expand": "groups"}),
                Reply(json={"users": [{"uid": 1, "login": "a"}, {"uid": 2}], "hasNext": True}),
            ),
            (
                Sent("GET", "users/_relative", {"perPage": "100", "expand": "groups", "id": "2"}),
                Reply(json={"users": [{"uid": 3, "login": "c"}], "hasNext": True}),
            ),
            (
                Sent("GET", "users/_relative", {"perPage": "100", "expand": "groups", "id": "3"}),
                Reply(json={"users": [], "hasNext": False}),
            ),
        ],
    ),
    # A small cap narrows the page.
    Case(
        "tracker.users.list",
        kwargs={"limit": 1},
        cli=["tracker", "users", "list", "--limit", "1"],
        mcp=("tracker_users_list", {"limit": 1}),
        exchanges=[
            (
                Sent("GET", "users/_relative", {"perPage": "1"}),
                Reply(json={"users": [{"uid": 7, "login": "solo"}], "hasNext": True}),
            )
        ],
    ),
    # A last user without a uid gives no cursor, so the walk ends.
    Case(
        "tracker.users.list",
        kwargs={"limit": None},
        cli=["tracker", "users", "list", "--all"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "users/_relative", {"perPage": "100"}),
                Reply(json={"users": [{"login": "no-uid"}], "hasNext": True}),
            )
        ],
    ),
]
