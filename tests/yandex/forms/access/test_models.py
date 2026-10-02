"""Forms access models parse what the live API returns and shape the write bodies."""

import pytest
from pydantic import ValidationError

from ycli.yandex.forms.access.models import (
    AccessGrant,
    AccessRevoke,
    AccessUpdate,
    GroupIdentity,
    PermissionList,
    UserIdentity,
)

# As GET /surveys/{id}/access answered on the test organization (2026-10-02).
LIVE = [
    {
        "access": "restricted",
        "action": "change",
        "users": [
            {
                "identity": {"uid": "101523906", "cloud_uid": "ajen8nffceu4rqs0i39r"},
                "username": "znatnov-sava",
                "display_name": "Сава Знатнов",
            }
        ],
    },
    {"access": "common", "action": "submit"},
]


def test_permissions_parse_live_answer():
    change, submit = PermissionList.model_validate(LIVE).root
    assert change.users and change.users[0].identity and change.users[0].identity.uid == "101523906"
    assert submit.access == "common" and submit.users is None


def test_access_update_refuses_an_unknown_level():
    with pytest.raises(ValidationError):
        AccessUpdate.model_validate({"action": "change", "access": "everyone"})


def test_grant_and_revoke_drop_the_principal_not_given():
    grant = AccessGrant(action="change", user=UserIdentity(uid="7"))
    revoke = AccessRevoke(action="submit", group=GroupIdentity(src="dir", id="5"))
    assert grant.model_dump(exclude_none=True) == {"action": "change", "user": {"uid": "7"}}
    assert revoke.model_dump(exclude_none=True) == {
        "action": "submit",
        "group": {"src": "dir", "id": "5"},
    }
