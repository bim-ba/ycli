"""`datalens screenshots ... --output`: a reply with no picture is an error, not an empty file."""

from typer.testing import CliRunner

import ycli.cli.app as cli
from ycli.yandex.datalens import SERVICE
from ycli.yandex.errors import YandexUnexpectedReplyError

BASE = SERVICE.profile.base_url.rstrip("/")


def test_a_reply_with_no_picture_writes_no_file(api, monkeypatch, tmp_path):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")
    reply = {"status": 500, "code": "ERR.SCREENSHOT", "message": "render failed"}
    api.add("POST", f"{BASE}/rpc/getDashScreenshot", json=reply)
    target = tmp_path / "dash.png"
    argv = ["datalens", "screenshots", "dashboard-get", "d1", "--output", str(target)]
    result = CliRunner().invoke(cli.app, argv)
    assert isinstance(result.exception, YandexUnexpectedReplyError)
    assert "ERR.SCREENSHOT render failed" in str(result.exception)
    assert not target.exists()
