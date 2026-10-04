"""`ycli auth login` — hybrid device/implicit OAuth flow, org resolution, .env write."""

import os
import webbrowser
from io import StringIO
from types import SimpleNamespace

import pytest
from rich.console import Console
from rich.live import Live
from typer.testing import CliRunner

import ycli.cli.app as cli
from ycli.yandex.errors import YandexServerError
from ycli.yandex.status.cli import _device_flow, _suppressed_stderr
from ycli.yandex.status.client import OAuthClient, TokenPollResult
from ycli.yandex.status.oauth_models import TokenResponse

DEVICE_CODE_URL = "https://oauth.yandex.ru/device/code"
TOKEN_URL = "https://oauth.yandex.ru/token"
ORG_URL = "https://api360.yandex.net/directory/v1/org"
ID_URL = "https://login.yandex.ru/info"
TRACKER_ME = "https://api.tracker.yandex.net/v3/myself"
FORMS_ME = "https://api.forms.yandex.net/v1/users/me"
WIKI_ME = "https://api.wiki.yandex.net/v1/users/me"

TOKEN = "y0_AgAAAABsecret_TOKEN_value_1234"

runner = CliRunner()


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


def _stub_device_code(api):
    api.add(
        "POST",
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


@pytest.fixture(autouse=True)
def _core_probes(api):
    """Everything but Wiki runs on the httpx2 core, so ``api`` answers it in every login."""
    api.add("GET", ID_URL, json={"id": "7", "login": "alice"})
    api.add("GET", FORMS_ME, json={"email": "alice@x"})
    api.add("GET", TRACKER_ME, json={"login": "alice"})


def _stub_token_success(api):
    api.add("POST", TOKEN_URL, json={"access_token": TOKEN}, status=200)


def _stub_single_org(api):
    api.add("GET", ORG_URL, json={"organizations": [{"id": 42, "name": "Acme"}]}, status=200)


def _stub_valid_me(api):
    api.add("GET", WIKI_ME, json={"username": "alice"}, status=200)


def test_no_client_id_prints_guidance(monkeypatch):
    res = runner.invoke(cli.app, ["auth", "login"])
    assert res.exit_code == 1
    assert "YANDEX_OAUTH_CLIENT_ID" in res.output
    assert "https://oauth.yandex.ru" in res.output


def test_device_flow_success_writes_env(monkeypatch, tmp_path, api):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code(api)
    _stub_token_success(api)
    _stub_single_org(api)
    _stub_valid_me(api)

    res = runner.invoke(cli.app, ["--format", "json", "auth", "login", "--yes"])

    assert res.exit_code == 0, res.output
    assert '"login":"alice"' in res.stdout  # the owner, from Yandex ID
    assert '"name":"Acme"' in res.stdout  # the organization, from API 360
    assert TOKEN not in res.output  # never echo the full token
    assert "...1234" in res.output  # masked fingerprint
    env_content = (tmp_path / ".env").read_text(encoding="utf-8")
    assert f"YANDEX_ID_OAUTH_TOKEN={TOKEN}" in env_content
    assert "YANDEX_ID_ORGANIZATION_ID=42" in env_content


def test_device_flow_with_device_name(monkeypatch, api):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code(api)
    _stub_token_success(api)
    _stub_single_org(api)
    _stub_valid_me(api)

    res = runner.invoke(cli.app, ["auth", "login", "--yes", "--device-name", "my-laptop"])

    assert res.exit_code == 0, res.output
    assert "device_name=my-laptop" in api.calls[0].content.decode()


def test_device_flow_pending_then_success(monkeypatch, api):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code(api)
    api.add("POST", TOKEN_URL, json={"error": "authorization_pending"}, status=400)
    _stub_token_success(api)  # second poll succeeds
    _stub_single_org(api)
    _stub_valid_me(api)

    res = runner.invoke(cli.app, ["auth", "login", "--yes"])

    assert res.exit_code == 0, res.output


def test_device_flow_stops_when_the_code_expires(monkeypatch, api):
    """The server may answer ``authorization_pending`` for ever; the code's lifetime ends it."""
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code(api)  # expires_in 300, interval 5
    api.add("POST", TOKEN_URL, json={"error": "authorization_pending"}, status=400)
    clock = iter(range(0, 10_000, 100))
    monkeypatch.setattr("time.monotonic", lambda: next(clock))

    res = runner.invoke(cli.app, ["auth", "login", "--yes"])

    assert res.exit_code == 1
    assert "The code expired" in res.output
    polls = [call for call in api.calls if str(call.url) == TOKEN_URL]
    assert len(polls) == 3  # at 100, 200 and 300 seconds; the deadline was set at 0


@pytest.mark.parametrize("error", ["invalid_client", "expired_token", "access_denied"])
def test_device_flow_terminal_error(api, monkeypatch, error):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code(api)
    api.add("POST", TOKEN_URL, json={"error": error}, status=400)

    res = runner.invoke(cli.app, ["auth", "login", "--yes"])

    assert res.exit_code == 1
    assert error in res.output


def test_implicit_flow_when_secret_absent(monkeypatch, tmp_path, api):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")  # no secret -> implicit
    _stub_single_org(api)
    _stub_valid_me(api)

    res = runner.invoke(cli.app, ["auth", "login", "--yes"], input=f"{TOKEN}\n")

    assert res.exit_code == 0, res.output
    env_content = (tmp_path / ".env").read_text(encoding="utf-8")
    assert f"YANDEX_ID_OAUTH_TOKEN={TOKEN}" in env_content


def test_implicit_flow_rejects_a_blank_token(api, monkeypatch, tmp_path):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")

    res = runner.invoke(cli.app, ["auth", "login", "--yes"], input="   \n")

    assert res.exit_code == 1
    assert res.exception is None or isinstance(res.exception, SystemExit)  # no traceback
    assert "No token was pasted" in res.output
    assert not api.calls  # nothing is sent with an empty credential
    assert not (tmp_path / ".env").exists()


def test_device_code_failure_is_a_typed_error(api, monkeypatch):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    api.add("POST", DEVICE_CODE_URL, content="<html>down</html>", status=503)

    res = runner.invoke(cli.app, ["auth", "login", "--yes"])

    # ycli.cli.app.main turns a YandexError into one clean line; a JSONDecodeError would not.
    assert isinstance(res.exception, YandexServerError)


def test_implicit_flag_overrides_device(monkeypatch, tmp_path, api):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv(
        "YANDEX_OAUTH_CLIENT_SECRET", "app-secret"
    )  # secret set, but --implicit wins
    _stub_single_org(api)
    _stub_valid_me(api)

    res = runner.invoke(cli.app, ["auth", "login", "--yes", "--implicit"], input=f"{TOKEN}\n")

    assert res.exit_code == 0, res.output


def test_multiple_orgs_prompts_for_choice(monkeypatch, tmp_path, api):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code(api)
    _stub_token_success(api)
    api.add(
        "GET",
        ORG_URL,
        json={"organizations": [{"id": 42, "name": "Acme"}, {"id": 43, "name": "Beta"}]},
        status=200,
    )
    _stub_valid_me(api)

    # 0 and 3 are outside the list of two: each is refused and the prompt repeats.
    res = runner.invoke(cli.app, ["auth", "login", "--yes"], input="0\n3\n2\n")

    assert res.exit_code == 0, res.output
    assert res.output.count("Enter a number from 1 to 2.") == 2
    env_content = (tmp_path / ".env").read_text(encoding="utf-8")
    assert "YANDEX_ID_ORGANIZATION_ID=43" in env_content


def test_org_fallback_prompt_on_missing_scope(monkeypatch, tmp_path, api):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code(api)
    _stub_token_success(api)
    api.add("GET", ORG_URL, status=403)
    _stub_valid_me(api)

    res = runner.invoke(cli.app, ["auth", "login", "--yes"], input="manual-org-99\n")

    assert res.exit_code == 0, res.output
    assert "directory:read_organization" in res.output
    assert "tracker.yandex.ru/admin/orgs" in res.output
    env_content = (tmp_path / ".env").read_text(encoding="utf-8")
    assert "YANDEX_ID_ORGANIZATION_ID=manual-org-99" in env_content


def test_confirm_declined_skips_write(monkeypatch, tmp_path, api):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code(api)
    _stub_token_success(api)
    _stub_single_org(api)
    _stub_valid_me(api)

    res = runner.invoke(cli.app, ["auth", "login"], input="n\n")

    assert res.exit_code == 0, res.output
    assert not (tmp_path / ".env").exists()


def test_confirm_accepted_writes(monkeypatch, tmp_path, api):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code(api)
    _stub_token_success(api)
    _stub_single_org(api)
    _stub_valid_me(api)

    res = runner.invoke(cli.app, ["auth", "login"], input="y\n")

    assert res.exit_code == 0, res.output
    assert (tmp_path / ".env").exists()


def test_confirm_prompt_names_the_services_that_reject_the_token(monkeypatch, tmp_path, api):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code(api)
    _stub_token_success(api)
    _stub_single_org(api)
    api.add("GET", WIKI_ME, status=403)

    res = runner.invoke(cli.app, ["-o", "json", "auth", "login"], input="n\n")

    assert res.exit_code == 0, res.output
    assert "The token works for: tracker, forms. Rejected by: wiki." in res.stderr
    assert '"service":"wiki","valid":false' in res.stdout


class _FakeOAuth:
    """A stand-in OAuthClient: yields the given poll results in order after one device code."""

    def __init__(self, results):
        self._results = iter(results)

    def request_device_code(self, *, device_name=None):
        return SimpleNamespace(
            verification_url="https://ya.ru/device",
            user_code="ABCD-EFGH",
            device_code="dev-1",
            interval=0,
            expires_in=None,
        )

    def poll_token(self, device_code):
        return next(self._results)


def test_device_flow_shows_code_in_a_panel_and_returns_token(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _seconds: None)
    buf = StringIO()
    console = Console(file=buf, force_terminal=False, width=80)
    client = _FakeOAuth(
        [TokenPollResult(pending=True), TokenPollResult(token=TokenResponse(access_token="tok-9"))]
    )
    token = _device_flow(client, None, console)  # ty: ignore[invalid-argument-type]
    assert token == "tok-9"
    out = buf.getvalue()
    assert "ABCD-EFGH" in out  # the code is shown prominently
    assert "Authorize ycli" in out  # inside a titled panel


def test_suppressed_stderr_silences_fd_level_browser_noise(capfd):
    with _suppressed_stderr():
        os.write(2, b"browser-subprocess-noise")
    _out, err = capfd.readouterr()
    assert "browser-subprocess-noise" not in err  # fd-2 chatter swallowed during the launch


def test_backup_existing_env(monkeypatch, tmp_path, api):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    (tmp_path / ".env").write_text("KEEP=me\nYANDEX_ID_OAUTH_TOKEN=old\n", encoding="utf-8")
    _stub_device_code(api)
    _stub_token_success(api)
    _stub_single_org(api)
    _stub_valid_me(api)

    res = runner.invoke(cli.app, ["auth", "login", "--yes"])

    assert res.exit_code == 0, res.output
    assert (tmp_path / ".env.bak").read_text(
        encoding="utf-8"
    ) == "KEEP=me\nYANDEX_ID_OAUTH_TOKEN=old\n"
    env_content = (tmp_path / ".env").read_text(encoding="utf-8")
    assert "KEEP=me" in env_content
    assert f"YANDEX_ID_OAUTH_TOKEN={TOKEN}" in env_content
    assert "YANDEX_ID_OAUTH_TOKEN=old" not in env_content


def test_device_code_stays_copyable_while_waiting(api, monkeypatch):
    """No live redraw while the code is on screen: a redraw drops the user's text selection."""
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    _stub_device_code(api)
    _stub_token_success(api)

    def no_live_region(self: Live) -> None:
        raise AssertionError("the device code screen must not redraw the terminal")

    monkeypatch.setattr(Live, "start", no_live_region)
    screen = StringIO()
    console = Console(file=screen, force_terminal=True, width=80)
    client = OAuthClient(
        client_id="app-id", client_secret="app-secret", timeout_seconds=30.0, retries=0
    )

    assert _device_flow(client, None, console) == TOKEN
    assert "Waiting for you to confirm" in screen.getvalue()


def test_login_refuses_dry_run(monkeypatch):
    """Signing in cannot be planned: it would talk to Yandex and write .env for real."""
    monkeypatch.setattr(OAuthClient, "__init__", lambda *args, **kwargs: pytest.fail("signed in"))
    result = runner.invoke(cli.app, ["auth", "login", "--dry-run"])
    assert result.exit_code == 2
    assert "nothing to plan" in result.output
