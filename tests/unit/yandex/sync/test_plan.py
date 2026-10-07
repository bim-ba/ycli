"""`ycli sync diff`: each file against the object it stands for, as the server has it now."""

import json
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path, PurePosixPath
from typing import Any

from pydantic import SecretStr
from typer.testing import CliRunner

import ycli.cli.app as cli
from ycli.yandex.models import RequestBody
from ycli.yandex.sync.document import Document, Link, fingerprint
from ycli.yandex.sync.files import State, offline_state, read_file
from ycli.yandex.sync.plan import compared, difference
from ycli.yandex.tracker.triggers.sync import TRIGGER as TRIGGER_KIND

WIKI = "https://api.wiki.yandex.net/v1"
TEAM = {"id": 4821, "slug": "team", "title": "Team", "page_type": "page", "content": "# Team\n"}
CHILD = {
    "id": 4822,
    "slug": "team/onboarding",
    "title": "Onboarding",
    "page_type": "page",
    "content": "Ask for access.\n",
}
GRID = {"id": 4823, "slug": "team/roadmap", "title": "Roadmap", "page_type": "grid"}


def _serve(api, page: dict, revision: int, status: int = 200) -> None:
    """One more answer about ``page``: the one before it is given once, the last one repeats."""
    api.add("GET", f"{WIKI}/pages/{page['id']}", json=page, status=status)
    revisions = {"results": [{"id": revision}], "next_cursor": None}
    api.add("GET", f"{WIKI}/pages/{page['id']}/revisions", json=revisions)


def _run(root: Path, monkeypatch, *argv: str) -> tuple[int, list[dict], str]:
    monkeypatch.chdir(root)
    result = CliRunner().invoke(cli.app, ["-o", "json", "sync", *argv])
    listed = json.loads(result.stdout) if result.stdout.strip() else []
    return result.exit_code, listed, result.stderr


def _pulled(
    api, root: Path, monkeypatch, *pages: dict, later: Sequence[tuple[Any, ...]] = ()
) -> None:
    """The files of ``pages`` as `pull` writes them at revision 1.

    ``later`` are the answers after that pull, ``(page, revision)`` or ``(page, revision,
    status)``: the mock gives an answer once while another one waits, so they are said first.
    """
    listed = {"results": [{"id": page["id"], "slug": page["slug"]} for page in pages]}
    api.add("GET", f"{WIKI}/pages/descendants", json={**listed, "next_cursor": None})
    for page in pages:
        _serve(api, page, 1)
    for answer in later:
        _serve(api, *answer)
    code, _, summary = _run(root, monkeypatch, "pull", "wiki/team")
    assert code == 0, summary


def _states(listed: list[dict]) -> dict[str, str]:
    return {row["path"]: row["state"] for row in listed}


def test_nothing_changed_is_nothing_to_show(api, tmp_path, monkeypatch):
    _pulled(api, tmp_path, monkeypatch, TEAM, CHILD)
    code, listed, summary = _run(tmp_path, monkeypatch, "diff", "--exit-code")
    assert (code, listed) == (0, [])
    assert summary.strip().endswith(
        "2 unchanged, 0 update, 0 create, 0 untracked, 0 unsupported, 0 unreadable, "
        "0 changed-on-server, 0 gone, 0 no-file"
    )
    _, everything, _ = _run(tmp_path, monkeypatch, "diff", "--show-unchanged")
    assert _states(everything) == {
        "wiki/team.md": "unchanged",
        "wiki/team/onboarding.md": "unchanged",
    }
    assert everything[0]["diff"] is None


def test_an_edited_file_is_shown_against_the_server_and_counts_as_a_change(
    api, tmp_path, monkeypatch
):
    _pulled(api, tmp_path, monkeypatch, TEAM, CHILD)
    page = tmp_path / "wiki/team.md"
    page.write_text(page.read_text("utf-8").replace("# Team", "# Team, edited"), encoding="utf-8")
    code, listed, _ = _run(tmp_path, monkeypatch, "diff", "--exit-code")
    assert code == 7
    assert _states(listed) == {"wiki/team.md": "update"}
    difference_ = listed[0]["diff"]
    # From the server to the file; the link of the file is on both sides and is no change.
    assert difference_.startswith("--- server/wiki/team.md\n+++ local/wiki/team.md\n")
    assert "-# Team\n+# Team, edited\n" in difference_
    changed = [line for line in difference_.splitlines() if line[:1] in "+-"][2:]
    assert changed == ["-# Team", "+# Team, edited"]
    # Without the flag a change is no failure.
    assert _run(tmp_path, monkeypatch, "diff")[0] == 0


def test_an_object_that_changed_on_the_server_outweighs_a_change_to_push(
    api, tmp_path, monkeypatch
):
    theirs = {**TEAM, "content": "# Team, by somebody else\n"}
    _pulled(api, tmp_path, monkeypatch, TEAM, CHILD, later=[(theirs, 2)])
    child = tmp_path / "wiki/team/onboarding.md"
    child.write_text(child.read_text("utf-8") + "More.\n", encoding="utf-8")
    code, listed, _ = _run(tmp_path, monkeypatch, "diff", "--exit-code")
    assert code == 8  # the two went apart: more than something to push
    assert _states(listed) == {
        "wiki/team.md": "changed-on-server",
        "wiki/team/onboarding.md": "update",
    }
    assert "-# Team, by somebody else\n+# Team\n" in listed[0]["diff"]


def test_a_new_version_with_the_same_content_is_a_change_on_the_server_too(
    api, tmp_path, monkeypatch
):
    """The version is compared beside the fingerprint: somebody saved it, whatever they saved."""
    _pulled(api, tmp_path, monkeypatch, TEAM, later=[(TEAM, 2)])
    _, listed, _ = _run(tmp_path, monkeypatch, "diff")
    assert (_states(listed), listed[0]["diff"]) == ({"wiki/team.md": "changed-on-server"}, None)


def test_an_object_that_is_gone_is_said(api, tmp_path, monkeypatch):
    _pulled(api, tmp_path, monkeypatch, TEAM, later=[({"id": 4821}, 1, 404)])
    code, listed, _ = _run(tmp_path, monkeypatch, "diff", "--exit-code", "wiki/team.md")
    assert (code, _states(listed)) == (8, {"wiki/team.md": "gone"})


def test_a_file_written_by_hand_is_to_create_or_is_untracked(api, tmp_path, monkeypatch):
    _pulled(api, tmp_path, monkeypatch, TEAM)
    (tmp_path / "wiki/team").mkdir()
    (tmp_path / "wiki/team/new.md").write_text("---\nycli: wiki/page\ntitle: New\n---\nText\n")
    (tmp_path / "wiki/team.md").write_text(
        "---\nycli: wiki/page\nid: 4821\ntitle: Team\n---\n# Mine\n", encoding="utf-8"
    )
    before = len(api.calls)
    code, listed, _ = _run(
        tmp_path, monkeypatch, "diff", "--exit-code", "wiki/team.md", "wiki/team/new.md"
    )
    assert _states(listed) == {"wiki/team.md": "untracked", "wiki/team/new.md": "create"}
    assert "-# Team\n+# Mine\n" in listed[0]["diff"]
    assert code == 8  # an untracked file is not pushed until it is pulled
    # A file that names no object is read from nowhere.
    assert all("4821" in str(call.url) for call in api.calls[before:])


def test_under_a_container_an_object_with_no_file_is_said(api, tmp_path, monkeypatch):
    _pulled(api, tmp_path, monkeypatch, TEAM, CHILD, GRID)
    (tmp_path / "wiki/team/onboarding.md").unlink()
    _, listed, _ = _run(tmp_path, monkeypatch, "diff", "wiki/team")
    # The page with no file is said; the grid, which no kind keeps, is not.
    assert _states(listed) == {"wiki/team/onboarding.md": "no-file"}
    assert listed[0]["detail"] == "`ycli sync pull` writes it"
    # A directory names the page beside it too, as `pull wiki/team` writes both.
    _, everything, _ = _run(tmp_path, monkeypatch, "diff", "wiki/team", "--show-unchanged")
    assert _states(everything)["wiki/team.md"] == "unchanged"
    # Named as a file, nothing lists the container: there is nothing to say.
    assert _run(tmp_path, monkeypatch, "diff", "wiki/team.md")[1] == []


def test_a_file_for_an_object_its_kind_does_not_keep_is_unsupported(api, tmp_path, monkeypatch):
    _pulled(api, tmp_path, monkeypatch, TEAM, GRID)
    grid = tmp_path / "wiki/team/roadmap.md"
    grid.parent.mkdir()
    grid.write_text("---\nycli: wiki/page\nhash: sha256:0\nid: 4823\ntitle: Roadmap\n---\n")
    _, listed, _ = _run(tmp_path, monkeypatch, "diff", "wiki/team/roadmap.md")
    assert _states(listed) == {"wiki/team/roadmap.md": "unsupported"}
    assert listed[0]["detail"] == "the object is not one a wiki/page file keeps"


def test_a_file_that_cannot_be_read_fails_the_run_and_a_kind_limits_it(api, tmp_path, monkeypatch):
    _pulled(api, tmp_path, monkeypatch, TEAM)
    (tmp_path / "wiki/broken.md").write_text("---\nycli: wiki/page\nkeywords: [a]\n---\n")
    code, listed, _ = _run(tmp_path, monkeypatch, "diff")
    assert (code, _states(listed)) == (1, {"wiki/broken.md": "unreadable"})
    assert "line 3" in listed[0]["detail"]
    assert _run(tmp_path, monkeypatch, "diff", "--kind", "tracker/trigger")[1] == []


def test_what_the_api_of_a_kind_cannot_do_is_said_with_no_network():
    text = "ycli: tracker/trigger\nid: 16\nhash: sha256:0\nname: Renamed\n"
    path = PurePosixPath("tracker/queues/DE/triggers/16.yaml")
    read_only = replace(TRIGGER_KIND, update=None, create=None)
    _, edited = read_file(path, text, {"tracker/trigger": read_only})
    assert offline_state(read_only, edited) == (
        State.UNSUPPORTED,
        "the API cannot update a tracker/trigger",
    )
    _, new = read_file(
        PurePosixPath("tracker/queues/DE/triggers/new.yaml"),
        "ycli: tracker/trigger\nname: New\n",
        {"tracker/trigger": read_only},
    )
    assert offline_state(read_only, new)[1] == "the API cannot create a tracker/trigger"


class Hook(RequestBody):
    url: str
    token: SecretStr | None = None


def _hook(url: str, token: str) -> Document[Link, Hook]:
    content = Hook(url=url, token=SecretStr(token))
    path = PurePosixPath("tracker/queues/DE/triggers/16.yaml")
    return Document(path=path, link=Link(hash=fingerprint(content)), content=content)


def test_a_secret_is_masked_on_both_sides_and_named_when_it_differs():
    kind = replace(TRIGGER_KIND, content=Hook, link=Link)
    text, changed = difference(kind, _hook("https://b", "mine"), _hook("https://a", "theirs"))
    assert "-url: https://a\n+url: https://b\n" in text
    assert "mine" not in text and "theirs" not in text and changed == ["token"]
    # The same secret on both sides is no change, and nothing of it is shown.
    assert difference(kind, _hook("https://a", "one"), _hook("https://a", "one")) == ("", [])
    shown, _ = difference(
        kind, _hook("https://a", "mine"), _hook("https://a", "theirs"), show_secrets=True
    )
    assert "-token: theirs\n+token: mine\n" in shown
    # In the plan a secret that differs is named beside the state, never shown.
    server = _hook("https://a", "theirs")
    edited = _hook("https://a", "mine").model_copy(update={"link": server.link})
    planned = compared(kind, edited, server, show_secrets=False)
    assert (planned.state, planned.detail) == (State.UPDATE, "secret changed: token")
    assert "mine" not in (planned.diff or "") and "theirs" not in (planned.diff or "")
