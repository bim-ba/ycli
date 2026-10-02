"""Contract cases for Forms ``/surveys`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent

SURVEY = {"id": "686d0a1b2c3d4e5f00000001", "name": "Onboarding"}
CREATED = {
    "name": "Onboarding",
    "language": "en",
    "is_published": True,
    "is_public": False,
    "need_auth": True,
    "max_count": 40,
}


def _listed(survey_id: str) -> dict:
    """A survey as listed with only its id, every other field unset."""
    unset = (
        "name", "dir_id", "collab_id", "created", "modified", "language", "is_published",
        "is_public", "is_banned", "answers", "is_favourite",
    )  # fmt: skip
    return {"id": survey_id, **dict.fromkeys(unset)}


CASES = [
    Case(
        "forms.surveys.list",
        kwargs={"limit": 500},
        cli=["forms", "surveys", "list"],
        mcp=("forms_surveys_list", {}),
        exchanges=[
            (
                Sent("GET", "surveys", {"offset": "0", "limit": "100"}),
                Reply(json={"result": [SURVEY]}),
            )
        ],
    ),
    Case(
        "forms.surveys.get",
        args=("686d0a1b2c3d4e5f00000001",),
        cli=["forms", "surveys", "get", "686d0a1b2c3d4e5f00000001"],
        mcp=("forms_surveys_get", {"survey_id": "686d0a1b2c3d4e5f00000001"}),
        exchanges=[(Sent("GET", "surveys/686d0a1b2c3d4e5f00000001"), Reply(json=SURVEY))],
    ),
    Case(
        "forms.surveys.create",
        args=({**CREATED, "allow_multiple_answers": False},),
        cli=[
            "forms",
            "surveys",
            "create",
            "--name",
            "Onboarding",
            "--language",
            "en",
            "--published",
            "--no-public",
            "--need-auth",
            "--max-count",
            "40",
            "--field",
            "allow_multiple_answers=false",
        ],
        mcp=("forms_surveys_create", {"body": {**CREATED, "allow_multiple_answers": False}}),
        exchanges=[
            (
                Sent("POST", "surveys", json={**CREATED, "allow_multiple_answers": False}),
                Reply(json=SURVEY, status=201),
            )
        ],
    ),
    Case(
        "forms.surveys.modify",
        args=("686d0a1b2c3d4e5f00000002", {"name": "Renamed", "is_public": True, "max_count": 9}),
        cli=[
            "forms",
            "surveys",
            "modify",
            "686d0a1b2c3d4e5f00000002",
            "--name",
            "Renamed",
            "--public",
            "--max-count",
            "9",
        ],
        mcp=(
            "forms_surveys_modify",
            {
                "survey_id": "686d0a1b2c3d4e5f00000002",
                "body": {"name": "Renamed", "is_public": True, "max_count": 9},
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "surveys/686d0a1b2c3d4e5f00000002",
                    json={"name": "Renamed", "is_public": True, "max_count": 9},
                ),
                Reply(json=SURVEY),
            )
        ],
    ),
    Case(
        "forms.surveys.delete",
        args=("686d0a1b2c3d4e5f00000003",),
        cli=["forms", "surveys", "delete", "686d0a1b2c3d4e5f00000003"],
        mcp=("forms_surveys_delete", {"survey_id": "686d0a1b2c3d4e5f00000003"}),
        exchanges=[(Sent("DELETE", "surveys/686d0a1b2c3d4e5f00000003"), Reply(status=204))],
        output={"ok": True, "detail": "deleted survey 686d0a1b2c3d4e5f00000003"},
    ),
    Case(
        "forms.surveys.publish",
        args=("686d0a1b2c3d4e5f00000004",),
        cli=["forms", "surveys", "publish", "686d0a1b2c3d4e5f00000004"],
        mcp=("forms_surveys_publish", {"survey_id": "686d0a1b2c3d4e5f00000004"}),
        exchanges=[(Sent("POST", "surveys/686d0a1b2c3d4e5f00000004/publish"), Reply())],
        output={"ok": True, "detail": "published survey 686d0a1b2c3d4e5f00000004"},
    ),
    Case(
        "forms.surveys.unpublish",
        args=("686d0a1b2c3d4e5f00000005",),
        cli=["forms", "surveys", "unpublish", "686d0a1b2c3d4e5f00000005"],
        mcp=("forms_surveys_unpublish", {"survey_id": "686d0a1b2c3d4e5f00000005"}),
        exchanges=[(Sent("POST", "surveys/686d0a1b2c3d4e5f00000005/unpublish"), Reply())],
        output={"ok": True, "detail": "unpublished survey 686d0a1b2c3d4e5f00000005"},
    ),
    # A limit below the page keeps only that many surveys, on every surface.
    Case(
        "forms.surveys.list",
        kwargs={"limit": 2},
        cli=["forms", "surveys", "list", "--limit", "2"],
        mcp=("forms_surveys_list", {"limit": 2}),
        exchanges=[
            (
                Sent("GET", "surveys", {"offset": "0", "limit": "100"}),
                Reply(json={"result": [{"id": "s1"}, {"id": "s2"}, {"id": "s3"}]}),
            )
        ],
        output=[_listed("s1"), _listed("s2")],
    ),
    # --all lifts the configured cap (shrunk to 1 here, so a CLI ignoring --all keeps one).
    Case(
        "forms.surveys.list",
        kwargs={"limit": None},
        cli=["forms", "surveys", "list", "--all"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "surveys", {"offset": "0", "limit": "100"}),
                Reply(json={"result": [{"id": "all-1"}, {"id": "all-2"}]}),
            )
        ],
        env={"YCLI__HTTP__MAX_ITEMS": "1"},
    ),
]
