"""``ycli doctor``: each check passes, warns, fails or is skipped on its own, in order."""

import json
from importlib.metadata import version

import httpx2
import pytest
from pydantic import SecretStr
from typer.testing import CliRunner

from ycli.cli import app as cli
from ycli.cli.exit_codes import ExitCode
from ycli.settings import AppConfig, Credentials, credential_sources, proxy_variables
from ycli.yandex.status import doctor
from ycli.yandex.status.doctor import diagnose

ID_URL = "https://login.yandex.ru/info"
ORG_URL = "https://api360.yandex.net/directory/v1/org"
PROBES = {
    "tracker": "https://api.tracker.yandex.net/v3/myself",
    "wiki": "https://api.wiki.yandex.net/v1/users/me",
    "forms": "https://api.forms.yandex.net/v1/users/me",
}
CREDENTIALS = Credentials(oauth_token=SecretStr("y0_secret-value"), organization_id="42")
SOURCES = {"YANDEX_ID_OAUTH_TOKEN": "environment", "YANDEX_ID_ORGANIZATION_ID": ".env file"}
PYPI_URL = "https://pypi.org/pypi/yandex-cli/json"
INSTALLED = version("yandex-cli")
ANSWERS = {
    PYPI_URL: {"json": {"info": {"version": INSTALLED}}},
    ID_URL: {"json": {"id": "7", "login": "ivan"}},
    ORG_URL: {"json": {"organizations": [{"id": 42, "name": "Acme"}]}},
    **{url: {"json": {"login": "ivan"}} for url in PROBES.values()},
}
runner = CliRunner()


def _diagnose(api, proxies=(), **replaced):
    """The diagnosis with every read answering, except the URLs in ``replaced``."""
    for url, answer in ANSWERS.items():
        api.add("GET", url, **replaced.get(url, answer))
    report, exit_code = diagnose(CREDENTIALS, SOURCES, list(proxies), AppConfig())
    return {check.check: check for check in report.checks}, report, exit_code


def _unreachable(monkeypatch, api, url):
    """Answer like ``api``, but lose the connection for ``url``."""

    def handle(request: httpx2.Request) -> httpx2.Response:
        if str(request.url.copy_with(query=None)) == url:
            raise httpx2.ConnectError("connection refused", request=request)
        return api.handle(request)

    monkeypatch.setattr(
        "ycli.yandex.core.session.default_transport", lambda: httpx2.MockTransport(handle)
    )


def test_everything_in_order_is_all_ok_in_the_order_it_ran(api):
    checks, report, exit_code = _diagnose(api)
    assert (report.ok, exit_code) == (True, ExitCode.OK)
    assert list(checks) == [
        "credentials",
        "token",
        "organization",
        "service:tracker",
        "service:wiki",
        "service:forms",
        "extra:mcp",
        "extra:jq",
        "version",
    ]
    assert {check.status for check in report.checks} == {"ok"}
    assert checks["credentials"].detail == (
        "YANDEX_ID_OAUTH_TOKEN: environment; YANDEX_ID_ORGANIZATION_ID: .env file"
    )
    assert checks["token"].detail == "belongs to ivan"
    assert checks["organization"].detail == "Acme (42)"
    assert (
        "y0_secret-value" not in report.model_dump_json()
    )  # the token itself is never in the report


def test_without_credentials_nothing_else_is_tried(api):
    sources = dict.fromkeys(SOURCES, "not set")
    api.add("GET", PYPI_URL, **ANSWERS[PYPI_URL])
    report, exit_code = diagnose(None, sources, [], AppConfig())
    statuses = {check.check: check.status for check in report.checks}
    assert (report.ok, exit_code) == (False, ExitCode.AUTH)
    assert statuses["credentials"] == "fail"
    assert report.checks[0].fix == "run `ycli auth login`"
    skipped = ["token", "organization", "service:tracker", "service:wiki", "service:forms"]
    assert [statuses[name] for name in skipped] == ["skipped"] * 5
    assert [str(call.url) for call in api.calls] == [PYPI_URL]  # nothing went to Yandex


def test_a_token_yandex_id_rejects_fails_once_and_skips_the_rest(api):
    checks, report, exit_code = _diagnose(api, **{ID_URL: {"status": 401, "json": {}}})
    assert (report.ok, exit_code) == (False, ExitCode.AUTH)
    assert (checks["token"].status, checks["token"].fix) == ("fail", "run `ycli auth login`")
    assert checks["organization"].status == "skipped"
    assert checks["service:tracker"].detail == "the token was rejected"


def test_no_connection_names_the_proxy_variables_and_skips_the_rest(monkeypatch, api):
    _unreachable(monkeypatch, api, ID_URL)
    checks, _, exit_code = _diagnose(api, proxies=["HTTPS_PROXY"])
    assert exit_code is ExitCode.TRANSIENT
    assert checks["token"].status == "fail"
    assert checks["token"].detail.startswith("no connection: ")
    assert checks["token"].detail.endswith("; proxy variables set: HTTPS_PROXY")
    assert checks["service:forms"].status == "skipped"
    assert checks["version"].status == "skipped"  # no connection: PyPI is not asked either


def test_a_yandex_id_outage_is_a_warning_and_the_services_still_answer(api):
    checks, report, exit_code = _diagnose(api, **{ID_URL: {"status": 503, "json": {}}})
    assert (report.ok, exit_code) == (True, ExitCode.OK)
    assert checks["token"].status == "warn"
    assert checks["service:tracker"].status == "ok"


def test_an_organization_without_a_name_is_a_warning(api):
    checks, report, _ = _diagnose(api, **{ORG_URL: {"status": 403, "json": {}}})
    assert report.ok is True
    assert checks["organization"].status == "warn"
    assert "directory:read_organization" in checks["organization"].detail
    assert "YANDEX_ID_ORGANIZATION_ID" in (checks["organization"].fix or "")


def test_a_service_that_rejects_the_token_fails_and_the_others_still_run(api):
    checks, report, exit_code = _diagnose(api, **{PROBES["wiki"]: {"status": 403, "json": {}}})
    assert (report.ok, exit_code) == (False, ExitCode.AUTH)
    assert checks["service:wiki"].status == "fail"
    assert "wiki permissions" in (checks["service:wiki"].fix or "")
    assert (checks["service:tracker"].status, checks["service:forms"].status) == ("ok", "ok")


def test_the_exit_code_is_that_of_the_first_failure(api):
    replaced = {
        PROBES["tracker"]: {"status": 503, "json": {}},
        PROBES["wiki"]: {"status": 403, "json": {}},
    }
    checks, _, exit_code = _diagnose(api, **replaced)
    assert (checks["service:tracker"].status, checks["service:wiki"].status) == ("fail", "fail")
    assert exit_code is ExitCode.TRANSIENT


def test_a_service_outage_fails_with_its_own_exit_code(api):
    checks, _, exit_code = _diagnose(api, **{PROBES["forms"]: {"status": 503, "json": {}}})
    assert exit_code is ExitCode.TRANSIENT
    assert checks["service:forms"].status == "fail"
    assert "503" in checks["service:forms"].detail


def test_a_service_that_cannot_be_reached_skips_the_later_ones(monkeypatch, api):
    _unreachable(monkeypatch, api, PROBES["wiki"])
    checks, _, exit_code = _diagnose(api)
    assert exit_code is ExitCode.TRANSIENT
    assert checks["service:tracker"].status == "ok"
    assert checks["service:wiki"].detail.startswith("no connection: ")
    assert checks["service:forms"].status == "skipped"


def test_a_missing_extra_is_not_a_problem(monkeypatch, api):
    monkeypatch.setattr(doctor, "find_spec", lambda module: None)
    checks, report, _ = _diagnose(api)
    assert report.ok is True
    assert checks["extra:mcp"].status == "ok"
    assert checks["extra:mcp"].detail == "not installed: `yandex-cli[mcp]` adds the MCP server"


def test_a_newer_release_is_a_warning_with_the_upgrade_command(api):
    checks, report, exit_code = _diagnose(
        api, **{PYPI_URL: {"json": {"info": {"version": "999.0.0"}}}}
    )
    assert (report.ok, exit_code) == (True, ExitCode.OK)
    assert checks["version"].status == "warn"
    assert checks["version"].detail == f"{INSTALLED} is installed, 999.0.0 is out"
    assert checks["version"].fix == "`uv tool upgrade yandex-cli`"


def test_the_latest_release_is_ok(api):
    checks, _, _ = _diagnose(api)
    assert checks["version"].detail == f"{INSTALLED} is the latest release"


def test_a_silent_pypi_skips_the_version_check_and_breaks_nothing(api):
    checks, report, exit_code = _diagnose(api, **{PYPI_URL: {"status": 503, "json": {}}})
    assert (report.ok, exit_code) == (True, ExitCode.OK)
    assert checks["version"].status == "skipped"
    assert checks["version"].detail.startswith(f"{INSTALLED} is installed; PyPI did not answer")


def test_pypi_gets_no_credentials_and_no_organization(api):
    _diagnose(api)
    (request,) = [call for call in api.calls if str(call.url) == PYPI_URL]
    assert "authorization" not in request.headers
    assert not any(name.lower().startswith("x-") for name in request.headers)


def test_the_command_prints_the_report_and_exits_by_the_first_failure(monkeypatch, tmp_path, api):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    monkeypatch.chdir(tmp_path)
    api.add("GET", PYPI_URL, **ANSWERS[PYPI_URL])
    result = runner.invoke(cli.app, ["-o", "json", "doctor"])
    assert result.exit_code == 4
    report = json.loads(result.stdout)
    assert report["ok"] is False
    assert report["checks"][0]["detail"] == (
        "YANDEX_ID_OAUTH_TOKEN: not set; YANDEX_ID_ORGANIZATION_ID: not set"
    )


def test_the_command_exits_0_when_every_check_passes(creds, api):
    for url, answer in ANSWERS.items():
        api.add("GET", url, **answer)
    result = runner.invoke(cli.app, ["-o", "json", "doctor"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["ok"] is True


@pytest.mark.parametrize(
    ("environment", "file", "source"),
    [
        ({"YANDEX_ID_OAUTH_TOKEN": "t"}, "", "environment"),
        ({"YCLI__AUTH__OAUTH_TOKEN": "t"}, "", "environment"),
        ({}, "YANDEX_ID_OAUTH_TOKEN=t\n", ".env file"),
        ({"YANDEX_ID_OAUTH_TOKEN": ""}, "", "not set"),
        ({}, "", "not set"),
    ],
)
def test_a_credential_is_traced_to_the_environment_or_the_env_file(
    monkeypatch, tmp_path, environment, file, source
):
    monkeypatch.chdir(tmp_path)
    for name in ("YANDEX_ID_OAUTH_TOKEN", "YCLI__AUTH__OAUTH_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    for name, value in environment.items():
        monkeypatch.setenv(name, value)
    (tmp_path / ".env").write_text(file)
    assert credential_sources()["YANDEX_ID_OAUTH_TOKEN"] == source


def test_the_proxy_variables_are_named_in_either_case(monkeypatch):
    for name in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "NO_PROXY"):
        monkeypatch.delenv(name, raising=False)
        monkeypatch.delenv(name.lower(), raising=False)
    assert proxy_variables() == []
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy:3128")
    monkeypatch.setenv("no_proxy", "localhost")
    assert proxy_variables() == ["HTTPS_PROXY", "no_proxy"]
