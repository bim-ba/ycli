"""Property accessors on the changelog models — populated and None branches."""

from ycli.yandex.tracker.changelog.models import ChangeField, ChangelogEntry


def test_field_id_populated_and_none():
    assert ChangeField.model_validate({"field": {"id": "status"}}).field == "status"
    assert ChangeField.model_validate({}).field is None


def test_author_display_populated_and_none():
    assert ChangelogEntry.model_validate({"updatedBy": {"display": "X"}}).updated_by == "X"
    assert ChangelogEntry.model_validate({"id": "1"}).updated_by is None
