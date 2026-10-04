"""Wiki page access models — the shapes the live API returned, and the bodies sent to it."""

from ycli.yandex.wiki.access.models import (
    PageAccess,
    PageAccessCreate,
    PageAccessLists,
    PageAccessPolicy,
    PageAccessUpdate,
    PageOwner,
)

USER = {
    "id": 39185659,
    "identity": {"uid": "9001", "cloud_uid": None},
    "username": "robot",
    "display_name": "Robot",
    "is_dismissed": False,
    "affiliation": "",
}


def test_a_user_grant_parses_as_the_api_prints_it():
    grant = PageAccess.model_validate(
        {
            "id": "48723431",
            "created_at": "2026-10-02T17:11:10.778Z",
            "user": USER,
            "group": None,
            "role": "reader",
            "inheritance": "not_inherited",
        }
    )
    assert grant.id == "48723431" and grant.role == "reader"
    assert grant.user is not None and grant.user.identity is not None
    assert grant.user.identity.uid == "9001" and grant.user.username == "robot"


def test_a_group_grant_parses_with_its_directory_identity():
    grant = PageAccess.model_validate(
        {
            "id": "7",
            "role": "editor",
            "group": {
                "id": "42",
                "identity": {"src": "staff", "id": "42"},
                "name": "Docs",
                "type": "department",
                "metadata": {"url": "https://staff.example/docs", "externals_count": 2},
                "members_count": 12,
            },
        }
    )
    assert grant.group is not None and grant.group.identity is not None
    assert (grant.group.identity.src, grant.group.members_count) == ("staff", 12)


def test_the_policy_and_lists_parse_as_page_fields_return_them():
    policy = PageAccessPolicy.model_validate(
        {
            "access_type": "all_staff",
            "inherited_access_type": None,
            "all_staff_role": "reader",
            "has_external": None,
            "invite": None,
        }
    )
    lists = PageAccessLists.model_validate(
        {"direct": [{"id": "1", "role": "author", "user": USER}], "by_link": [], "inherited": []}
    )
    assert policy.all_staff_role == "reader"
    assert [grant.role for grant in lists.direct] == ["author"]


def test_an_owner_without_a_user_is_allowed():
    assert PageOwner.model_validate({"user": None, "group": None}).user is None


def test_a_create_body_is_kept_with_both_grantees_or_none():
    body = PageAccessCreate.model_validate({"user": {"uid": "1"}, "role": "reader"})
    assert body.model_dump(exclude_none=True) == {"user": {"uid": "1"}, "role": "reader"}
    both = {"user": {"uid": "1"}, "group": {"src": "dir", "id": "2"}, "role": "reader"}
    assert PageAccessCreate.model_validate(both).model_dump(exclude_none=True) == both
    assert PageAccessCreate.model_validate({"role": "reader"}).model_dump(exclude_none=True) == {
        "role": "reader"
    }


def test_an_update_body_with_nothing_to_change_is_kept_empty():
    assert PageAccessUpdate(inheritance="inherited").model_dump(exclude_none=True) == {
        "inheritance": "inherited"
    }
    assert PageAccessUpdate().model_dump(exclude_none=True) == {}


def test_a_role_outside_the_known_set_is_kept():
    body = PageAccessCreate.model_validate({"user": {"uid": "1"}, "role": "admin"})
    assert body.role == "admin"
