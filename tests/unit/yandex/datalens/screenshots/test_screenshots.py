"""`datalens screenshots ... --output`: only a base64 picture in the reply becomes a file."""

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli
from ycli.yandex.datalens import SERVICE
from ycli.yandex.errors import YandexUnexpectedReplyError

BASE = SERVICE.profile.base_url.rstrip("/")


@pytest.fixture(autouse=True)
def signed_in(monkeypatch):
    """DataLens takes an IAM token and a Yandex Cloud organization."""
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")


def _dashboard(target, *flags):
    argv = ["datalens", "screenshots", "dashboard-get", "d1", *flags, "--output", str(target)]
    return CliRunner().invoke(cli.app, argv)


@pytest.mark.parametrize("flag", ["--s3", "--no-base64"])
def test_output_refuses_what_keeps_the_picture_out_of_the_reply(api, tmp_path, flag):
    target = tmp_path / "dash.png"
    result = _dashboard(target, flag)
    assert result.exit_code == 2
    said = " ".join(result.output.replace("│", " ").split())  # the error box wraps its text
    assert "drop --s3 and --no-base64" in said
    assert api.calls == []
    assert not target.exists()


@pytest.mark.parametrize(
    ("reply", "says"),
    [
        (
            {"status": 500, "code": "ERR.SCREENSHOT", "message": "render failed"},
            "the reply holds no picture: ERR.SCREENSHOT render failed",
        ),
        ({"data": "https://s3.example.invalid/d1.png"}, "the reply holds no base64 picture"),
    ],
)
def test_a_reply_with_no_base64_picture_writes_no_file(api, tmp_path, reply, says):
    api.add("POST", f"{BASE}/rpc/getDashScreenshot", json=reply)
    target = tmp_path / "dash.png"
    result = _dashboard(target)
    assert isinstance(result.exception, YandexUnexpectedReplyError)
    assert says in str(result.exception)
    assert not target.exists()
