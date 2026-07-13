from ycli.yandex.models import Ack, APIModel, DisplayStr, KeyStr, _extract


def test_apimodel_is_lenient_and_alias_friendly():
    cfg = APIModel.model_config
    assert cfg["extra"] == "ignore"
    assert cfg["populate_by_name"] is True
    # Runtime behaviour, not just the config dict: an unknown field is dropped, not an error.
    instance = APIModel.model_validate({"unknown_field": "dropped"})
    assert not hasattr(instance, "unknown_field")


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
