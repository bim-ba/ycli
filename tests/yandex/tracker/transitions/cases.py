"""Contract cases for Tracker issue ``/transitions`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.transitions.models import TransitionExecute

AFTER_CLOSE = [{"id": "reopen", "to": {"id": "1", "key": "open", "display": "Open"}}]

CASES = [
    Case(
        "tracker.transitions.list",
        args=("DE-51",),
        cli=["tracker", "transitions", "list", "DE-51"],
        mcp=("tracker_transitions_list", {"issue_key": "DE-51"}),
        exchanges=[
            (
                Sent("GET", "issues/DE-51/transitions"),
                Reply(json=[{"id": "close", "to": {"key": "closed", "display": "Closed"}}]),
            )
        ],
    ),
    # `--field` values are JSON-coerced.
    Case(
        "tracker.transitions.execute",
        args=(
            "DE-52",
            "close",
            TransitionExecute.model_validate(
                {"comment": "done", "resolution": "fixed", "storyPoints": 3}
            ),
        ),
        cli=[
            "tracker",
            "transitions",
            "execute",
            "DE-52",
            "close",
            "--field",
            "comment=done",
            "--field",
            "resolution=fixed",
            "-F",
            "storyPoints=3",
        ],
        mcp=(
            "tracker_transitions_execute",
            {
                "issue_key": "DE-52",
                "transition_id": "close",
                "body": {"comment": "done", "resolution": "fixed", "storyPoints": 3},
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/DE-52/transitions/close/_execute",
                    json={"comment": "done", "resolution": "fixed", "storyPoints": 3},
                ),
                Reply(json=AFTER_CLOSE),
            )
        ],
    ),
    Case(
        "tracker.transitions.execute",
        args=("DE-53", "start_progress", TransitionExecute.model_validate({})),
        cli=["tracker", "transitions", "execute", "DE-53", "start_progress"],
        mcp=(
            "tracker_transitions_execute",
            {"issue_key": "DE-53", "transition_id": "start_progress", "body": {}},
        ),
        exchanges=[
            (
                Sent("POST", "issues/DE-53/transitions/start_progress/_execute", json={}),
                Reply(json=[{"id": "stop_progress"}]),
            )
        ],
    ),
]
