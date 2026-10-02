"""`ycli auth status` and `ycli <service> auth status` — what the token owner, the organization
and each service's own probe say."""

import json

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli
from ycli.settings import missing_credentials

ID_URL = "https://login.yandex.ru/info"
ORG_URL = "https://api360.yandex.net/directory/v1/org"
PROBES = {
    "tracker": "https://api.tracker.yandex.net/v3/myself",
    "wiki": "https://api.wiki.yandex.net/v1/users/me",
    "forms": "https://api.forms.yandex.net/v1/users/me",
}

runner = CliRunner()


@pytest.fixture
def stubbed(api, monkeypatch):
    """Every read answers; a test replaces one by listing it in ``failing`` before the call."""
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "42")

    def stub(*, failing: dict[str, int] | None = None) -> None:
        failing = failing or {}
        answers = {
            ID_URL: {"json": {"id": "7", "login": "alice"}},
            ORG_URL: {"json": {"organizations": [{"id": 42, "name": "Acme"}]}},
            PROBES["tracker"]: {"json": {"login": "alice"}},
            PROBES["wiki"]: {"json": {"username": "alice"}},
            PROBES["forms"]: {"json": {"email": "alice@x"}},
        }
        for url, answer in answers.items():
            status = failing.get(url, 200)
            api.add(
                "GET",
                url,
                **({"json": {"message": "no"}} if status != 200 else answer),
                status=status,
            )

    return stub


def _no_credentials(monkeypatch, tmp_path):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    monkeypatch.chdir(tmp_path)


def test_missing_env_reports_not_configured(monkeypatch, tmp_path):
    _no_credentials(monkeypatch, tmp_path)
    res = runner.invoke(cli.app, ["--format", "json", "auth", "status"])
    assert res.exit_code == 1
    assert "YANDEX_ID_OAUTH_TOKEN" in res.stderr  # the variable is named on stderr
    assert json.loads(res.stdout) == {
        "configured": False,
        "identity": None,
        "organization": None,
        "services": [],
    }


def test_status_reports_the_owner_the_organization_and_every_service(stubbed):
    stubbed()
    res = runner.invoke(cli.app, ["--format", "json", "auth", "status"])
    assert res.exit_code == 0, res.output
    report = json.loads(res.stdout)
    assert report["identity"] == {
        "id": "7",
        "login": "alice",
        "display_name": None,
        "real_name": None,
        "default_email": None,
    }
    assert report["organization"] == {"id": "42", "name": "Acme", "detail": ""}
    assert [(s["service"], s["valid"]) for s in report["services"]] == [
        ("tracker", True),
        ("wiki", True),
        ("forms", True),
    ]


@pytest.mark.parametrize("service", PROBES)
@pytest.mark.parametrize("status", [401, 422])
def test_one_service_failing_sets_a_nonzero_exit_and_names_it(stubbed, service, status):
    stubbed(failing={PROBES[service]: status})
    res = runner.invoke(cli.app, ["--format", "json", "auth", "status"])
    assert res.exit_code == 1
    by_name = {s["service"]: s for s in json.loads(res.stdout)["services"]}
    assert by_name[service]["valid"] is False
    assert by_name[service]["detail"]
    assert all(s["valid"] for name, s in by_name.items() if name != service)


def test_a_token_without_the_directory_scope_is_still_a_success(stubbed):
    stubbed(failing={ORG_URL: 403})
    res = runner.invoke(cli.app, ["--format", "json", "auth", "status"])
    assert res.exit_code == 0, res.output
    organization = json.loads(res.stdout)["organization"]
    assert organization["id"] == "42"
    assert organization["name"] is None
    assert "directory:read_organization" in organization["detail"]


@pytest.mark.parametrize("service", PROBES)
def test_a_service_auth_status_probes_only_that_service(stubbed, api, service):
    stubbed()
    res = runner.invoke(cli.app, ["--format", "json", service, "auth", "status"])
    assert res.exit_code == 0, res.output
    assert json.loads(res.stdout) == {"service": service, "valid": True, "detail": ""}
    assert [str(call.url) for call in api.calls] == [PROBES[service]]


@pytest.mark.parametrize("service", PROBES)
def test_a_rejected_token_fails_that_services_auth_status(stubbed, service):
    stubbed(failing={PROBES[service]: 401})
    res = runner.invoke(cli.app, ["--format", "json", service, "auth", "status"])
    assert res.exit_code == 1
    assert json.loads(res.stdout) == {
        "service": service,
        "valid": False,
        "detail": "token invalid or expired",
    }


def test_a_service_auth_status_without_credentials_names_the_missing_variables(
    monkeypatch, tmp_path
):
    _no_credentials(monkeypatch, tmp_path)
    res = runner.invoke(cli.app, ["tracker", "auth", "status"])
    assert isinstance(res.exception, ValidationError)
    assert missing_credentials(res.exception) == [
        "YANDEX_ID_OAUTH_TOKEN",
        "YANDEX_ID_ORGANIZATION_ID",
    ]
