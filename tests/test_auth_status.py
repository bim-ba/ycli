"""`ycli auth status` — env check + a real /myself probe, errors caught."""
from __future__ import annotations

import responses
from typer.testing import CliRunner

from ycli.cli import app

_URL = "https://api.tracker.yandex.net/v3/myself"
_RUNNER = CliRunner()


def test_auth_status_missing_env(monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    result = _RUNNER.invoke(app, ["auth", "status"])
    assert result.exit_code != 0
    assert "not configured" in result.stdout.lower() or "configured" in result.stdout.lower()


@responses.activate
def test_auth_status_valid(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")
    responses.add(responses.GET, _URL, json={"login": "alice", "display": "Alice", "uid": 1}, status=200)
    result = _RUNNER.invoke(app, ["auth", "status"])
    assert result.exit_code == 0
    assert "alice" in result.stdout


@responses.activate
def test_auth_status_invalid_token(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "bad")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")
    responses.add(responses.GET, _URL, json={"errorMessages": ["unauthorized"]}, status=401)
    result = _RUNNER.invoke(app, ["auth", "status"])
    assert result.exit_code != 0


@responses.activate
def test_auth_status_generic_error(monkeypatch):
    """Exercises the generic ``except YandexError`` branch (non-auth API error)."""
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")
    # 422 → YandexClientError (subclass of YandexError, not YandexAuthError)
    responses.add(responses.GET, _URL, json={"errorMessages": ["bad request"]}, status=422)
    result = _RUNNER.invoke(app, ["auth", "status"])
    assert result.exit_code != 0
    assert "configured" in result.stdout.lower()
