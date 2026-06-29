"""Property accessors on the changelog models — populated and None branches."""

from ycli.yandex.tracker.changelog.models import ChangeField, ChangelogEntry


def test_field_id_populated_and_none():
    assert ChangeField.model_validate({"field": {"id": "status"}}).field_id == "status"
    assert ChangeField.model_validate({}).field_id is None


def test_author_display_populated_and_none():
    assert ChangelogEntry.model_validate({"updatedBy": {"display": "X"}}).author_display == "X"
    assert ChangelogEntry.model_validate({"id": "1"}).author_display is None
