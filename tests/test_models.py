from ycli.yandex.models import APIModel, DisplayStr, KeyStr, _extract


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
