import pytest
from pydantic import ValidationError

from ycli.yandex.models import Ack, APIModel, DisplayStr, KeyStr, RequestBody, _extract


def test_a_reply_keeps_a_field_the_model_does_not_declare():
    cfg = APIModel.model_config
    assert cfg["extra"] == "allow"
    assert cfg["validate_by_name"] is True
    # Runtime behaviour, not just the config dict: a field Yandex adds shows up at once, untyped.
    instance = APIModel.model_validate({"brandNew": {"nested": 1}})
    assert instance.model_dump() == {"brandNew": {"nested": 1}}


def test_a_request_body_refuses_a_field_the_model_does_not_declare():
    class Rename(RequestBody):
        name: str

    assert RequestBody.model_config["extra"] == "forbid"
    with pytest.raises(ValidationError, match="nmae"):
        Rename.model_validate({"name": "Sprint", "nmae": "typo"})


def test_extract_pulls_field_from_wrapper_and_passes_scalars_through():
    pull = _extract("key")
    assert pull({"key": "x", "display": "X"}) == "x"  # wrapper → bare field
    assert pull("already-flat") == "already-flat"  # scalar passes through
    assert pull(None) is None  # None passes through
    assert _extract("display")({"display": "d"}) == "d"


def test_ref_annotations_accept_a_bare_scalar():
    from pydantic import TypeAdapter

    assert TypeAdapter(KeyStr).validate_python("flat") == "flat"
    assert TypeAdapter(DisplayStr).validate_python({"display": "d"}) == "d"


def test_ack_defaults_ok_true_and_detail_empty():
    ack = Ack()
    assert ack.ok is True and ack.detail == ""


def test_ack_deleted_bare():
    assert Ack.deleted("board", 5) == Ack(detail="deleted board 5")


def test_ack_deleted_with_on():
    assert Ack.deleted("column", 5, on="board 73") == Ack(detail="deleted column 5 on board 73")


def test_ack_deleted_with_from():
    assert Ack.deleted("macro", 3, from_="queue TEST") == Ack(
        detail="deleted macro 3 from queue TEST"
    )


def test_ack_published():
    assert Ack.published("survey", "686d") == Ack(detail="published survey 686d")


def test_ack_unpublished():
    assert Ack.unpublished("survey", "686d") == Ack(detail="unpublished survey 686d")


def test_ack_linked():
    assert Ack.linked("project", "655f", "658", "relates") == Ack(
        detail="linked project 655f -> 658 (relates)"
    )


def test_ack_unlinked():
    assert Ack.unlinked("project", "655f", "658") == Ack(detail="unlinked project 655f -> 658")


def test_ack_removed():
    assert Ack.removed("tag", "obsolete", from_="queue TEST") == Ack(
        detail="removed tag 'obsolete' from queue TEST"
    )


def test_ack_cleared():
    assert Ack.cleared("search scroll resources") == Ack(detail="cleared search scroll resources")
