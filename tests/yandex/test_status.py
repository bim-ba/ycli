"""`ycli auth status` — probes Tracker, Wiki, Forms identity endpoints."""

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli as cli

TRACKER_ME = "https://api.tracker.yandex.net/v3/myself"
FORMS_ME = "https://api.forms.yandex.net/v1/users/me"
WIKI_ME = "https://api.wiki.yandex.net/v1/users/me"

runner = CliRunner()
pytestmark = pytest.mark.integration


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")


def test_missing_env_reports_not_configured(monkeypatch, tmp_path):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(cli.app, ["auth", "status"])
    assert res.exit_code == 1
    # error message goes to stderr; res.output is the combined terminal view
    assert "YANDEX_ID_OAUTH_TOKEN" in res.output


@responses.activate
def test_all_services_valid(creds):
    responses.add(
        responses.GET, TRACKER_ME, json={"login": "alice", "display": "Alice"}, status=200
    )
    responses.add(responses.GET, WIKI_ME, json={"username": "alice"}, status=200)
    responses.add(responses.GET, FORMS_ME, json={"email": "alice@x"}, status=200)
    res = runner.invoke(cli.app, ["--format", "json", "auth", "status"])
    assert res.exit_code == 0
    assert res.stdout.count('"valid":true') == 3


@responses.activate
def test_one_service_invalid_sets_nonzero_exit(creds):
    responses.add(responses.GET, TRACKER_ME, status=401)
    responses.add(responses.GET, WIKI_ME, json={"username": "alice"}, status=200)
    responses.add(responses.GET, FORMS_ME, json={"email": "alice@x"}, status=200)
    res = runner.invoke(cli.app, ["--format", "json", "auth", "status"])
    assert res.exit_code == 1
    assert "tracker" in res.stdout


@responses.activate
def test_tracker_generic_error(creds):
    """Exercises the generic YandexError branch for the tracker probe (e.g. 422)."""
    responses.add(responses.GET, TRACKER_ME, json={"errorMessages": ["bad"]}, status=422)
    responses.add(responses.GET, WIKI_ME, json={"username": "alice"}, status=200)
    responses.add(responses.GET, FORMS_ME, json={"email": "alice@x"}, status=200)
    res = runner.invoke(cli.app, ["--format", "json", "auth", "status"])
    assert res.exit_code == 1
    assert "tracker" in res.stdout
    assert '"valid":false' in res.stdout


@responses.activate
def test_forms_auth_error(creds):
    """Exercises the YandexAuthError branch for the forms probe (401)."""
    responses.add(
        responses.GET, TRACKER_ME, json={"login": "alice", "display": "Alice"}, status=200
    )
    responses.add(responses.GET, WIKI_ME, json={"username": "alice"}, status=200)
    responses.add(responses.GET, FORMS_ME, status=401)
    res = runner.invoke(cli.app, ["--format", "json", "auth", "status"])
    assert res.exit_code == 1
    assert "forms" in res.stdout


@responses.activate
def test_forms_generic_error(creds):
    """Exercises the generic YandexError branch for the forms probe (422)."""
    responses.add(
        responses.GET, TRACKER_ME, json={"login": "alice", "display": "Alice"}, status=200
    )
    responses.add(responses.GET, WIKI_ME, json={"username": "alice"}, status=200)
    responses.add(responses.GET, FORMS_ME, json={"errorMessages": ["bad"]}, status=422)
    res = runner.invoke(cli.app, ["--format", "json", "auth", "status"])
    assert res.exit_code == 1
    assert "forms" in res.stdout


@responses.activate
def test_wiki_auth_error(creds):
    """Exercises the YandexAuthError branch for the wiki probe (401)."""
    responses.add(
        responses.GET, TRACKER_ME, json={"login": "alice", "display": "Alice"}, status=200
    )
    responses.add(responses.GET, WIKI_ME, status=401)
    responses.add(responses.GET, FORMS_ME, json={"email": "alice@x"}, status=200)
    res = runner.invoke(cli.app, ["--format", "json", "auth", "status"])
    assert res.exit_code == 1
    assert "wiki" in res.stdout


@responses.activate
def test_wiki_generic_error(creds):
    """Exercises the generic YandexError branch for the wiki probe (422)."""
    responses.add(
        responses.GET, TRACKER_ME, json={"login": "alice", "display": "Alice"}, status=200
    )
    responses.add(responses.GET, WIKI_ME, json={"errorMessages": ["bad"]}, status=422)
    responses.add(responses.GET, FORMS_ME, json={"email": "alice@x"}, status=200)
    res = runner.invoke(cli.app, ["--format", "json", "auth", "status"])
    assert res.exit_code == 1
    assert "wiki" in res.stdout
