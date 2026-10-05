"""Contract cases for Forms display conditions (see tests/contract/).

The four targets share one shape, so :func:`_family` writes the six cases of a target from its
literal ids and path; every case still spells its own condition id and body.
"""

import json
from pathlib import Path

from tests.contract import Case, Reply, Sent
from ycli.yandex.forms.conditions.models import ConditionCreate, ConditionUpdate

SID = "686d0a1b2c3d4e5f00000090"
GROUP_FILE = str(Path(__file__).with_name("group.json"))
FROM_FILE = {
    "operator": "or",
    "items": [{"type": "origin", "condition": "neq", "value": "partner-site"}],
}


def _group(condition_id: int) -> dict:
    return {
        "id": condition_id,
        "operator": "and",
        "items": [{"type": "question", "condition": "eq", "question": "q1", "value": "yes"}],
    }


def _envelope(condition_id: int) -> dict:
    return {"operator": "or", "items": [_group(condition_id)]}


def _family(
    family: str, owner_cli: list[str], owner_mcp: dict, owner_sdk: tuple, path: str, base: int
) -> list[Case]:
    """The six cases of one target; ``base`` keeps every id distinct across families."""
    created = {
        "operator": "and",
        "items": [{"type": "question", "condition": "gt", "question": f"age{base}", "value": "18"}],
    }
    replaced = {"operator": "or", "items": [{"type": "language", "condition": "eq", "value": "ru"}]}
    cli = ["forms", "conditions", family]
    tool = f"forms_conditions_{family}_"
    return [
        Case(
            f"forms.conditions.{family}_list",
            args=(SID, *owner_sdk),
            cli=[*cli, "list", SID, *owner_cli],
            mcp=(f"{tool}list", {"survey_id": SID, **owner_mcp}),
            exchanges=[(Sent("GET", path), Reply(json=_envelope(base + 1)))],
        ),
        Case(
            f"forms.conditions.{family}_get",
            args=(SID, *owner_sdk, base + 2),
            cli=[*cli, "get", SID, *owner_cli, str(base + 2)],
            mcp=(f"{tool}get", {"survey_id": SID, **owner_mcp, "condition_id": base + 2}),
            exchanges=[(Sent("GET", f"{path}/{base + 2}"), Reply(json=_group(base + 2)))],
        ),
        Case(
            f"forms.conditions.{family}_create",
            args=(SID, *owner_sdk, ConditionCreate.model_validate(created)),
            cli=[
                *cli,
                "create",
                SID,
                *owner_cli,
                "--operator",
                "and",
                "--item",
                json.dumps(created["items"][0]),
            ],
            mcp=(f"{tool}create", {"survey_id": SID, **owner_mcp, "body": created}),
            exchanges=[(Sent("POST", path, json=created), Reply(json=_group(base + 3)))],
        ),
        Case(
            f"forms.conditions.{family}_update",
            args=(SID, *owner_sdk, base + 4, ConditionUpdate.model_validate(replaced)),
            cli=[
                *cli,
                "update",
                SID,
                *owner_cli,
                str(base + 4),
                "--operator",
                "or",
                "--item",
                '{"type": "language", "condition": "eq", "value": "ru"}',
            ],
            mcp=(
                f"{tool}update",
                {"survey_id": SID, **owner_mcp, "condition_id": base + 4, "body": replaced},
            ),
            exchanges=[
                (Sent("PATCH", f"{path}/{base + 4}", json=replaced), Reply(json=_group(base + 4)))
            ],
        ),
        Case(
            f"forms.conditions.{family}_update",
            args=(SID, *owner_sdk, base + 5, ConditionUpdate.model_validate(FROM_FILE)),
            cli=[*cli, "update", SID, *owner_cli, str(base + 5), "--body-file", GROUP_FILE],
            mcp=None,
            exchanges=[
                (Sent("PATCH", f"{path}/{base + 5}", json=FROM_FILE), Reply(json=_group(base + 5)))
            ],
        ),
        Case(
            f"forms.conditions.{family}_delete",
            args=(SID, *owner_sdk, base + 6),
            cli=[*cli, "delete", SID, *owner_cli, str(base + 6)],
            mcp=(f"{tool}delete", {"survey_id": SID, **owner_mcp, "condition_id": base + 6}),
            exchanges=[(Sent("DELETE", f"{path}/{base + 6}"), Reply())],
        ),
        Case(
            f"forms.conditions.{family}_update_operator",
            args=(SID, *owner_sdk, "and"),
            cli=[*cli, "update-operator", SID, *owner_cli, "--operator", "and"],
            mcp=(f"{tool}update_operator", {"survey_id": SID, **owner_mcp, "operator": "and"}),
            exchanges=[
                (Sent("PATCH", path, json={"operator": "and"}), Reply(json=_envelope(base + 7)))
            ],
        ),
    ]


CASES = [
    *_family(
        "question",
        ["17"],
        {"question_id": "17"},
        ("17",),
        f"surveys/{SID}/questions/17/conditions",
        100,
    ),
    *_family("page", ["3"], {"page_id": 3}, (3,), f"surveys/{SID}/pages/3/conditions", 200),
    *_family("submit", [], {}, (), f"surveys/{SID}/conditions", 300),
    *_family("hook", ["11"], {"hook_id": 11}, (11,), f"surveys/{SID}/hooks/11/conditions", 400),
    Case(
        "forms.conditions.submit_create",
        args=(SID, ConditionCreate.model_validate(FROM_FILE)),
        cli=["forms", "conditions", "submit", "create", SID, "--body-file", GROUP_FILE],
        mcp=None,
        exchanges=[
            (Sent("POST", f"surveys/{SID}/conditions", json=FROM_FILE), Reply(json=_group(9)))
        ],
    ),
]
