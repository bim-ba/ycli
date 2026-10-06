"""`datalens workbookexports start` and `workbookimports start` wait for what they started."""

import json

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli
from ycli.yandex.datalens import SERVICE

BASE = SERVICE.profile.base_url.rstrip("/")


@pytest.fixture(autouse=True)
def signed_in(monkeypatch):
    """DataLens takes an IAM token and a Yandex Cloud organization."""
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")
    monkeypatch.setattr("time.sleep", lambda seconds: None)


def test_an_export_is_polled_to_its_final_status_by_default(api):
    api.add("POST", f"{BASE}/rpc/startWorkbookExport", json={"exportId": "exp1"})
    for status, progress in (("pending", 0), ("success", 100)):
        api.add(
            "POST",
            f"{BASE}/rpc/getWorkbookExportStatus",
            json={"exportId": "exp1", "status": status, "progress": progress},
        )
    result = CliRunner().invoke(
        cli.app, ["-o", "json", "datalens", "workbookexports", "start", "wb1"]
    )
    assert result.exit_code == 0, result.output
    printed = json.loads(result.stdout)
    assert (printed["exportId"], printed["status"], printed["progress"]) == ("exp1", "success", 100)
    assert len(api.calls) == 3


def test_an_import_is_polled_to_its_final_status_by_default(api):
    api.add("POST", f"{BASE}/rpc/startWorkbookImport", json={"importId": "imp1", "workbookId": "w"})
    api.add(
        "POST",
        f"{BASE}/rpc/getWorkbookImportStatus",
        json={"importId": "imp1", "workbookId": "w", "status": "error", "progress": 30},
    )
    argv = ["workbookimports", "start", "--data", '{"export": {}, "hash": "h"}', "--title", "T"]
    result = CliRunner().invoke(cli.app, ["-o", "json", "datalens", *argv])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["status"] == "error"
    assert api.body(0) == {"data": {"export": {}, "hash": "h"}, "title": "T", "collectionId": None}
