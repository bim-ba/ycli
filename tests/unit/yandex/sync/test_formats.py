"""The two layouts of a file: what they read, what they write, what they refuse."""

from pathlib import PurePosixPath

import pytest

from ycli.yandex.sync.document import Parts, UnreadableFile
from ycli.yandex.sync.formats import MarkdownWithHeader, YAMLFile

PAGE = PurePosixPath("wiki/team/onboarding.md")
TRIGGER = PurePosixPath("tracker/queues/DE/triggers/16.yaml")
PAGE_TEXT = """\
---
ycli: wiki/page
id: 4821
revision: 9917
title: Онбординг
---
# First day

Ask for access to the queue DE.
"""
TRIGGER_TEXT = """\
ycli: tracker/trigger
id: 16
version: 3
name: Assign on create
active: true
conditions:
- type: Event.create
actions:
- type: Transition
  status:
    key: inProgress
"""


def test_a_markdown_file_is_its_header_and_the_text_under_it():
    parts = MarkdownWithHeader().read(PAGE, PAGE_TEXT)
    assert parts == Parts(
        PAGE,
        "wiki/page",
        {"id": 4821, "revision": 9917, "title": "Онбординг"},
        "# First day\n\nAsk for access to the queue DE.\n",
    )
    assert parts.lines == {"ycli": 2, "id": 3, "revision": 4, "title": 5}
    assert MarkdownWithHeader().write(parts) == PAGE_TEXT


def test_a_yaml_file_is_one_mapping_in_the_order_written():
    parts = YAMLFile().read(TRIGGER, TRIGGER_TEXT)
    assert parts.kind == "tracker/trigger" and parts.text is None
    assert list(parts.keys) == ["id", "version", "name", "active", "conditions", "actions"]
    assert parts.keys["actions"] == [{"type": "Transition", "status": {"key": "inProgress"}}]
    assert parts.lines["conditions"] == 6
    assert YAMLFile().write(parts) == TRIGGER_TEXT


@pytest.mark.parametrize(
    "body", ["", "no newline at the end", "\n\nstarts blank\n", "---\nfence\n"]
)
def test_the_text_under_a_header_comes_back_as_it_was(body):
    text = f"---\nycli: wiki/page\nid: 1\n---\n{body}"
    parts = MarkdownWithHeader().read(PAGE, text)
    assert parts.text == body
    assert MarkdownWithHeader().write(parts) == text


def test_a_text_of_several_lines_is_written_as_a_block():
    """One changed line of a description is one line of a diff."""
    parts = Parts(
        TRIGGER, "tracker/macro", {"body": "First line.\nSecond line.\n", "name": "Close"}
    )
    text = YAMLFile().write(parts)
    assert text == "ycli: tracker/macro\nbody: |\n  First line.\n  Second line.\nname: Close\n"
    assert YAMLFile().read(TRIGGER, text) == parts


def test_a_yaml_file_has_no_place_for_a_body():
    with pytest.raises(TypeError, match="written as Markdown"):
        YAMLFile().write(Parts(TRIGGER, "wiki/page", {}, "text"))


@pytest.mark.parametrize(
    ("layout", "text", "line", "reason"),
    [
        (YAMLFile(), "ycli: tracker/trigger\nname: [unclosed\n", 3, "expected"),
        (YAMLFile(), "name: Assign\nid: 16\n", 1, "no `ycli` key"),
        (YAMLFile(), "id: 16\nycli: 7\n", 2, "no `ycli` key"),
        (YAMLFile(), "- a\n- b\n", 1, "a YAML mapping"),
        (YAMLFile(), "", 1, "a YAML mapping"),
        (MarkdownWithHeader(), "# Just a page\n", 1, "starts with a header"),
        (MarkdownWithHeader(), "---\nycli: wiki/page\n# no end\n", 4, "not closed"),
        (MarkdownWithHeader(), "---\nycli: wiki/page\ntitle: [x\n---\ntext\n", 3, "expected"),
        (MarkdownWithHeader(), "---\ntitle: T\n---\ntext\n", 1, "no `ycli` key"),
        (MarkdownWithHeader(), "---\n---\ntext\n", 2, "a YAML mapping"),
    ],
)
def test_a_file_that_is_not_one_is_refused_with_its_path_and_line(layout, text, line, reason):
    with pytest.raises(UnreadableFile) as refusal:
        layout.read(PAGE, text)
    assert (refusal.value.path, refusal.value.line) == (PAGE, line)
    assert reason in refusal.value.reason
