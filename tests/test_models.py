from ycli.models import APIModel


def test_apimodel_is_lenient_and_alias_friendly():
    cfg = APIModel.model_config
    assert cfg["extra"] == "ignore"
    assert cfg["populate_by_name"] is True
