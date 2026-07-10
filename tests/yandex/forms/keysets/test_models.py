"""TDD for Forms keysets models (Keyset read + KeysetCreate/Update write bodies)."""

from ycli.yandex.forms.keysets.models import Keyset, KeysetCreate, KeysetList, KeysetUpdate


def test_keyset_parses_read_fields():
    ks = Keyset.model_validate({"id": 7, "name": "Q1", "total": 100, "used": 3, "is_enabled": True})
    assert ks.id == 7 and ks.total == 100 and ks.used == 3 and ks.is_enabled is True


def test_keyset_list_wraps_bare_array():
    out = KeysetList.model_validate([{"id": 7}, {"id": 8}])
    assert [k.id for k in out.root] == [7, 8]


def test_keyset_create_drops_unset_fields():
    body = KeysetCreate(name="Q1", total=250).model_dump(exclude_none=True)
    assert body == {"name": "Q1", "total": 250}  # is_enabled omitted


def test_keyset_update_is_partial_and_subclasses_create():
    body = KeysetUpdate(is_enabled=False).model_dump(exclude_none=True)
    assert body == {"is_enabled": False}
    assert issubclass(KeysetUpdate, KeysetCreate)
