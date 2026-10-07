"""`ycli sync pull`: the objects of a service read from the server and written as files."""

import json
import subprocess
from pathlib import Path, PurePosixPath
from typing import Annotated

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli
from ycli.yandex.registry import kinds
from ycli.yandex.sync.document import fingerprint
from ycli.yandex.sync.files import State, examine
from ycli.yandex.sync.git import uncommitted
from ycli.yandex.sync.pull import ScopeError, Sender, pull
from ycli.yandex.wiki.pages.models import PageUpdate

WIKI = "https://api.wiki.yandex.net/v1"
TRACKER = "https://api.tracker.yandex.net/v3"
TEAM = {"id": 4821, "slug": "team", "title": "Team", "page_type": "page", "content": "# Team\n"}
ONBOARDING = {
    "id": 4822,
    "slug": "team/onboarding",
    "title": "Онбординг",
    "page_type": "wysiwyg",
    "content": "Ask for access.\n",
}
ROADMAP = {"id": 4823, "slug": "team/roadmap", "title": "Roadmap", "page_type": "grid"}
TRIGGER = {
    "self": f"{TRACKER}/queues/DE/triggers/16",
    "id": 16,
    "queue": {"key": "DE"},
    "name": "Assign on create",
    "order": "0.0001",
    "actions": [{"type": "Transition", "status": {"key": "inProgress"}}],
    "conditions": [{"type": "Event.create"}],
    "version": 3,
    "active": True,
}


@pytest.fixture
def wiki(api):
    """A page, a page under it, and a grid among them; each with one revision."""
    pages = [TEAM, ONBOARDING, ROADMAP]
    listed = {"results": [{"id": page["id"], "slug": page["slug"]} for page in pages]}
    api.add("GET", f"{WIKI}/pages/descendants", json={**listed, "next_cursor": None})
    for page in pages:
        api.add("GET", f"{WIKI}/pages/{page['id']}", json=page)
        revisions = {"results": [{"id": int(str(page["id"])) + 5000}], "next_cursor": None}
        api.add("GET", f"{WIKI}/pages/{page['id']}/revisions", json=revisions)
    return api


def _run(root: Path, monkeypatch, *argv: str) -> tuple[int, list[dict], str]:
    monkeypatch.chdir(root)
    result = CliRunner().invoke(cli.app, ["-o", "json", *argv])
    listed = json.loads(result.stdout) if result.stdout.strip() else []
    return result.exit_code, listed, result.stderr


def test_a_tree_of_pages_is_written_and_what_no_kind_keeps_is_named(wiki, tmp_path, monkeypatch):
    code, listed, summary = _run(tmp_path, monkeypatch, "sync", "pull", "wiki/team")
    assert code == 0, summary
    assert [(row["path"], row["action"]) for row in listed] == [
        ("wiki/team.md", "written"),
        ("wiki/team/onboarding.md", "written"),
        ("wiki/team/roadmap.md", "skipped"),  # a grid holds no Markdown: `only` leaves it out
    ]
    assert listed[2]["detail"] == "not an object this kind keeps"
    assert summary.strip() == "2 written, 0 unchanged, 1 skipped"
    assert not (tmp_path / "wiki/team/roadmap.md").exists()
    # The file: the link first (identity, the version under the service's word, the
    # fingerprint), then the content as the request that changes the page carries it.
    held = fingerprint(PageUpdate(title="Онбординг", content="Ask for access.\n"))
    assert (tmp_path / "wiki/team/onboarding.md").read_text("utf-8") == (
        f"---\nycli: wiki/page\nhash: {held}\nid: 4822\nrevision: 9822\ntitle: Онбординг\n---\n"
        "Ask for access.\n"
    )
    # The listing asked for the page itself too, and each read asked for the content.
    assert wiki.calls[0].url.params["slug"] == "team"
    assert wiki.calls[0].url.params["include_self"] == "true"
    assert wiki.calls[1].url.params["fields"] == "content"
    # What was written is what `status` calls unchanged.
    states = {file.path: file.state for file in examine(tmp_path, [], kinds())}
    assert set(states.values()) == {State.UNCHANGED}


def test_a_second_pull_writes_nothing_and_says_so(wiki, tmp_path, monkeypatch):
    _run(tmp_path, monkeypatch, "sync", "pull", "wiki/team")
    before = (tmp_path / "wiki/team.md").stat().st_mtime_ns
    code, listed, summary = _run(tmp_path, monkeypatch, "sync", "pull", "wiki/team")
    assert (code, summary.strip()) == (0, "0 written, 2 unchanged, 1 skipped")
    assert [row["action"] for row in listed] == ["skipped"]  # unchanged files are hidden
    assert (tmp_path / "wiki/team.md").stat().st_mtime_ns == before
    _, everything, _ = _run(tmp_path, monkeypatch, "sync", "pull", "wiki/team", "--show-unchanged")
    assert len(everything) == 3


def test_a_pull_overwrites_a_local_edit(wiki, tmp_path, monkeypatch):
    """Git is what protects an edit: `pull` writes what the server has."""
    _run(tmp_path, monkeypatch, "sync", "pull", "wiki/team")
    page = tmp_path / "wiki/team.md"
    pulled = page.read_text("utf-8")
    page.write_text(pulled.replace("# Team", "# Team, edited"), encoding="utf-8")
    _, listed, _ = _run(tmp_path, monkeypatch, "sync", "pull", "wiki/team")
    assert ("wiki/team.md", "written") in [(row["path"], row["action"]) for row in listed]
    assert page.read_text("utf-8") == pulled


def test_a_dry_run_writes_nothing_and_names_the_uncommitted_work_it_would_overwrite(
    wiki, tmp_path, monkeypatch
):
    _run(tmp_path, monkeypatch, "sync", "pull", "wiki/team")
    for command in (["init", "-q"], ["add", "."]):
        subprocess.run(["git", *command], cwd=tmp_path, check=True)
    commit = ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "pulled"]
    subprocess.run(["git", *commit], cwd=tmp_path, check=True)
    page = tmp_path / "wiki/team.md"
    edited = page.read_text("utf-8").replace("# Team", "# Team, edited")
    page.write_text(edited, encoding="utf-8")
    code, listed, summary = _run(tmp_path, monkeypatch, "--dry-run", "sync", "pull", "wiki/team")
    assert code == 0
    by_path = {row["path"]: row for row in listed}
    # Nothing was written, and neither the action nor the summary says it was.
    assert by_path["wiki/team.md"]["action"] == "would write"
    assert summary.strip() == "1 would write, 1 unchanged, 1 skipped"
    assert by_path["wiki/team.md"]["detail"] == "would overwrite uncommitted work"
    assert page.read_text("utf-8") == edited  # nothing was written


def test_the_triggers_of_a_queue_lie_under_it(api, tmp_path, monkeypatch):
    api.add("GET", f"{TRACKER}/queues/DE/triggers", json=[TRIGGER])
    api.add("GET", f"{TRACKER}/queues/DE/triggers/16", json=TRIGGER)
    code, listed, summary = _run(tmp_path, monkeypatch, "sync", "pull", "tracker/queues/DE")
    assert code == 0, summary
    assert [(row["path"], row["kind"]) for row in listed] == [
        ("tracker/queues/DE/triggers/16.yaml", "tracker/trigger")
    ]
    text = (tmp_path / "tracker/queues/DE/triggers/16.yaml").read_text("utf-8")
    # The version comes with the reply; what belongs to the server is not in the file.
    assert text.startswith("ycli: tracker/trigger\nhash: ")
    assert "\nid: 16\nversion: 3\nname: Assign on create\n" in text
    assert "self:" not in text and "order:" not in text and "queue:" not in text
    assert "actions:\n- type: Transition\n  status:\n    key: inProgress\n" in text


@pytest.mark.parametrize(
    ("path", "said"),
    [
        ("wiki", "name what to pull: wiki/<place>"),
        ("tracker", "name where to pull from: tracker/queues"),
        ("tracker/boards/7", "name where to pull from: tracker/queues"),
        ("forms/surveys", "no kind keeps files under forms/surveys"),
    ],
)
def test_a_path_that_names_nothing_to_fetch_is_refused_before_a_request(
    api, tmp_path, monkeypatch, path, said
):
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli.app, ["sync", "pull", path])
    assert result.exit_code == 2 and api.calls == []
    assert said in result.output


def _nobody(service: str) -> Sender:
    raise AssertionError(f"no request is sent, so no client of {service} is asked for")


def test_a_kind_the_api_cannot_list_says_so(tmp_path):
    from dataclasses import replace

    from ycli.yandex.tracker.triggers.sync import TRIGGER as KIND

    with pytest.raises(ScopeError, match="the API cannot list the objects of tracker/trigger"):
        pull(tmp_path, PurePosixPath("tracker/queues/DE"), [replace(KIND, find=None)], _nobody)


def test_outside_a_repository_git_names_nothing(tmp_path):
    assert uncommitted(tmp_path, []) == set()
    assert uncommitted(tmp_path, [PurePosixPath("wiki/team.md")]) == set()


def test_a_file_names_one_object_of_what_its_container_lists(wiki, tmp_path, monkeypatch):
    """A path limits a run: the page and what lies under it, nothing beside it."""
    _, listed, summary = _run(tmp_path, monkeypatch, "sync", "pull", "wiki/team/onboarding.md")
    assert [row["path"] for row in listed] == ["wiki/team/onboarding.md"]
    assert summary.strip() == "1 written, 0 unchanged, 0 skipped"
    assert wiki.calls[0].url.params["slug"] == "team/onboarding"
    assert not (tmp_path / "wiki/team.md").exists()


def test_a_page_with_no_revision_listed_has_no_version_in_its_file(api, tmp_path, monkeypatch):
    api.add("GET", f"{WIKI}/pages/descendants", json={"results": [{"id": 4821, "slug": "team"}]})
    api.add("GET", f"{WIKI}/pages/4821", json=TEAM)
    api.add("GET", f"{WIKI}/pages/4821/revisions", json={"results": []})
    _run(tmp_path, monkeypatch, "sync", "pull", "wiki/team")
    text = (tmp_path / "wiki/team.md").read_text("utf-8")
    assert "\nid: 4821\ntitle: Team\n" in text and "revision" not in text


def test_a_kind_of_a_service_with_no_version_carries_the_fingerprint_alone(api, tmp_path):
    """Seven resources in ten have no version: the link is the identity and the `hash`."""
    from dataclasses import replace

    from pydantic import Field

    from ycli.yandex.sync.document import Link
    from ycli.yandex.sync.kind import NoVersion
    from ycli.yandex.sync.marks import Identity
    from ycli.yandex.tracker.client import TrackerClient
    from ycli.yandex.tracker.triggers.sync import TRIGGER as KIND

    class Bare(Link):
        id: Annotated[int | None, Identity()] = Field(default=None, description="Id.")

    api.add("GET", f"{TRACKER}/queues/DE/triggers", json=[TRIGGER])
    api.add("GET", f"{TRACKER}/queues/DE/triggers", json=[])  # the page after the last
    api.add("GET", f"{TRACKER}/queues/DE/triggers/16", json=TRIGGER)
    bare = replace(KIND, link=Bare, version=NoVersion())
    client = TrackerClient(oauth_token="t", organization_id="o")
    done = pull(tmp_path, PurePosixPath("tracker/queues/DE"), [bare], lambda service: client)
    assert [one.path for one in done] == ["tracker/queues/DE/triggers/16.yaml"]
    text = (tmp_path / "tracker/queues/DE/triggers/16.yaml").read_text("utf-8")
    assert "\nid: 16\nname: Assign on create\n" in text and "version" not in text
