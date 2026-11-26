"""The DataLens kinds of `ycli sync`: an Editor chart and a dashboard of a workbook as a file."""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

import ycli.cli.app as cli

RPC = "https://api.datalens.tech/rpc"
WB = "wb000000000001"
OTHER = "wb000000000002"
TABS = {
    "meta": "{}",
    "params": "module.exports = {};",
    "sources": "module.exports = {};",
    "controls": "module.exports = {};",
    "prepare": "// sales\nmodule.exports = {};\n",
    "config": "module.exports = {};",
}
CHART: dict[str, Any] = {
    "version": 1,
    "entryId": "ch000000000001",
    "key": "1/sales",
    "revId": "r1",
    "savedId": "r1",
    "publishedId": "r1",
    "workbookId": WB,
    "scope": "widget",
    "type": "d3_node",
    "meta": {},
    "links": None,
    "annotation": {"description": "Sales"},
    "data": {**TABS, "activities": None},
}
DASH: dict[str, Any] = {
    "entryId": "da000000000001",
    "key": "2/overview",
    "revId": "r1",
    "savedId": "r1",
    "publishedId": "r1",
    "workbookId": WB,
    "scope": "dash",
    "type": "",
    "meta": {},
    "links": {},
    "annotation": {"description": "Sales"},
    "data": {"counter": 2, "salt": "0.5", "tabs": [{"id": "t1", "title": "Main", "items": []}]},
}


@dataclass(frozen=True)
class Shape:
    """One DataLens kind as the tests drive it."""

    kind: str
    folder: str
    name: str
    entry: dict[str, Any]
    id_key: str
    rpc: str
    content: tuple[str, ...]
    data: dict[str, Any]


EDITOR = Shape(
    "datalens/editor-chart",
    "charts",
    "sales",
    CHART,
    "chartId",
    "EditorChart",
    ("type", "annotation", "meta", "data"),
    # A tab that came as `null` is no key of the file.
    TABS,
)
DASHBOARD = Shape(
    "datalens/dashboard",
    "dashboards",
    "overview",
    DASH,
    "dashboardId",
    "Dashboard",
    ("annotation", "meta", "data"),
    DASH["data"],
)
SHAPES = pytest.mark.parametrize("shape", [EDITOR, DASHBOARD], ids=["editor-chart", "dashboard"])


@pytest.fixture(autouse=True)
def signed_in(monkeypatch):
    """DataLens takes an IAM token and a Yandex Cloud organization."""
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")


def _run(root: Path, monkeypatch, *argv: str) -> tuple[int, list[dict], str]:
    monkeypatch.chdir(root)
    result = CliRunner().invoke(cli.app, ["-o", "json", *argv])
    listed = json.loads(result.stdout) if result.stdout.strip() else []
    return result.exit_code, listed, result.stderr


def _listed(api, *entries: dict[str, Any]) -> None:
    api.add("POST", f"{RPC}/getWorkbookEntries", json={"entries": list(entries)})


def _read(api, shape: Shape, *answers: dict[str, Any]) -> None:
    for entry in answers:
        api.add("POST", f"{RPC}/get{shape.rpc}", json={"entry": entry})


def _bodies(api, name: str) -> list[Any]:
    return [json.loads(call.content) for call in api.calls if call.url.path == f"/rpc/{name}"]


def _path(shape: Shape, workbook: str = WB) -> str:
    return f"datalens/workbooks/{workbook}/{shape.folder}/{shape.name}.yaml"


def _pulled(api, root: Path, monkeypatch, shape: Shape, *after: dict[str, Any]) -> Path:
    """The entry as `pull` writes it; ``after`` are what reading it answers from then on."""
    wizard = {"entryId": "wz000000000001", "scope": "widget", "type": "graph_wizard_node"}
    # DataLens lists only the scope asked for; a wizard chart is a widget too.
    _listed(api, {**shape.entry, "data": None}, *([wizard] if shape is EDITOR else []))
    _read(api, shape, shape.entry, *after)
    pulled = ["sync", "pull", f"datalens/workbooks/{WB}", "--kind", shape.kind]
    code, _, summary = _run(root, monkeypatch, *pulled)
    assert code == 0, summary
    return root / _path(shape)


def _edit(file: Path) -> None:
    text = file.read_text("utf-8")
    file.write_text(text.replace("description: Sales", "description: Sales, edited"), "utf-8")


@SHAPES
def test_pull_writes_each_entry_of_a_workbook_under_its_name(api, tmp_path, monkeypatch, shape):
    file = _pulled(api, tmp_path, monkeypatch, shape)
    held = yaml.safe_load(file.read_text("utf-8"))
    assert held.pop("hash")
    assert held == {
        "ycli": shape.kind,
        "entryId": shape.entry["entryId"],
        "revId": "r1",
        **{key: shape.entry[key] for key in shape.content},
        "data": shape.data,
    }
    # What everyone sees is read, in the workbook the path names; a wizard chart is not read.
    (read,) = _bodies(api, f"get{shape.rpc}")
    assert read == {shape.id_key: shape.entry["entryId"], "workbookId": WB, "branch": "published"}
    (listing,) = _bodies(api, "getWorkbookEntries")
    assert listing["workbookId"] == WB
    _, after, _ = _run(tmp_path, monkeypatch, "sync", "status", "--show-unchanged")
    assert [(row["path"], row["state"]) for row in after] == [(_path(shape), "unchanged")]


@SHAPES
def test_push_publishes_an_edit_and_sends_no_revision(api, tmp_path, monkeypatch, shape):
    edited = {**shape.entry, "annotation": {"description": "Sales, edited"}, "revId": "r2"}
    file = _pulled(api, tmp_path, monkeypatch, shape, shape.entry, edited)
    api.add("POST", f"{RPC}/update{shape.rpc}", json={"entry": edited})
    _edit(file)
    code, listed, summary = _run(tmp_path, monkeypatch, "sync", "push")
    assert code == 0, summary
    assert [(row["path"], row["result"]) for row in listed] == [(_path(shape), "updated")]
    (sent,) = _bodies(api, f"update{shape.rpc}")
    # A revision in the entry would publish that revision and drop what was sent (measured).
    assert sent["mode"] == "publish" and "revId" not in sent["entry"]
    assert sent["entry"]["entryId"] == shape.entry["entryId"]
    assert sent["entry"]["annotation"] == {"description": "Sales, edited"}
    assert "\nrevId: r2\n" in file.read_text("utf-8")


@SHAPES
def test_a_new_file_creates_its_entry_in_the_workbook_and_under_the_name_of_its_path(
    api, tmp_path, monkeypatch, shape
):
    created = {**shape.entry, "entryId": "new000000001", "key": "1/new"}
    new = tmp_path / f"datalens/workbooks/{WB}/{shape.folder}/new.yaml"
    new.parent.mkdir(parents=True)
    content = {key: shape.entry[key] for key in shape.content}
    new.write_text(yaml.safe_dump({"ycli": shape.kind, **content}), encoding="utf-8")
    api.add("POST", f"{RPC}/create{shape.rpc}", json={"entry": created})
    _read(api, shape, created)
    code, listed, summary = _run(tmp_path, monkeypatch, "sync", "push")
    assert code == 0, summary
    # A file named by its entry stays where it is: the name is the entry's, not its id.
    assert [(row["path"], row["result"]) for row in listed] == [
        (str(new.relative_to(tmp_path)), "created")
    ]
    (sent,) = _bodies(api, f"create{shape.rpc}")
    assert sent["entry"]["workbookId"] == WB and sent["entry"]["name"] == "new"
    held = yaml.safe_load(new.read_text("utf-8"))
    assert (held["entryId"], held["revId"]) == ("new000000001", "r1")


@SHAPES
def test_a_file_whose_entry_lies_in_another_workbook_is_refused_before_a_write(
    api, tmp_path, monkeypatch, shape
):
    """DataLens refuses a read in a workbook the entry is not in: nothing is sent after it."""
    copied = tmp_path / _path(shape, OTHER)
    copied.parent.mkdir(parents=True)
    link = {"hash": "0" * 64, "entryId": shape.entry["entryId"], "revId": "r1"}
    content = {key: shape.entry[key] for key in shape.content}
    copied.write_text(yaml.safe_dump({"ycli": shape.kind, **link, **content}), encoding="utf-8")
    refusal = {"code": "WORKBOOK_ISOLATION_INTERRUPTION", "message": "Workbook isolation"}
    api.add("POST", f"{RPC}/get{shape.rpc}", json=refusal, status=403)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli.app, ["-o", "json", "sync", "push"])
    assert result.exit_code != 0
    assert "WORKBOOK_ISOLATION_INTERRUPTION" in str(result.exception) + result.output
    assert _bodies(api, f"update{shape.rpc}") == []
    assert _bodies(api, f"get{shape.rpc}")[-1]["workbookId"] == OTHER


def _commit(root: Path) -> None:
    for command in (["init", "-q"], ["add", "."]):
        subprocess.run(["git", *command], cwd=root, check=True)
    commit = ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "pulled"]
    subprocess.run(["git", *commit], cwd=root, check=True)


@SHAPES
def test_prune_reads_the_entry_in_its_workbook_then_deletes_it(api, tmp_path, monkeypatch, shape):
    file = _pulled(api, tmp_path, monkeypatch, shape)
    _commit(tmp_path)
    file.unlink()
    api.add("POST", f"{RPC}/delete{shape.rpc}", json={})
    code, listed, summary = _run(tmp_path, monkeypatch, "--yes", "sync", "push", "--prune", "HEAD")
    assert code == 0, summary
    assert [(row["path"], row["result"]) for row in listed] == [(_path(shape), "deleted")]
    assert _bodies(api, f"delete{shape.rpc}") == [{shape.id_key: shape.entry["entryId"]}]
    # Read once by `pull`, and once more by the prune itself, in the workbook, before the delete.
    sent = [call.url.path.rpartition("/")[2] for call in api.calls]
    assert sent[-2:] == [f"get{shape.rpc}", f"delete{shape.rpc}"]
    reads = _bodies(api, f"get{shape.rpc}")
    assert len(reads) == 2 and reads[1]["workbookId"] == WB


def test_prune_deletes_nothing_of_another_workbook(api, tmp_path, monkeypatch):
    """A deleted file that held an entry of another workbook: its read is refused, so no delete."""
    copied = tmp_path / _path(EDITOR, OTHER)
    copied.parent.mkdir(parents=True)
    link = {"hash": "0" * 64, "entryId": CHART["entryId"], "revId": "r1"}
    copied.write_text(yaml.safe_dump({"ycli": EDITOR.kind, **link, "type": "d3_node"}), "utf-8")
    _commit(tmp_path)
    copied.unlink()
    refusal = {"code": "WORKBOOK_ISOLATION_INTERRUPTION", "message": "Workbook isolation"}
    api.add("POST", f"{RPC}/getEditorChart", json=refusal, status=403)
    code, listed, _ = _run(tmp_path, monkeypatch, "--yes", "sync", "push", "--prune", "HEAD")
    assert (code, listed[0]["result"]) == (1, "failed")
    assert "WORKBOOK_ISOLATION_INTERRUPTION" in listed[0]["detail"]
    assert _bodies(api, "deleteEditorChart") == []


def test_sync_kinds_lists_both(monkeypatch):
    result = CliRunner().invoke(cli.app, ["-o", "json", "sync", "kinds"])
    listed = {row["name"]: row for row in json.loads(result.stdout)}
    for name in ("datalens/editor-chart", "datalens/dashboard"):
        assert listed[name]["operations"] == ["read", "find", "create", "update", "delete"]
        assert listed[name]["version"] == "read and compared before the write"


def test_a_path_that_names_one_file_says_nothing_of_the_rest_of_its_workbook(
    api, tmp_path, monkeypatch
):
    """A deleted file is no file, so its workbook is listed: only what the path names is said."""
    _pulled(api, tmp_path, monkeypatch, EDITOR)
    gone = f"datalens/workbooks/{WB}/charts/gone.yaml"
    _, listed, _ = _run(tmp_path, monkeypatch, "sync", "diff", gone)
    assert listed == []


@SHAPES
def test_a_copy_of_a_file_under_another_name_is_stopped(api, tmp_path, monkeypatch, shape):
    """The copy holds the id of the original: pushing it would overwrite the original entry."""
    file = _pulled(api, tmp_path, monkeypatch, shape)
    copy = file.with_name("copy.yaml")
    copy.write_text(file.read_text("utf-8"), "utf-8")
    _edit(copy)
    code, listed, _ = _run(tmp_path, monkeypatch, "sync", "push", str(copy.relative_to(tmp_path)))
    assert code == 8
    assert [(row["state"], row["result"]) for row in listed] == [("moved", "stopped")]
    assert listed[0]["detail"] == f"the file is named copy and holds the object named {shape.name}"
    assert _bodies(api, f"update{shape.rpc}") == []


@SHAPES
def test_prune_deletes_nothing_a_file_still_holds(api, tmp_path, monkeypatch, shape):
    """A rename that git sees as a delete: the entry lives on in the renamed file."""
    file = _pulled(api, tmp_path, monkeypatch, shape)
    _commit(tmp_path)
    file.rename(file.with_name("renamed.yaml"))
    code, listed, _ = _run(tmp_path, monkeypatch, "--yes", "sync", "push", "--prune", "HEAD")
    # The renamed file is said for what it is; its entry is not a candidate to delete.
    assert code == 8
    renamed = _path(shape).replace(f"{shape.name}.yaml", "renamed.yaml")
    assert [(row["path"], row["state"]) for row in listed] == [(renamed, "moved")]
    assert _bodies(api, f"delete{shape.rpc}") == []


@SHAPES
def test_an_unpublished_draft_stops_the_file(api, tmp_path, monkeypatch, shape):
    """A draft saved in DataLens after the pull: publishing the file would throw it away."""
    drafted = {**shape.entry, "savedId": "d1"}
    file = _pulled(api, tmp_path, monkeypatch, shape, drafted)
    _edit(file)
    code, listed, _ = _run(tmp_path, monkeypatch, "sync", "push")
    assert code == 8
    assert [(row["state"], row["result"]) for row in listed] == [("changed-on-server", "stopped")]
    assert listed[0]["detail"] == "unpublished draft in DataLens; publish or discard it first"
    assert _bodies(api, f"update{shape.rpc}") == []


def test_a_refused_read_fails_its_file_and_the_rest_still_runs(api, tmp_path, monkeypatch):
    """Each file is read on its own: one refused read names its file and stops nothing else."""
    file = _pulled(api, tmp_path, monkeypatch, DASHBOARD)
    copied = tmp_path / _path(EDITOR, OTHER)
    copied.parent.mkdir(parents=True)
    link = {"hash": "0" * 64, "entryId": CHART["entryId"], "revId": "r1"}
    copied.write_text(yaml.safe_dump({"ycli": EDITOR.kind, **link, "type": "d3_node"}), "utf-8")
    refusal = {"code": "WORKBOOK_ISOLATION_INTERRUPTION", "message": "Workbook isolation"}
    api.add("POST", f"{RPC}/getEditorChart", json=refusal, status=403)
    code, listed, _ = _run(tmp_path, monkeypatch, "sync", "push", "--show-unchanged")
    assert code == 1
    results = {row["path"]: (row["state"], row["result"]) for row in listed}
    assert results == {
        _path(EDITOR, OTHER): ("refused", "failed"),
        str(file.relative_to(tmp_path)): ("unchanged", "unchanged"),
    }
    (refused,) = [row for row in listed if row["state"] == "refused"]
    assert "WORKBOOK_ISOLATION_INTERRUPTION" in refused["detail"]
    assert "another workbook" in refused["detail"]
    assert _bodies(api, "updateEditorChart") == []


def test_pull_names_once_each_kind_of_editor_chart_the_api_does_not_describe(
    api, tmp_path, monkeypatch
):
    old = [{"entryId": f"gr00000000000{n}", "scope": "widget", "type": "graph_node"} for n in "12"]
    wizard = {"entryId": "wz000000000001", "scope": "widget", "type": "graph_wizard_node"}
    _listed(api, {**CHART, "data": None}, *old, wizard)
    _read(api, EDITOR, CHART)
    scope = f"datalens/workbooks/{WB}"
    code, listed, _ = _run(tmp_path, monkeypatch, "sync", "pull", scope, "--kind", EDITOR.kind)
    assert code == 0
    skipped = [(row["path"], row["detail"]) for row in listed if row["action"] == "skipped"]
    # A chart of the wizard is another kind's and is not said; neither is read.
    assert skipped == [(scope, "2 not read: an Editor chart of type graph_node, not in the API")]
    assert [body["chartId"] for body in _bodies(api, "getEditorChart")] == [CHART["entryId"]]


def test_the_content_of_a_file_is_what_the_update_takes_without_its_link():
    """The generated entry of a write, so a field DataLens adds reaches the file by itself."""
    from pydantic import ValidationError

    from ycli.yandex.datalens.charts.models import EditorChartContent
    from ycli.yandex.datalens.dashboards.models import DashboardContent
    from ycli.yandex.sync.document import as_sent

    # A `null` meta is what an update of a dashboard requires sent, as the generated entry says.
    assert as_sent(DashboardContent.model_validate({"meta": None})) == {"meta": None}
    # The revision is the link's: as content it would publish that revision (measured).
    for content, given in ((DashboardContent, {}), (EditorChartContent, {"type": "d3_node"})):
        with pytest.raises(ValidationError):
            content.model_validate({**given, "revId": "r1"})
