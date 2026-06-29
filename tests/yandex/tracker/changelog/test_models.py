"""Changelog ref fields flatten to bare scalars — populated and None branches."""

from ycli.yandex.tracker.changelog.models import ChangeField, ChangelogEntry


def test_field_flattens_to_scalar():
    assert ChangeField.model_validate({"field": {"id": "status"}}).field == "status"
    assert ChangeField.model_validate({}).field is None


def test_updated_by_flattens_to_scalar():
    assert ChangelogEntry.model_validate({"updatedBy": {"display": "X"}}).updated_by == "X"
    assert ChangelogEntry.model_validate({"id": "1"}).updated_by is None
