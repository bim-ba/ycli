"""Where the files of a kind lie, and what a path says of its object."""

from pathlib import PurePosixPath

import pytest

from ycli.yandex.sync.document import UnreadableFile
from ycli.yandex.sync.paths import Tree, tree_of
from ycli.yandex.tracker.triggers.sync import TRIGGER
from ycli.yandex.wiki.pages.sync import PAGE

TRIGGERS = Tree("tracker", ("queues",), "triggers", ".yaml")
PAGES = Tree("wiki", (), None, ".md")


def test_the_layout_of_a_kind_comes_from_its_declaration_and_its_marks():
    """The container is named by `Container(queues)`, the resource by where the operation lies."""
    assert tree_of(TRIGGER) == TRIGGERS
    # A page says where it lies itself (`slug` is marked `Place`): no directory of its own.
    assert tree_of(PAGE) == PAGES


def test_a_path_is_built_and_taken_apart_the_same_way():
    path = TRIGGERS.path(("DE",), "16")
    assert path == PurePosixPath("tracker/queues/DE/triggers/16.yaml")
    assert TRIGGERS.split(path) == (("DE",), "16")
    page = PAGES.path((), "team/onboarding")
    assert page == PurePosixPath("wiki/team/onboarding.md")
    assert PAGES.split(page) == ((), "team/onboarding")
    assert PAGES.split(PurePosixPath("wiki/team.md")) == ((), "team")


@pytest.mark.parametrize(
    ("tree", "path"),
    [
        (TRIGGERS, "tracker/queues/DE/triggers/16.md"),  # another suffix
        (TRIGGERS, "tracker/queues/DE/16.yaml"),  # not under its resource
        (TRIGGERS, "tracker/queues/DE/triggers/old/16.yaml"),  # an identity is one part
        (TRIGGERS, "tracker/boards/DE/triggers/16.yaml"),  # another container
        (TRIGGERS, "wiki/queues/DE/triggers/16.yaml"),  # another service
        (PAGES, "tracker/team.md"),
        (PAGES, "wiki/team.yaml"),
        (PAGES, "wiki.md"),  # no place under the service at all
    ],
)
def test_a_path_that_does_not_fit_the_layout_is_refused(tree, path):
    with pytest.raises(UnreadableFile) as refusal:
        tree.split(PurePosixPath(path))
    assert "a file of this kind lies at" in refusal.value.reason
    assert refusal.value.reason.endswith(("tracker/queues/*/triggers/*.yaml", "wiki/*.md"))
