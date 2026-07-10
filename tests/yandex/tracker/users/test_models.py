"""Model-parse + Field-metadata coverage for the Tracker users models."""

from ycli.yandex.tracker.users.models import Group, User, UserList, UsersRelativeResponse

_FULL = {
    "self": "https://api.tracker.yandex.net/v3/users/12",
    "uid": 12,
    "login": "username",
    "trackerUid": 13,
    "passportUid": 14,
    "cloudUid": "bfbdrb1aa248",
    "firstName": "Имя",
    "lastName": "Фамилия",
    "display": "Имя Фамилия",
    "email": "mail@example.com",
    "groups": [{"self": "u", "id": "5", "display": "Developers"}],
    "external": False,
    "hasLicense": True,
    "dismissed": False,
    "useNewFilters": True,
    "disableNotifications": False,
    "firstLoginDate": "2020-10-27T13:06:21.787+0000",
    "lastLoginDate": "2022-07-25T17:12:33.787+0000",
    "welcomeMailSent": True,
    "sources": ["directory"],
    "position": "Engineer",
}


def test_user_parses_every_aliased_field():
    u = User.model_validate(_FULL)
    assert u.self_url == "https://api.tracker.yandex.net/v3/users/12"
    assert u.uid == 12 and u.tracker_uid == 13 and u.passport_uid == 14
    assert u.cloud_uid == "bfbdrb1aa248"
    assert u.first_name == "Имя" and u.last_name == "Фамилия"
    assert u.has_license is True and u.dismissed is False
    assert u.use_new_filters is True and u.disable_notifications is False
    assert u.first_login_date is not None and u.last_login_date is not None
    assert u.first_login_date.endswith("+0000")
    assert u.last_login_date.endswith("+0000")
    assert u.welcome_mail_sent is True and u.sources == ["directory"]
    assert u.position == "Engineer"
    assert u.groups[0].id == "5" and u.groups[0].display == "Developers"


def test_group_parses_self_alias():
    g = Group.model_validate({"self": "https://x/groups/5", "id": "5", "display": "Devs"})
    assert g.self_url == "https://x/groups/5" and g.id == "5" and g.display == "Devs"


def test_userlist_is_flat_root_array():
    ul = UserList.model_validate([{"login": "a"}, {"login": "b"}])
    assert [u.login for u in ul.root] == ["a", "b"]


def test_relative_response_envelope():
    env = UsersRelativeResponse.model_validate({"users": [{"uid": 1}], "hasNext": True})
    assert env.has_next is True and env.users[0].uid == 1


def test_every_user_field_has_description():
    for name, field in User.model_fields.items():
        assert field.description, f"User.{name} is missing Field(description=…)"
    for name, field in Group.model_fields.items():
        assert field.description, f"Group.{name} is missing Field(description=…)"
    for name, field in UsersRelativeResponse.model_fields.items():
        assert field.description, f"UsersRelativeResponse.{name} is missing Field(description=…)"
