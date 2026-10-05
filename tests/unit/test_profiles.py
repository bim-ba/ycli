"""Named profiles: one file per profile, the only source of credentials once one is named."""

import json
import logging
import os
import stat
import webbrowser

import pytest
from fastmcp.exceptions import ToolError
from typer.testing import CliRunner

import ycli.cli.app as cli
from ycli.cli.errors import exit_code_for, format_cli_error
from ycli.cli.exit_codes import ExitCode
from ycli.settings import (
    Credentials,
    ProfileError,
    active_profile,
    credential_sources,
    profile_names,
    profile_path,
)
from ycli.yandex.mcp import caller_credentials

ID_URL = "https://login.yandex.ru/info"
ORG_URL = "https://api360.yandex.net/directory/v1/org"
PROBES = (
    "https://api.tracker.yandex.net/v3/myself",
    "https://api.wiki.yandex.net/v1/users/me",
    "https://api.forms.yandex.net/v1/users/me",
)
PYPI_URL = "https://pypi.org/pypi/yandex-cli/json"
PROFILE_TOKEN = "y0_profile-secret-value_9876"

runner = CliRunner()


@pytest.fixture
def work(profiles_directory):
    """A saved profile ``work``: organization 7, while the environment says ``o``."""
    return _save(profiles_directory, "work", organization="7")


def _save(directory, name, *, organization="7", token_variable="YANDEX_ID_OAUTH_TOKEN"):
    directory.mkdir(parents=True, exist_ok=True)
    lines = [f"{token_variable}={PROFILE_TOKEN}"]
    if organization:
        lines.append(f"YANDEX_ID_ORGANIZATION_ID={organization}")
    path = directory / f"{name}.env"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _answer_everything(api):
    api.add("GET", ID_URL, json={"id": "7", "login": "ivan"})
    api.add("GET", ORG_URL, json={"organizations": [{"id": 7, "name": "Client"}]})
    for url in PROBES:
        api.add("GET", url, json={"login": "ivan"})


def test_a_named_profile_is_the_only_source_of_credentials(work, creds):
    credentials = Credentials.load("work")
    assert credentials.organization_id == "7"  # not the environment's "o"
    assert credentials.token.get_secret_value() == PROFILE_TOKEN
    assert (credentials.profile, credentials.kind) == ("work", "oauth")


def test_no_profile_named_reads_the_environment_as_before(work, creds):
    credentials = Credentials.load()
    assert (credentials.organization_id, credentials.profile) == ("o", None)


def test_the_variable_names_the_profile_and_the_option_wins(work, profiles_directory, monkeypatch):
    _save(profiles_directory, "client", organization="9")
    monkeypatch.setenv("YCLI_PROFILE", "client")
    assert active_profile() == "client"
    assert Credentials.load().organization_id == "9"
    assert Credentials.load("work").organization_id == "7"


def test_a_profile_missing_a_value_is_not_completed_from_the_environment(profiles_directory, creds):
    path = _save(profiles_directory, "half", organization="")
    with pytest.raises(ProfileError) as raised:
        Credentials.from_profile("half")
    assert str(raised.value) == (f"profile 'half' ({path}): YANDEX_ID_ORGANIZATION_ID is not set")


def test_a_profile_may_hold_an_iam_token(profiles_directory):
    _save(profiles_directory, "cloud", token_variable="YANDEX_CLOUD_IAM_TOKEN")
    assert Credentials.from_profile("cloud").kind == "iam"


def test_an_unknown_profile_names_the_saved_ones(work):
    with pytest.raises(
        ProfileError, match=r"profile 'nope' not found in .* \(saved profiles: work\)"
    ):
        Credentials.from_profile("nope")


def test_an_unknown_profile_with_none_saved_says_so():
    with pytest.raises(ProfileError, match=r"saved profiles: none"):
        Credentials.from_profile("nope")
    assert profile_names() == []


@pytest.mark.parametrize("name", ["../etc", "Work", "a/b", "", ".hidden", "a b"])
def test_a_profile_name_cannot_leave_the_directory(name):
    with pytest.raises(ProfileError, match="is not a profile name"):
        profile_path(name)


def test_the_sources_of_a_profile_name_it_and_nothing_else(work, profiles_directory, creds):
    assert credential_sources("work") == {
        "YANDEX_ID_OAUTH_TOKEN": "profile work",
        "YANDEX_ID_ORGANIZATION_ID": "profile work",
    }
    _save(profiles_directory, "cloud", organization="", token_variable="YANDEX_CLOUD_IAM_TOKEN")
    assert credential_sources("cloud") == {
        "YANDEX_CLOUD_IAM_TOKEN": "profile cloud",
        "YANDEX_ID_ORGANIZATION_ID": "not set",
    }
    assert credential_sources("../x") == {
        "YANDEX_ID_OAUTH_TOKEN": "not set",
        "YANDEX_ID_ORGANIZATION_ID": "not set",
    }


def test_a_profile_error_is_a_usage_error_with_its_own_message():
    error = ProfileError("profile 'x' not found")
    assert exit_code_for(error) is ExitCode.USAGE
    assert format_cli_error(error) == "Invalid configuration:\n  profile 'x' not found"


@pytest.mark.parametrize(
    "argv",
    [["--profile", "work", "tracker", "me", "get"], ["tracker", "me", "get", "--profile", "work"]],
)
def test_a_command_sends_the_profiles_token_and_organization(work, creds, api, argv):
    api.add("GET", PROBES[0], json={"login": "ivan"})
    result = runner.invoke(cli.app, ["-o", "json", *argv])
    assert result.exit_code == 0, result.output
    (request,) = api.calls
    assert request.headers["authorization"] == f"OAuth {PROFILE_TOKEN}"
    assert request.headers["x-org-id"] == "7"


def test_an_unknown_profile_stops_a_command_with_exit_code_2(creds, api):
    with pytest.raises(ProfileError):
        runner.invoke(
            cli.app, ["--profile", "nope", "tracker", "me", "get"], catch_exceptions=False
        )
    assert api.calls == []


def test_auth_status_names_the_active_profile(work, api):
    _answer_everything(api)
    result = runner.invoke(cli.app, ["-o", "json", "auth", "status", "--profile", "work"])
    assert result.exit_code == 0, result.output
    report = json.loads(result.stdout)
    assert (report["profile"], report["organization"]["id"]) == ("work", "7")
    assert PROFILE_TOKEN not in result.output


def test_auth_profiles_lists_them_without_a_token(work, profiles_directory, monkeypatch, caplog):
    _save(profiles_directory, "broken", organization="")
    _save(profiles_directory, "cloud", organization="9", token_variable="YANDEX_CLOUD_IAM_TOKEN")
    (profiles_directory / "work.env.bak").write_text("not a profile", encoding="utf-8")
    monkeypatch.setenv("YCLI_PROFILE", "cloud")
    with caplog.at_level(logging.DEBUG):
        result = runner.invoke(cli.app, ["-vv", "-o", "json", "auth", "profiles"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == [
        {
            "name": "broken",
            "organization_id": None,
            "organization_kind": None,
            "credential": None,
            "active": False,
        },
        {
            "name": "cloud",
            "organization_id": "9",
            "organization_kind": "360",
            "credential": "iam",
            "active": True,
        },
        {
            "name": "work",
            "organization_id": "7",
            "organization_kind": "360",
            "credential": "oauth",
            "active": False,
        },
    ]
    assert PROFILE_TOKEN not in result.output
    assert PROFILE_TOKEN not in caplog.text


def test_a_profiles_token_reaches_no_log(work, api, caplog):
    _answer_everything(api)
    with caplog.at_level(logging.DEBUG):
        result = runner.invoke(cli.app, ["-vv", "--profile", "work", "auth", "status"])
    assert result.exit_code == 0, result.output
    assert caplog.text  # the requests were logged
    assert PROFILE_TOKEN not in caplog.text
    assert PROFILE_TOKEN not in result.output


def test_doctor_names_the_profile_and_the_directory(work, profiles_directory, api):
    _answer_everything(api)
    api.add("GET", PYPI_URL, json={"info": {"version": "0.0.1"}})
    result = runner.invoke(cli.app, ["-o", "json", "--profile", "work", "doctor"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["checks"][0]["detail"] == (
        "YANDEX_ID_OAUTH_TOKEN: profile work; YANDEX_ID_ORGANIZATION_ID: profile work; "
        f"profile: work; profiles directory: {profiles_directory}"
    )
    assert PROFILE_TOKEN not in result.output


def test_doctor_reports_a_profile_that_cannot_be_used(creds, api):
    api.add("GET", PYPI_URL, json={"info": {"version": "0.0.1"}})
    result = runner.invoke(cli.app, ["-o", "json", "--profile", "nope", "doctor"])
    assert result.exit_code == ExitCode.USAGE
    first = json.loads(result.stdout)["checks"][0]
    assert (first["status"], first["fix"].startswith("profile 'nope' not found")) == ("fail", True)


def _sign_in(monkeypatch, api, tmp_path):
    """A device-flow login that succeeds, run from an empty directory."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    monkeypatch.setattr(webbrowser, "open", lambda *args, **kwargs: False)
    api.add(
        "POST",
        "https://oauth.yandex.ru/device/code",
        json={
            "device_code": "dev-123",
            "user_code": "ABCD-EFGH",
            "verification_url": "https://ya.ru/device",
            "expires_in": 300,
            "interval": 5,
        },
    )
    api.add("POST", "https://oauth.yandex.ru/token", json={"access_token": PROFILE_TOKEN})
    _answer_everything(api)


def _mode(path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


@pytest.mark.skipif(os.name == "nt", reason="Windows does not enforce POSIX modes")
def test_login_saves_a_profile_owner_only(monkeypatch, api, tmp_path, profiles_directory):
    _sign_in(monkeypatch, api, tmp_path)
    old_umask = os.umask(0o022)  # a permissive umask must not widen either mode
    try:
        result = runner.invoke(cli.app, ["auth", "login", "--yes", "--profile", "client"])
    finally:
        os.umask(old_umask)
    assert result.exit_code == 0, result.output
    saved = profiles_directory / "client.env"
    assert (_mode(saved), _mode(profiles_directory)) == (0o600, 0o700)
    assert not (tmp_path / ".env").exists()
    assert PROFILE_TOKEN not in result.output
    credentials = Credentials.from_profile("client")
    assert (credentials.organization_id, credentials.token.get_secret_value()) == (
        "7",
        PROFILE_TOKEN,
    )


def test_login_over_a_saved_profile_backs_it_up_owner_only(
    monkeypatch, api, tmp_path, work, profiles_directory
):
    _sign_in(monkeypatch, api, tmp_path)
    work.chmod(0o644)
    result = runner.invoke(cli.app, ["--profile", "work", "auth", "login", "--yes"])
    assert result.exit_code == 0, result.output
    assert "Backed up existing work.env" in result.output
    assert (_mode(work), _mode(profiles_directory / "work.env.bak")) == (0o600, 0o600)
    assert profile_names() == ["work"]  # the backup is not a profile


def test_login_refuses_a_bad_profile_name_before_signing_in(monkeypatch, api, tmp_path):
    _sign_in(monkeypatch, api, tmp_path)
    with pytest.raises(ProfileError, match="is not a profile name"):
        runner.invoke(cli.app, ["auth", "login", "--profile", "../x"], catch_exceptions=False)
    assert api.calls == []


def test_the_mcp_provider_reads_the_active_profile_on_each_call(work, creds, monkeypatch):
    monkeypatch.setenv("YCLI_PROFILE", "work")
    assert caller_credentials().organization_id == "7"
    work.write_text(work.read_text().replace("=7", "=8"), encoding="utf-8")
    assert caller_credentials().organization_id == "8"


def test_the_mcp_provider_names_a_profile_that_cannot_be_used(monkeypatch):
    monkeypatch.setenv("YCLI_PROFILE", "nope")
    with pytest.raises(ToolError, match="Invalid configuration: profile 'nope' not found"):
        caller_credentials()


def test_mcp_start_hands_the_profile_to_its_providers(work, creds, monkeypatch):
    monkeypatch.setenv("YCLI_PROFILE", "other")  # restored after the test
    served = []
    monkeypatch.setattr(
        "ycli.mcp.server.main", lambda selection: served.append(os.environ["YCLI_PROFILE"])
    )
    result = runner.invoke(cli.app, ["mcp", "start", "--profile", "work"])
    assert result.exit_code == 0, result.output
    assert served == ["work"]
    assert caller_credentials().organization_id == "7"


def test_mcp_start_over_http_refuses_a_profile(work):
    result = runner.invoke(cli.app, ["mcp", "start", "--transport", "http", "--profile", "work"])
    assert result.exit_code == 2
    assert "--profile" in result.output
    assert "every caller signs in" in result.output
