"""`ycli sync push`: the plan carried out, each write read back and compared."""

import json
import subprocess
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

import ycli.cli.app as cli

WIKI = "https://api.wiki.yandex.net/v1"
TRACKER = "https://api.tracker.yandex.net/v3"
TEAM = {"id": 4821, "slug": "team", "title": "Team", "page_type": "page", "content": "# Team\n"}
EDITED = {**TEAM, "content": "# Team, edited\n"}
TRIGGER = {
    "self": f"{TRACKER}/queues/DE/triggers/16",
    "id": 16,
    "queue": {"key": "DE"},
    "name": "Assign on create",
    "actions": [{"type": "Transition", "status": {"key": "inProgress"}}],
    "conditions": [{"type": "Event.create"}],
    "version": 3,
    "active": True,
}


def _page(api, *answers: tuple[Any, ...]) -> None:
    """What reading a page answers, call after call: ``(page, revision)`` or with a status."""
    for page, revision, *status in answers:
        api.add("GET", f"{WIKI}/pages/{page['id']}", json=page, status=(status or [200])[0])
        revisions = {"results": [{"id": revision}], "next_cursor": None}
        api.add("GET", f"{WIKI}/pages/{page['id']}/revisions", json=revisions)


def _run(root: Path, monkeypatch, *argv: str) -> tuple[int, list[dict], str]:
    monkeypatch.chdir(root)
    result = CliRunner().invoke(cli.app, ["-o", "json", *argv])
    listed = json.loads(result.stdout) if result.stdout.strip() else []
    return result.exit_code, listed, result.stderr


def _pulled(api, root: Path, monkeypatch, *answers: tuple[Any, ...]) -> Path:
    """The page as `pull` writes it from the first answer; the rest are the answers after."""
    listed = {"results": [{"id": 4821, "slug": "team"}], "next_cursor": None}
    api.add("GET", f"{WIKI}/pages/descendants", json=listed)
    _page(api, *answers)
    code, _, summary = _run(root, monkeypatch, "sync", "pull", "wiki/team")
    assert code == 0, summary
    return root / "wiki/team.md"


def _edit(page: Path) -> None:
    page.write_text(page.read_text("utf-8").replace("# Team", "# Team, edited"), encoding="utf-8")


def _sent(api, method: str) -> list[Any]:
    return [call for call in api.calls if call.method == method]


def test_an_edited_file_is_sent_read_back_and_gets_its_new_link(api, tmp_path, monkeypatch):
    # Read three times: by `pull`, by the plan, and back after the write.
    page = _pulled(api, tmp_path, monkeypatch, (TEAM, 1), (TEAM, 1), (EDITED, 2))
    api.add("POST", f"{WIKI}/pages/4821", json=EDITED)
    _edit(page)
    code, listed, summary = _run(tmp_path, monkeypatch, "sync", "push")
    assert code == 0, summary
    assert [(row["path"], row["state"], row["result"]) for row in listed] == [
        ("wiki/team.md", "update", "updated")
    ]
    # Nothing was added by the service, so the summary says nothing of it.
    assert summary.strip() == "0 created, 1 updated, 0 deleted, 0 unchanged, 0 stopped, 0 failed"
    assert listed[0]["added"] is False
    (sent,) = _sent(api, "POST")
    assert json.loads(sent.content) == {"title": "Team", "content": "# Team, edited\n"}
    # The file carries the version it was read back at, and is unchanged from now on.
    assert "\nrevision: 2\n" in page.read_text("utf-8")
    _, after, _ = _run(tmp_path, monkeypatch, "sync", "status", "--show-unchanged")
    assert [row["state"] for row in after] == ["unchanged"]


def test_a_file_whose_object_changed_on_the_server_is_stopped_and_nothing_is_sent(
    api, tmp_path, monkeypatch
):
    theirs = {**TEAM, "content": "# Team, by somebody else\n"}
    page = _pulled(api, tmp_path, monkeypatch, (TEAM, 1), (theirs, 2))
    _edit(page)
    before = page.read_text("utf-8")
    code, listed, _ = _run(tmp_path, monkeypatch, "sync", "push")
    assert code == 8
    assert [(row["state"], row["result"]) for row in listed] == [("changed-on-server", "stopped")]
    assert listed[0]["detail"] == "the object changed on the server: pull, then push"
    assert _sent(api, "POST") == [] and page.read_text("utf-8") == before


def test_a_value_the_server_did_not_keep_fails_the_file_aloud(api, tmp_path, monkeypatch):
    # The write is answered, and reading back shows the old text: the server dropped ours.
    page = _pulled(api, tmp_path, monkeypatch, (TEAM, 1), (TEAM, 1), (TEAM, 2))
    api.add("POST", f"{WIKI}/pages/4821", json=TEAM)
    _edit(page)
    before = page.read_text("utf-8")
    code, listed, _ = _run(tmp_path, monkeypatch, "sync", "push")
    assert code == 1
    assert listed[0]["result"] == "failed"
    assert listed[0]["detail"] == "written, and the server did not keep: content"
    # The link stays as it was read, so `diff` shows the file against the server from here.
    assert page.read_text("utf-8") == before


def test_a_new_file_creates_its_object_and_gets_the_link(api, tmp_path, monkeypatch):
    created = {
        "id": 5000,
        "slug": "team/new",
        "title": "New",
        "page_type": "page",
        "content": "Text\n",
    }
    new = tmp_path / "wiki/team/new.md"
    new.parent.mkdir(parents=True)
    new.write_text("---\nycli: wiki/page\ntitle: New\n---\nText\n", encoding="utf-8")
    api.add("POST", f"{WIKI}/pages", json=created)
    _page(api, (created, 9))
    code, listed, summary = _run(tmp_path, monkeypatch, "sync", "push", "wiki/team/new.md")
    assert code == 0, summary
    assert [(row["state"], row["result"]) for row in listed] == [("create", "created")]
    # Where the file lies is where the page goes: the path gives the request its `slug`.
    (sent,) = _sent(api, "POST")
    assert json.loads(sent.content) == {"slug": "team/new", "title": "New", "content": "Text\n"}
    text = new.read_text("utf-8")
    assert "\nid: 5000\n" in text and "\nrevision: 9\n" in text and "\nhash: " in text


def test_a_new_file_under_an_identity_is_moved_to_the_name_of_its_object(
    api, tmp_path, monkeypatch
):
    new = tmp_path / "tracker/queues/DE/triggers/assign.yaml"
    new.parent.mkdir(parents=True)
    new.write_text(
        "ycli: tracker/trigger\nname: Assign on create\n"
        "actions:\n- type: Transition\n  status:\n    key: inProgress\n",
        encoding="utf-8",
    )
    api.add("POST", f"{TRACKER}/queues/DE/triggers", json=TRIGGER)
    api.add("GET", f"{TRACKER}/queues/DE/triggers/16", json=TRIGGER)
    code, listed, summary = _run(tmp_path, monkeypatch, "sync", "push")
    assert code == 0, summary
    assert [(row["path"], row["result"]) for row in listed] == [
        ("tracker/queues/DE/triggers/16.yaml", "created")
    ]
    assert not new.exists()
    # The file was written anew: it is said of the file, and counted in the summary.
    assert listed[0]["added"] is True
    assert summary.strip().endswith("0 failed; 1 file now holds what the service added")
    text = (tmp_path / "tracker/queues/DE/triggers/16.yaml").read_text("utf-8")
    # What the server added of its own (the conditions) is in the file from now on.
    assert "\nid: 16\nversion: 3\n" in text and "conditions:\n- type: Event.create\n" in text
    assert _run(tmp_path, monkeypatch, "sync", "status")[1] == []


def test_an_update_carries_the_version_where_the_api_takes_one(api, tmp_path, monkeypatch):
    renamed = {**TRIGGER, "name": "Renamed", "version": 4}
    api.add("GET", f"{TRACKER}/queues/DE/triggers", json=[TRIGGER])
    api.add("GET", f"{TRACKER}/queues/DE/triggers", json=[])  # the page after the last
    for answer in (TRIGGER, TRIGGER, renamed):
        api.add("GET", f"{TRACKER}/queues/DE/triggers/16", json=answer)
    api.add("PATCH", f"{TRACKER}/queues/DE/triggers/16", json=renamed)
    _run(tmp_path, monkeypatch, "sync", "pull", "tracker/queues/DE")
    file = tmp_path / "tracker/queues/DE/triggers/16.yaml"
    file.write_text(
        file.read_text("utf-8").replace("Assign on create", "Renamed"), encoding="utf-8"
    )
    code, listed, summary = _run(
        tmp_path, monkeypatch, "sync", "push", "tracker/queues/DE/triggers/16.yaml"
    )
    assert (code, listed[0]["result"]) == (0, "updated"), summary
    (sent,) = _sent(api, "PATCH")
    assert sent.url.params["version"] == "3"
    assert "\nversion: 4\n" in file.read_text("utf-8")


def test_a_file_the_api_refuses_fails_and_on_error_says_whether_the_run_goes_on(
    api, tmp_path, monkeypatch
):
    for name in ("a", "b"):
        new = tmp_path / f"wiki/team/{name}.md"
        new.parent.mkdir(parents=True, exist_ok=True)
        new.write_text("---\nycli: wiki/page\n---\nNo title\n", encoding="utf-8")
    code, listed, summary = _run(tmp_path, monkeypatch, "sync", "push")
    assert code == 1
    assert [row["result"] for row in listed] == ["failed", "failed"]
    assert "title" in listed[0]["detail"] and api.calls == []
    assert summary.strip().endswith("0 stopped, 2 failed")
    _, aborted, _ = _run(tmp_path, monkeypatch, "sync", "push", "--on-error", "abort")
    assert [row["path"] for row in aborted] == ["wiki/team/a.md"]


def test_an_error_of_the_api_fails_the_file_with_what_the_api_said(api, tmp_path, monkeypatch):
    page = _pulled(api, tmp_path, monkeypatch, (TEAM, 1))
    api.add("POST", f"{WIKI}/pages/4821", json={"debug_message": "no access"}, status=403)
    _edit(page)
    code, listed, _ = _run(tmp_path, monkeypatch, "sync", "push")
    assert (code, listed[0]["result"]) == (1, "failed")
    assert listed[0]["detail"]


def test_a_dry_run_sends_nothing_and_prints_the_plan(api, tmp_path, monkeypatch):
    page = _pulled(api, tmp_path, monkeypatch, (TEAM, 1))
    _edit(page)
    code, listed, summary = _run(tmp_path, monkeypatch, "--dry-run", "sync", "push")
    assert code == 0
    assert [(row["path"], row["state"], row["diff"]) for row in listed] == [
        ("wiki/team.md", "update", None)
    ]
    assert "1 update" in summary and _sent(api, "POST") == []
    _, everything, _ = _run(
        tmp_path, monkeypatch, "--dry-run", "sync", "push", "--show-unchanged", "--kind", "x/y"
    )
    assert everything == []


def _commit(root: Path) -> None:
    for command in (["init", "-q"], ["add", "."]):
        subprocess.run(["git", *command], cwd=root, check=True)
    commit = ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "pulled"]
    subprocess.run(["git", *commit], cwd=root, check=True)


def test_prune_deletes_the_object_of_a_file_deleted_since_a_commit(api, tmp_path, monkeypatch):
    page = _pulled(api, tmp_path, monkeypatch, (TEAM, 1))
    for name, text in {
        "wiki/draft.md": "---\nycli: wiki/page\ntitle: Never pushed\n---\n",
        "wiki/notes.md": "# Not a file of a kind\n",
        "tracker/queues/DE/triggers/16.yaml": "ycli: tracker/trigger\nid: 16\nname: T\n",
        "README.txt": "no kind keeps this\n",
    }.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(text, encoding="utf-8")
    _commit(tmp_path)
    for name in (
        "wiki/draft.md",
        "wiki/notes.md",
        "tracker/queues/DE/triggers/16.yaml",
        "README.txt",
    ):
        (tmp_path / name).unlink()
    page.unlink()
    api.add("DELETE", f"{WIKI}/pages/4821", json={"recovery_token": "r"})
    # The plan first: what would be deleted, and what cannot be.
    _, planned, _ = _run(tmp_path, monkeypatch, "--dry-run", "sync", "push", "--prune", "HEAD")
    assert {row["path"]: row["state"] for row in planned} == {
        "tracker/queues/DE/triggers/16.yaml": "unsupported",
        "wiki/team.md": "delete",
    }
    assert _sent(api, "DELETE") == []
    code, listed, summary = _run(tmp_path, monkeypatch, "--yes", "sync", "push", "--prune", "HEAD")
    assert {row["path"]: row["result"] for row in listed} == {
        # The API has no operation that deletes a trigger: said, and counted as a failure.
        "tracker/queues/DE/triggers/16.yaml": "failed",
        "wiki/team.md": "deleted",
    }
    assert code == 1 and "1 deleted" in summary
    assert len(_sent(api, "DELETE")) == 1


def test_prune_is_refused_outside_a_repository_and_a_failed_delete_is_said(
    api, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    refused = CliRunner().invoke(cli.app, ["sync", "push", "--prune", "main"])
    assert refused.exit_code == 2 and "--prune reads git" in refused.output
    page = _pulled(api, tmp_path, monkeypatch, (TEAM, 1))
    _commit(tmp_path)
    page.unlink()
    api.add("DELETE", f"{WIKI}/pages/4821", json={"debug_message": "no access"}, status=403)
    code, listed, _ = _run(tmp_path, monkeypatch, "--yes", "sync", "push", "--prune", "HEAD")
    assert (code, listed[0]["result"]) == (1, "failed")
    # A run that was aborted deletes nothing.
    (tmp_path / "wiki/bad.md").write_text("---\nycli: wiki/page\n---\n", encoding="utf-8")
    argv = ["--yes", "sync", "push", "--prune", "HEAD", "--on-error", "abort"]
    _, aborted, _ = _run(tmp_path, monkeypatch, *argv)
    assert [row["path"] for row in aborted] == ["wiki/bad.md"]


def test_what_cannot_be_pushed_is_counted_as_failed(api, tmp_path, monkeypatch):
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki/broken.md").write_text("---\nycli: wiki/page\nkeywords: [a]\n---\n")
    code, listed, _ = _run(tmp_path, monkeypatch, "sync", "push")
    assert (code, listed[0]["state"], listed[0]["result"]) == (1, "unreadable", "failed")
    assert "line 3" in listed[0]["detail"]


def test_nothing_to_push_is_nothing_done(api, tmp_path, monkeypatch):
    _pulled(api, tmp_path, monkeypatch, (TEAM, 1))
    code, listed, summary = _run(tmp_path, monkeypatch, "sync", "push", "wiki/team")
    assert (code, listed) == (0, [])
    assert summary.strip() == "0 created, 0 updated, 0 deleted, 1 unchanged, 0 stopped, 0 failed"
    _, everything, _ = _run(tmp_path, monkeypatch, "sync", "push", "--show-unchanged")
    assert [row["result"] for row in everything] == ["unchanged"]


def test_an_object_with_no_file_is_not_pushed_and_one_no_kind_keeps_fails(
    api, tmp_path, monkeypatch
):
    grid = {"id": 5000, "slug": "team/new", "title": "New", "page_type": "grid"}
    page = _pulled(api, tmp_path, monkeypatch, (TEAM, 1))
    page.unlink()
    new = tmp_path / "wiki/team/new.md"
    new.parent.mkdir()
    new.write_text("---\nycli: wiki/page\ntitle: New\n---\n", encoding="utf-8")
    api.add("POST", f"{WIKI}/pages", json=grid)
    _page(api, (grid, 1))
    code, listed, _ = _run(tmp_path, monkeypatch, "sync", "push", "wiki/team")
    # The page with no file is `pull`'s to write; what came back from the write is no page.
    assert [(row["path"], row["result"]) for row in listed] == [("wiki/team/new.md", "failed")]
    assert (
        listed[0]["detail"] == "written, and what the server holds now is not one a wiki/page keeps"
    )
    assert code == 1


def test_the_plan_says_beforehand_that_a_new_file_gets_its_identity_and_a_new_name(
    api, tmp_path, monkeypatch
):
    for name, text in {
        "wiki/team/new.md": "---\nycli: wiki/page\ntitle: New\n---\n",
        "tracker/queues/DE/triggers/assign.yaml": "ycli: tracker/trigger\nname: Assign\n",
    }.items():
        (tmp_path / name).parent.mkdir(parents=True)
        (tmp_path / name).write_text(text, encoding="utf-8")
    _, planned, _ = _run(tmp_path, monkeypatch, "--dry-run", "sync", "push")
    assert {row["path"]: row["detail"] for row in planned} == {
        # A trigger lies under its identity, so its file is moved; a page lies where it is.
        "tracker/queues/DE/triggers/assign.yaml": (
            "once created, the file gets its identity and the name of its object"
        ),
        "wiki/team/new.md": "once created, the file gets its identity",
    }
    assert api.calls == []


def test_the_summary_counts_the_files_the_service_added_to(api, tmp_path, monkeypatch):
    second = {**TRIGGER, "id": 17, "self": f"{TRACKER}/queues/DE/triggers/17"}
    for name in ("a", "b"):
        new = tmp_path / f"tracker/queues/DE/triggers/{name}.yaml"
        new.parent.mkdir(parents=True, exist_ok=True)
        new.write_text(
            "ycli: tracker/trigger\nname: Assign on create\n"
            "actions:\n- type: Transition\n  status:\n    key: inProgress\n",
            encoding="utf-8",
        )
    for created in (TRIGGER, second):
        api.add("POST", f"{TRACKER}/queues/DE/triggers", json=created)
        api.add("GET", f"{TRACKER}/queues/DE/triggers/{created['id']}", json=created)
    _, listed, summary = _run(tmp_path, monkeypatch, "sync", "push")
    assert [row["added"] for row in listed] == [True, True]
    assert summary.strip().endswith("0 failed; 2 files now hold what the service added")
