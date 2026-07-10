"""TDD for OperationsClient — clone-status reads plus the ``poll()`` --wait path."""

import requests
import responses

from ycli.yandex.polling import poll
from ycli.yandex.wiki.operations.client import OperationsClient
from ycli.yandex.wiki.operations.models import (
    CloneOperationStatus,
    GridCloneOperationStatus,
)

BASE = "https://api.wiki.yandex.net/v1"


def _client() -> OperationsClient:
    session = requests.Session()
    session.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return OperationsClient(session=session)


@responses.activate
def test_clone_get_deserializes_status():
    responses.add(
        responses.GET,
        f"{BASE}/operations/clone/task-1",
        json={"status": "success", "result": {"page": {"id": 42, "slug": "data/y"}}},
        status=200,
    )
    out = _client().clone_get("task-1")
    assert isinstance(out, CloneOperationStatus)
    assert out.is_terminal is True
    assert out.result is not None and out.result.page is not None
    assert out.result.page.slug == "data/y"


@responses.activate
def test_gridclone_get_deserializes_status():
    responses.add(
        responses.GET,
        f"{BASE}/operations/clone_inline_grid/task-1",
        json={"status": "in_progress", "progress": {"percentage": 0.5}},
        status=200,
    )
    out = _client().gridclone_get("task-1")
    assert isinstance(out, GridCloneOperationStatus)
    assert out.is_terminal is False
    assert out.progress is not None and out.progress.percentage == 0.5


@responses.activate
def test_wait_polls_clone_until_terminal():
    """The ``--wait`` path: poll() re-reads the clone status until it is terminal.

    Two-status sequence (scheduled → success) with a recorder ``sleep`` (no real waiting): the
    loop fetches twice, sleeps exactly once in between, and returns the terminal status.
    """
    responses.add(
        responses.GET, f"{BASE}/operations/clone/task-1", json={"status": "scheduled"}, status=200
    )
    responses.add(
        responses.GET,
        f"{BASE}/operations/clone/task-1",
        json={"status": "success", "result": {"page": {"id": 42, "slug": "data/y"}}},
        status=200,
    )
    client = _client()
    slept: list[float] = []
    final = poll(
        lambda: client.clone_get("task-1"),
        lambda state: state.is_terminal,
        sleep=slept.append,
    )
    assert final.status == "success"
    assert final.is_terminal is True
    assert len(responses.calls) == 2  # fetched twice
    assert slept == [0.5]  # slept once between the two fetches (default backoff)
