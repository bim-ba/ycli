"""Contract cases for Forms ``/surveys`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.forms.surveys.models import SurveyCreate, SurveyUpdate

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
        "is_public", "is_banned", "answers", "is_favourite", "hashed_id", "author", "need_auth",
        "allow_multiple_answers", "show_last_answer", "max_count", "texts", "styles", "quiz",
        "auto_publication", "follow", "followers", "captcha", "metric", "file_storage",
        "validator_url", "iframe", "footer", "teaser", "stats", "share", "fill_again",
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
        args=(SurveyCreate.model_validate({**CREATED, "allow_multiple_answers": False}),),
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
        args=(
            "686d0a1b2c3d4e5f00000002",
            SurveyUpdate.model_validate({"name": "Renamed", "is_public": True, "max_count": 9}),
        ),
        cli=[
            "forms",
            "surveys",
            "update",
            "686d0a1b2c3d4e5f00000002",
            "--name",
            "Renamed",
            "--public",
            "--max-count",
            "9",
        ],
        mcp=(
            "forms_surveys_update",
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
    # The filters of the listing (#196).
    Case(
        "forms.surveys.list",
        kwargs={
            "limit": 7,
            "name": "Onboarding",
            "published": True,
            "ownership": "mine",
            "group": "hr",
            "favourite": False,
            "show_all": True,
            "orderby": "name,-modified",
        },
        cli=[
            "forms",
            "surveys",
            "list",
            "--limit",
            "7",
            "--name",
            "Onboarding",
            "--published",
            "--ownership",
            "mine",
            "--group",
            "hr",
            "--no-favourite",
            "--show-all",
            "--orderby",
            "name,-modified",
        ],
        mcp=(
            "forms_surveys_list",
            {
                "limit": 7,
                "name": "Onboarding",
                "published": True,
                "ownership": "mine",
                "group": "hr",
                "favourite": False,
                "show_all": True,
                "orderby": "name,-modified",
            },
        ),
        exchanges=[
            (
                Sent(
                    "GET",
                    "surveys",
                    {
                        "offset": "0",
                        "limit": "100",
                        "name": "Onboarding",
                        "published": "true",
                        "ownership": "mine",
                        "group": "hr",
                        "favourite": "false",
                        "show_all": "true",
                        "orderby": "name,-modified",
                    },
                ),
                Reply(json={"result": [SURVEY]}),
            )
        ],
    ),
    # The settings a single form carries, as the API publishes them (#196).
    Case(
        "forms.surveys.get",
        args=("686d0a1b2c3d4e5f00000007",),
        cli=["forms", "surveys", "get", "686d0a1b2c3d4e5f00000007"],
        mcp=("forms_surveys_get", {"survey_id": "686d0a1b2c3d4e5f00000007"}),
        exchanges=[
            (
                Sent("GET", "surveys/686d0a1b2c3d4e5f00000007"),
                Reply(
                    json={
                        "id": "686d0a1b2c3d4e5f00000007",
                        "name": "Quiz",
                        "hashed_id": "686d0a1b2c3d4e5f00000007.abc",
                        "is_published": True,
                        "is_public": False,
                        "is_favourite": False,
                        "allow_multiple_answers": True,
                        "show_last_answer": False,
                        "need_auth": False,
                        "max_count": 100,
                        "metric": 9001,
                        "follow": "1h",
                        "captcha": "std",
                        "file_storage": "https://files.test/",
                        "validator_url": "https://check.test/",
                        "iframe": False,
                        "footer": True,
                        "teaser": True,
                        "stats": False,
                        "share": True,
                        "fill_again": True,
                        "texts": {"submit": "Send", "title": "Thanks"},
                        "styles": {
                            "id": 3,
                            "name": "Blue",
                            "type": "custom",
                            "custom": {"color": "#00f"},
                            "images": {"page": {"id": 41, "links": {}, "name": "bg.png"}},
                        },
                        "auto_publication": {
                            "enabled": True,
                            "date_open": "2026-10-01T00:00:00Z",
                            "date_close": "2026-12-31T00:00:00Z",
                        },
                        "quiz": {
                            "show_results": True,
                            "show_format": "score_with_total",
                            "show_correct": False,
                            "calc_method": "range",
                            "pass_scores": 5,
                            "question_count": 3,
                            "total_scores": 10,
                            "items": [{"title": "Passed", "upper_limit": 10}],
                        },
                        "followers": [
                            {"id": 4, "login": "ann", "email": "ann@example.com", "type": "user"},
                            {"id": "team@example.com", "type": "mail_list"},
                        ],
                        "author": {
                            "identity": {"uid": "9104", "cloud_uid": "cloud-9104"},
                            "username": "vera",
                            "display_name": "Vera",
                        },
                    }
                ),
            )
        ],
    ),
]
