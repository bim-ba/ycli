from ycli.yandex.models import APIModel


def test_apimodel_is_lenient_and_alias_friendly():
    cfg = APIModel.model_config
    assert cfg["extra"] == "ignore"
    assert cfg["populate_by_name"] is True
    # Runtime behaviour, not just the config dict: an unknown field is dropped, not an error.
    instance = APIModel.model_validate({"unknown_field": "dropped"})
    assert not hasattr(instance, "unknown_field")
