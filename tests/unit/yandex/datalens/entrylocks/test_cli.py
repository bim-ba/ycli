"""`datalens entrylocks`: what `-F` can and cannot stand for."""

import json

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli

CREATE = ["-o", "json", "--dry-run", "datalens", "entrylocks", "create", "ent1"]


@pytest.fixture(autouse=True)
def signed_in(monkeypatch):
    """DataLens takes an IAM token and a Yandex Cloud organization."""
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")


def test_a_field_adds_to_the_terms_the_option_gives(api):
    """Both sides: `-F` lays a field under `--data`; alone it does not replace the option."""
    both = CliRunner().invoke(
        cli.app, [*CREATE, "--data", '{"duration": 60000}', "-F", "data[force]=true"]
    )
    assert both.exit_code == 0, both.output
    assert json.loads(both.stdout)["body"]["data"] == {"duration": 60000, "force": True}
    alone = CliRunner().invoke(cli.app, [*CREATE, "-F", "data[duration]=60000"])
    assert alone.exit_code == 2
    assert "Missing option '--data'" in alone.output
    assert api.calls == []
