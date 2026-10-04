"""Forms access models parse what the live API returns and shape the write bodies."""

from ycli.yandex.forms.access.models import (
    AccessGrant,
    AccessRevoke,
    AccessUpdate,
    GroupIdentity,
    Permission,
)
from ycli.yandex.forms.models import UserIdentity
from ycli.yandex.models import ItemList

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
    change, submit = ItemList[Permission].model_validate(LIVE).root
    assert change.users and change.users[0].identity and change.users[0].identity.uid == "101523906"
    assert submit.access == "common" and submit.users is None


def test_access_update_keeps_a_level_outside_the_known_set():
    body = AccessUpdate.model_validate({"action": "change", "access": "everyone"})
    assert body.access == "everyone"


def test_grant_and_revoke_drop_the_principal_not_given():
    grant = AccessGrant(action="change", user=UserIdentity(uid="7"))
    revoke = AccessRevoke(action="submit", group=GroupIdentity(src="dir", id="5"))
    assert grant.model_dump(exclude_none=True) == {"action": "change", "user": {"uid": "7"}}
    assert revoke.model_dump(exclude_none=True) == {
        "action": "submit",
        "group": {"src": "dir", "id": "5"},
    }
