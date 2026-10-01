"""Each service's ``me`` payload maps onto the shared Account shape used by ``auth status``."""

from ycli.yandex.account import Account
from ycli.yandex.forms.me.models import User as FormsMe
from ycli.yandex.tracker.me.models import Me as TrackerMe
from ycli.yandex.wiki.me.models import Me as WikiMe


def test_tracker_me_maps_numeric_uid_and_display_name():
    me = TrackerMe.model_validate({"uid": 42, "login": "alice", "display": "Alice", "email": "a@x"})
    assert me.account() == Account(uid="42", login="alice", email="a@x", display_name="Alice")


def test_tracker_me_without_uid():
    assert TrackerMe(login="alice").account().uid is None


def test_wiki_me_maps_username_and_identity_uid():
    me = WikiMe.model_validate({"username": "alice", "identity": {"uid": "u-1"}})
    assert me.account() == Account(uid="u-1", login="alice")
    assert WikiMe(username="bob").account() == Account(login="bob")


def test_forms_me_maps_uid_and_email():
    assert FormsMe(uid="u-2", email="a@x").account() == Account(uid="u-2", email="a@x")
