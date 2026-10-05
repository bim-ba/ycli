"""`datalens collections`: where a command line cannot say what the request needs."""

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli


@pytest.fixture(autouse=True)
def signed_in(monkeypatch):
    """DataLens takes an IAM token and a Yandex Cloud organization."""
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")


def test_a_delta_that_is_not_json_is_refused_before_anything_is_sent(api):
    argv = ["datalens", "collections", "access-bindings-update", "col1", "--delta", "{oops"]
    result = CliRunner().invoke(cli.app, argv)
    assert isinstance(result.exception, ValidationError)
    assert api.calls == []
