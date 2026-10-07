"""The files of a repository with no network: what each is now, and the two commands."""

import json
from pathlib import Path, PurePosixPath

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli
from ycli.yandex.registry import kinds
from ycli.yandex.sync.document import UnreadableFile, fingerprint
from ycli.yandex.sync.files import FileState, State, examine, read_file
from ycli.yandex.wiki.pages.models import PageUpdate

PAGE = (
    "---\nycli: wiki/page\nid: 4821\nrevision: 9917\nhash: {hash}\ntitle: Onboarding\n---\nText\n"
)
HASH = fingerprint(PageUpdate(title="Onboarding", content="Text\n"))
TRIGGER = "ycli: tracker/trigger\nid: 16\nversion: 3\nname: Assign\n"


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    """A repository with a page as pulled, a page edited since, a new page and a trigger."""
    files = {
        "wiki/team.md": PAGE.format(hash=HASH),
        "wiki/team/edited.md": PAGE.format(hash=HASH).replace("Text", "Text, edited"),
        "wiki/team/new.md": "---\nycli: wiki/page\ntitle: New\n---\nNew text\n",
        "tracker/queues/DE/triggers/16.yaml": TRIGGER,
        "tracker/queues/DE/README.txt": "a file no kind keeps is not looked at",
        "notes.md": "# Not under the directory of a service",
    }
    for name, text in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return tmp_path


def _states(found: list[FileState]) -> dict[str, State]:
    return {file.path: file.state for file in found}


def test_each_file_is_unchanged_edited_or_new_by_its_fingerprint(repository):
    assert _states(examine(repository, [], kinds())) == {
        # It names an object and carries no `hash`: written by hand, never read from it.
        "tracker/queues/DE/triggers/16.yaml": State.UNTRACKED,
        "wiki/team.md": State.UNCHANGED,
        "wiki/team/edited.md": State.EDITED,
        "wiki/team/new.md": State.NEW,
    }


def test_a_run_is_limited_by_a_path(repository):
    under = examine(repository, [PurePosixPath("wiki/team")], kinds())
    assert sorted(_states(under)) == ["wiki/team/edited.md", "wiki/team/new.md"]
    one = examine(repository, [PurePosixPath("wiki/team.md")], kinds())
    assert _states(one) == {"wiki/team.md": State.UNCHANGED}
    assert examine(repository, [PurePosixPath("wiki/nowhere")], kinds()) == []


@pytest.mark.parametrize(
    ("path", "text", "said"),
    [
        ("wiki/broken.md", "---\nycli: wiki/page\ntitle: [x\n---\n", "line 3: "),
        ("wiki/unknown.md", "---\nycli: wiki/grid\n---\n", "line 2: no such kind: wiki/grid"),
        ("wiki/extra.md", "---\nycli: wiki/page\nkeywords: [a]\n---\n", "line 3: keywords: Extra"),
        # A trigger that lies where triggers do not, and a file of a kind with another suffix.
        ("tracker/queues/DE/16.yaml", TRIGGER, "lies at tracker/queues/*/triggers/*.yaml"),
        ("wiki/trigger.md", "---\nycli: tracker/trigger\n---\n", "lies at tracker/queues/*/"),
        # A trigger file copied under another name still holds the id of the first.
        (
            "tracker/queues/DE/triggers/17.yaml",
            TRIGGER,
            "line 2: the file is named 17 and holds 16",
        ),
    ],
)
def test_a_file_that_is_not_one_is_unreadable_and_the_rest_are_still_read(
    repository, path, text, said
):
    (repository / path).write_text(text, encoding="utf-8")
    found = {file.path: file for file in examine(repository, [], kinds())}
    assert found[path].state is State.UNREADABLE and found[path].kind is None
    assert said in (found[path].detail or "")
    assert found["wiki/team.md"].state is State.UNCHANGED


def test_no_kind_keeps_a_file_of_another_suffix():
    by_name = {kind.name: kind for kind in kinds()}
    with pytest.raises(UnreadableFile, match="no kind keeps a file that ends in"):
        read_file(PurePosixPath("wiki/team.txt"), "text", by_name)


def _run(repository: Path, monkeypatch, *argv: str) -> tuple[int, list[dict], str]:
    monkeypatch.chdir(repository)
    result = CliRunner().invoke(cli.app, ["-o", "json", "sync", *argv])
    return result.exit_code, json.loads(result.stdout), result.stderr


def test_sync_status_lists_what_was_edited_and_sums_up(repository, monkeypatch):
    code, listed, summary = _run(repository, monkeypatch, "status")
    assert code == 0
    assert {row["path"]: row["state"] for row in listed} == {
        "tracker/queues/DE/triggers/16.yaml": "untracked",
        "wiki/team/edited.md": "edited",
        "wiki/team/new.md": "new",
    }
    assert summary.strip() == "1 unchanged, 1 edited, 1 new, 1 untracked, 0 unreadable"
    # Changes are an exit code only when asked for: 7, in the one table of every ycli command.
    assert _run(repository, monkeypatch, "status", "--exit-code")[0] == 7
    assert _run(repository, monkeypatch, "status", "--exit-code", "wiki/team.md")[0] == 0
    # The files that were not edited are hidden until asked for.
    _, everything, _ = _run(repository, monkeypatch, "status", "--show-unchanged")
    assert len(everything) == 4
    # A run is limited to kinds without knowing the layout, and to paths.
    _, pages, _ = _run(repository, monkeypatch, "status", "--kind", "wiki/page")
    assert [row["kind"] for row in pages] == ["wiki/page", "wiki/page"]
    _, under, _ = _run(repository, monkeypatch, "status", "tracker")
    assert [row["path"] for row in under] == ["tracker/queues/DE/triggers/16.yaml"]


def test_sync_validate_passes_a_clean_tree_and_fails_on_a_file_that_is_not_one(
    repository, monkeypatch
):
    assert _run(repository, monkeypatch, "validate")[:2] == (0, [])
    (repository / "wiki/extra.md").write_text("---\nycli: wiki/page\nkeywords: [a]\n---\n")
    code, listed, summary = _run(repository, monkeypatch, "validate")
    assert code == 1
    assert [(row["path"], row["state"]) for row in listed] == [("wiki/extra.md", "unreadable")]
    assert "line 3: keywords" in listed[0]["detail"]
    assert "1 unreadable" in summary


def test_a_file_that_cannot_be_read_fails_status_whatever_else_is_there(repository, monkeypatch):
    """An error is more than a change: 1, with `--exit-code` or without, never 7."""
    (repository / "wiki/extra.md").write_text("---\nycli: wiki/page\nkeywords: [a]\n---\n")
    assert _run(repository, monkeypatch, "status")[0] == 1
    assert _run(repository, monkeypatch, "status", "--exit-code")[0] == 1
