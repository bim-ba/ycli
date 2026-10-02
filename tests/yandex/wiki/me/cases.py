"""Contract cases for Wiki ``/users/me`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent

ME = {
    "username": "vera.petrova",
    "home_cluster": "homepage",
    "identity": {"uid": "1130000011", "cloud_uid": "ajeu7l2e"},
    "org": {"dir_id": "7700112", "collab_id": "21b4c0aa-3d0f-4c55-9a52-2f4a7a6f1c11"},
}

CASES = [
    Case(
        "wiki.me.get",
        cli=["wiki", "me", "get"],
        mcp=("wiki_me_get", {}),
        exchanges=[(Sent("GET", "users/me"), Reply(json=ME))],
    ),
]
