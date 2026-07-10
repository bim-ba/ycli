"""`ycli auth login` — hybrid device/implicit OAuth flow, org resolution, .env write."""

import webbrowser

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

DEVICE_CODE_URL = "https://oauth.yandex.ru/device/code"
TOKEN_URL = "https://oauth.yandex.ru/token"
ORG_URL = "https://api360.yandex.net/directory/v1/org"
TRACKER_ME = "https://api.tracker.yandex.net/v3/myself"
FORMS_ME = "https://api.forms.yandex.net/v1/users/me"
WIKI_ME = "https://api.wiki.yandex.net/v1/users/me"

TOKEN = "y0_AgAAAABsecret_TOKEN_value_1234"

runner = CliRunner()
pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def _isolated_env(monkeypatch, tmp_path):
    """No repo .env, no real credentials, no browser launch."""
    monkeypatch.chdir(tmp_path)
    for var in (
        "YANDEX_OAUTH_CLIENT_ID",
        "YANDEX_OAUTH_CLIENT_SECRET",
        "YANDEX_ID_OAUTH_TOKEN",
        "YANDEX_ID_ORGANIZATION_ID",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(webbrowser, "open", lambda *args, **kwargs: False)
    monkeypatch.setattr("time.sleep", lambda seconds: None)
    return tmp_path


def _stub_device_code():
    responses.add(
        responses.POST,
        DEVICE_CODE_URL,
        json={
            "device_code": "dev-123",
            "user_code": "ABCD-EFGH",
            "verification_url": "https://ya.ru/device",
            "expires_in": 300,
            "interval": 5,
        },
        status=200,
    )


def _stub_token_success():
    responses.add(responses.POST, TOKEN_URL, json={"access_token": TOKEN}, status=200)


def _stub_single_org():
    responses.add(
        responses.GET, ORG_URL, json={"organizations": [{"id": 42, "name": "Acme"}]}, status=200
    )


def _stub_valid_me():
    responses.add(responses.GET, TRACKER_ME, json={"login": "alice"}, status=200)
    responses.add(responses.GET, WIKI_ME, json={"username": "alice"}, status=200)
    responses.add(responses.GET, FORMS_ME, json={"email": "alice@x"}, status=200)


def test_no_client_id_prints_guidance(monkeypatch):
    res = runner.invoke(cli.app, ["auth", "login"])
    assert res.exit_code == 1
    assert "YANDEX_OAUTH_CLIENT_ID" in res.output
    assert "https://oauth.yandex.ru" in res.output


@responses.activate
def test_device_flow_success_writes_env(monkeypatch, tmp_path):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code()
    _stub_token_success()
    _stub_single_org()
    _stub_valid_me()

    res = runner.invoke(cli.app, ["--format", "json", "auth", "login", "--yes"])

    assert res.exit_code == 0, res.output
    assert TOKEN not in res.output  # never echo the full token
    assert "...1234" in res.output  # masked fingerprint
    env_content = (tmp_path / ".env").read_text(encoding="utf-8")
    assert f"YANDEX_ID_OAUTH_TOKEN={TOKEN}" in env_content
    assert "YANDEX_ID_ORGANIZATION_ID=42" in env_content


@responses.activate
def test_device_flow_with_device_name(monkeypatch):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code()
    _stub_token_success()
    _stub_single_org()
    _stub_valid_me()

    res = runner.invoke(cli.app, ["auth", "login", "--yes", "--device-name", "my-laptop"])

    assert res.exit_code == 0, res.output
    assert "device_name=my-laptop" in str(responses.calls[0].request.body)


@responses.activate
def test_device_flow_pending_then_success(monkeypatch):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code()
    responses.add(responses.POST, TOKEN_URL, json={"error": "authorization_pending"}, status=400)
    _stub_token_success()  # second poll succeeds
    _stub_single_org()
    _stub_valid_me()

    res = runner.invoke(cli.app, ["auth", "login", "--yes"])

    assert res.exit_code == 0, res.output


@pytest.mark.parametrize("error", ["invalid_client", "expired_token", "access_denied"])
@responses.activate
def test_device_flow_terminal_error(monkeypatch, error):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code()
    responses.add(responses.POST, TOKEN_URL, json={"error": error}, status=400)

    res = runner.invoke(cli.app, ["auth", "login", "--yes"])

    assert res.exit_code == 1
    assert error in res.output


@responses.activate
def test_implicit_flow_when_secret_absent(monkeypatch, tmp_path):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")  # no secret -> implicit
    _stub_single_org()
    _stub_valid_me()

    res = runner.invoke(cli.app, ["auth", "login", "--yes"], input=f"{TOKEN}\n")

    assert res.exit_code == 0, res.output
    env_content = (tmp_path / ".env").read_text(encoding="utf-8")
    assert f"YANDEX_ID_OAUTH_TOKEN={TOKEN}" in env_content


@responses.activate
def test_implicit_flag_overrides_device(monkeypatch, tmp_path):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv(
        "YANDEX_OAUTH_CLIENT_SECRET", "app-secret"
    )  # secret set, but --implicit wins
    _stub_single_org()
    _stub_valid_me()

    res = runner.invoke(cli.app, ["auth", "login", "--yes", "--implicit"], input=f"{TOKEN}\n")

    assert res.exit_code == 0, res.output


@responses.activate
def test_multiple_orgs_prompts_for_choice(monkeypatch, tmp_path):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code()
    _stub_token_success()
    responses.add(
        responses.GET,
        ORG_URL,
        json={"organizations": [{"id": 42, "name": "Acme"}, {"id": 43, "name": "Beta"}]},
        status=200,
    )
    _stub_valid_me()

    res = runner.invoke(cli.app, ["auth", "login", "--yes"], input="2\n")

    assert res.exit_code == 0, res.output
    env_content = (tmp_path / ".env").read_text(encoding="utf-8")
    assert "YANDEX_ID_ORGANIZATION_ID=43" in env_content


@responses.activate
def test_org_fallback_prompt_on_missing_scope(monkeypatch, tmp_path):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code()
    _stub_token_success()
    responses.add(responses.GET, ORG_URL, status=403)
    _stub_valid_me()

    res = runner.invoke(cli.app, ["auth", "login", "--yes"], input="manual-org-99\n")

    assert res.exit_code == 0, res.output
    assert "tracker.yandex.ru/admin/orgs" in res.output
    env_content = (tmp_path / ".env").read_text(encoding="utf-8")
    assert "YANDEX_ID_ORGANIZATION_ID=manual-org-99" in env_content


@responses.activate
def test_confirm_declined_skips_write(monkeypatch, tmp_path):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code()
    _stub_token_success()
    _stub_single_org()
    _stub_valid_me()

    res = runner.invoke(cli.app, ["auth", "login"], input="n\n")

    assert res.exit_code == 0, res.output
    assert not (tmp_path / ".env").exists()


@responses.activate
def test_confirm_accepted_writes(monkeypatch, tmp_path):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code()
    _stub_token_success()
    _stub_single_org()
    _stub_valid_me()

    res = runner.invoke(cli.app, ["auth", "login"], input="y\n")

    assert res.exit_code == 0, res.output
    assert (tmp_path / ".env").exists()


@responses.activate
def test_backup_existing_env(monkeypatch, tmp_path):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    (tmp_path / ".env").write_text("KEEP=me\nYANDEX_ID_OAUTH_TOKEN=old\n", encoding="utf-8")
    _stub_device_code()
    _stub_token_success()
    _stub_single_org()
    _stub_valid_me()

    res = runner.invoke(cli.app, ["auth", "login", "--yes"])

    assert res.exit_code == 0, res.output
    assert (tmp_path / ".env.bak").read_text(
        encoding="utf-8"
    ) == "KEEP=me\nYANDEX_ID_OAUTH_TOKEN=old\n"
    env_content = (tmp_path / ".env").read_text(encoding="utf-8")
    assert "KEEP=me" in env_content
    assert f"YANDEX_ID_OAUTH_TOKEN={TOKEN}" in env_content
    assert "YANDEX_ID_OAUTH_TOKEN=old" not in env_content
