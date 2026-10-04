"""Model parsing for Tracker gaps: the doc replies and the request bodies."""

import pytest
from pydantic import ValidationError

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.gaps.models import (
    Gap,
    GapCreated,
    GapInput,
    GapsCreate,
    GapSearchPage,
    UserGaps,
)

USER = {
    "self": "https://api.tracker.yandex.net/v3/users/1234567890123456",
    "uid": 1234567890123456,
    "login": "username1",
    "trackerUid": 1234567890123456,
    "passportUid": 1234567890,
    "cloudUid": "ajehs6sinuiii1234567",
    "firstName": "Name",
    "lastName": "Surname",
    "display": "Ivan Ivanov",
    "email": "username@example.com",
    "external": False,
    "dismissed": False,
    "firstLoginDate": "2024-04-10T10:15:47.272+0000",
    "lastLoginDate": "2026-07-23T08:11:01.861+0000",
    "sources": ["directory"],
}


def test_create_reply_carries_the_whole_user_record():
    created = GapCreated.model_validate(
        {
            "gaps": [
                {
                    "id": "68340a1f2b4c1a3d5e7f9011",
                    "user": USER,
                    "workflow": "vacation",
                    "from": "2026-07-01T00:00:00.000+0000",
                    "to": "2026-07-15T00:00:00.000+0000",
                    "fullDay": True,
                    "workInAbsence": False,
                }
            ]
        }
    )
    gap = created.gaps[0]
    assert (
        gap.user is not None and gap.user.login == "username1" and gap.user.sources == ["directory"]
    )
    assert (gap.date_from, gap.date_to) == (
        "2026-07-01T00:00:00.000+0000",
        "2026-07-15T00:00:00.000+0000",
    )
    assert gap.full_day is True and gap.work_in_absence is False


def test_search_reply_groups_absences_by_user_and_flags_more_pages():
    page = GapSearchPage.model_validate(
        {
            "userGaps": [
                {"user": USER, "gaps": [{"id": "g1", "workflow": "vacation", "fullDay": True}]},
                {"user": {**USER, "login": "username2"}, "gaps": []},
            ],
            "hasMore": True,
        }
    )
    assert page.has_more is True
    assert page.user_gaps[0].gaps[0].user is None  # inside a search the gap has no user
    assert page.user_gaps[1].gaps == []
    assert ItemList[UserGaps](page.user_gaps).root[1].user is not None


def test_a_gap_without_optional_parts_parses():
    assert Gap.model_validate({"id": "g"}).full_day is None


def test_request_uses_the_api_names_and_accepts_the_docs_json():
    docs_json = {
        "user": "ann",
        "workflow": "trip",
        "from": "2026-07-10T00:00:00.000Z",
        "to": "2026-07-20T00:00:00.000Z",
        "fullDay": True,
    }
    gap = GapInput.model_validate(docs_json)
    assert gap.date_from.startswith("2026-07-10") and gap.workflow == "trip"
    assert GapsCreate(gaps=[gap]).model_dump(by_alias=True, exclude_none=True, mode="json") == {
        "gaps": [docs_json]
    }


def test_request_limits_hold():
    gap = {"user": "u", "workflow": "trip", "date_from": "a", "date_to": "b"}
    with pytest.raises(ValidationError):
        GapsCreate.model_validate({"gaps": [gap] * 101})
    with pytest.raises(ValidationError):
        GapInput.model_validate({**gap, "id": "x" * 129})
    assert GapInput.model_validate({**gap, "workflow": "holiday"}).workflow == "holiday"


def test_every_request_field_has_a_description():
    for model in (GapInput, GapsCreate, Gap):
        for name, field in model.model_fields.items():
            assert field.description, f"{model.__name__}.{name} is missing Field(description=…)"
