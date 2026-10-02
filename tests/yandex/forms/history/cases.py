"""Contract cases for Forms ``/surveys/{id}/history`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent


def _event(event_id: int, model: str) -> dict:
    return {
        "id": event_id,
        "created": "2026-10-02T14:29:33Z",
        "user": {
            "identity": {"uid": "101523906", "cloud_uid": "ajen8nffceu4rqs0i39r"},
            "username": "znatnov-sava",
            "display_name": "Сава Знатнов",
        },
        "model": model,
        "action": "POST api-v1:get_hooks_public_view",
    }


FIRST = _event(406971234, "servicesurveyhooksubscription")
SECOND = _event(406971230, "surveyhook")
THIRD = _event(406971101, "survey")

CASES = [
    Case(
        "forms.history.list",
        args=("686d0a1b2c3d4e5f000000e1",),
        kwargs={"ordering": "asc", "limit": 500},
        cli=["forms", "history", "list", "686d0a1b2c3d4e5f000000e1", "--ordering", "asc"],
        mcp=("forms_history_list", {"survey_id": "686d0a1b2c3d4e5f000000e1", "ordering": "asc"}),
        exchanges=[
            (
                Sent(
                    "GET",
                    "surveys/686d0a1b2c3d4e5f000000e1/history",
                    {"ordering": "asc", "limit": "100"},
                ),
                Reply(json={"iteration_key": 406971226, "limit": 100, "items": [FIRST, SECOND]}),
            ),
            (
                Sent(
                    "GET",
                    "surveys/686d0a1b2c3d4e5f000000e1/history",
                    {"ordering": "asc", "limit": "100", "iteration_key": "406971226"},
                ),
                Reply(json={"iteration_key": 406971226, "limit": 100, "items": []}),
            ),
        ],
        output=[FIRST, SECOND],
    ),
    Case(
        "forms.history.list",
        args=("686d0a1b2c3d4e5f000000e2",),
        kwargs={"limit": 1},
        cli=["forms", "history", "list", "686d0a1b2c3d4e5f000000e2", "--limit", "1"],
        mcp=("forms_history_list", {"survey_id": "686d0a1b2c3d4e5f000000e2", "limit": 1}),
        exchanges=[
            (
                Sent("GET", "surveys/686d0a1b2c3d4e5f000000e2/history", {"limit": "100"}),
                Reply(json={"iteration_key": 406971226, "limit": 100, "items": [FIRST, SECOND]}),
            ),
        ],
        output=[FIRST],
    ),
    Case(
        "forms.history.list",
        args=("686d0a1b2c3d4e5f000000e3",),
        kwargs={"ordering": "desc", "limit": None},
        cli=[
            "forms",
            "history",
            "list",
            "686d0a1b2c3d4e5f000000e3",
            "--ordering",
            "desc",
            "--all",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "GET",
                    "surveys/686d0a1b2c3d4e5f000000e3/history",
                    {"ordering": "desc", "limit": "100"},
                ),
                Reply(json={"iteration_key": 406971200, "limit": 100, "items": [FIRST]}),
            ),
            (
                Sent(
                    "GET",
                    "surveys/686d0a1b2c3d4e5f000000e3/history",
                    {"ordering": "desc", "limit": "100", "iteration_key": "406971200"},
                ),
                Reply(json={"limit": 100, "items": [SECOND, THIRD]}),
            ),
        ],
        output=[FIRST, SECOND, THIRD],
    ),
]
