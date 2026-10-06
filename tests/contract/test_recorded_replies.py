"""Every recorded reply of the real API is one the model of its operation reads (#143).

``tests/fixtures/replies/<service>/<resource>/<method>.json`` holds what the API answered an
operation with, recorded by ``pytest e2e --record`` and scrubbed (``e2e/recording.py``). The
hand-written reply of a contract case says what ycli expects; this says what the API sends.
A fixture also counts the keys its model does not know; that number may only go down.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx2
import pytest
from e2e.recording import REPLIES, load, reply_type
from e2e.scrub import scrub

from tests.contract import Sibling, load_cases
from tests.contract.test_contract import SERVICE_BY_NAME, _client
from ycli.yandex.core.endpoint import ENDPOINT_EXTENSION
from ycli.yandex.errors import YandexUnexpectedReplyError

if TYPE_CHECKING:
    from pathlib import Path

    from tests.contract import Case
    from ycli.yandex.core.endpoint import Endpoint

FIRST_CASE: dict[str, Case] = {}
for _case in load_cases():
    FIRST_CASE.setdefault(_case.operation, _case)


class _Asked(BaseException):
    """Stops an operation at its first request; not an ``Exception``, so nothing handles it."""

    def __init__(self, request: httpx2.Request) -> None:
        super().__init__()
        self.endpoint: Endpoint = request.extensions[ENDPOINT_EXTENSION]


def _stop(request: httpx2.Request) -> httpx2.Response:
    raise _Asked(request)


def first_endpoint(case: Case, monkeypatch: pytest.MonkeyPatch) -> Endpoint:
    """The endpoint ``case``'s operation sends first."""
    monkeypatch.setattr(
        "ycli.yandex.core.session.default_transport", lambda: httpx2.MockTransport(_stop)
    )
    domain, resource, method = case.operation.split(".")
    with _client(SERVICE_BY_NAME[domain]) as client:
        args = [getattr(client, a.resource) if isinstance(a, Sibling) else a for a in case.args]
        try:
            getattr(getattr(client, resource), method)(*args, **case.kwargs)
        except _Asked as asked:
            return asked.endpoint
    raise AssertionError(f"{case.operation} sent no request")


def _reply(status: int, body: object) -> httpx2.Response:
    """A reply as the core hands it to an endpoint: it names the request it answers."""
    return httpx2.Response(status, json=body, request=httpx2.Request("GET", "https://api.test"))


def _operation(path: Path) -> str:
    return ".".join(path.relative_to(REPLIES).with_suffix("").parts)


@pytest.mark.parametrize("path", sorted(REPLIES.glob("*/*/*.json")), ids=_operation)
def test_a_recorded_reply_is_read_by_the_model_of_its_operation(path: Path, monkeypatch):
    case = FIRST_CASE.get(_operation(path))
    assert case is not None, f"{path}: a fixture of an operation that no longer exists"
    fixture = load(path)
    if "body" not in fixture:
        return  # a reply that is not JSON: only its status was kept
    endpoint = first_endpoint(case, monkeypatch)
    endpoint.parse(_reply(fixture["status"], fixture["body"]))
    # The ratchet: a model may learn a key the API sends, never forget one.
    unknown = set(scrub(fixture["body"], reply_type(endpoint)).unknown_keys)
    assert len(unknown) <= fixture["unknown_keys"], (
        f"{_operation(path)}: the model no longer knows {sorted(unknown)}"
    )


def test_the_check_bites(monkeypatch):
    """A reply whose required field changed type is refused."""
    endpoint = first_endpoint(FIRST_CASE["tracker.issues.get"], monkeypatch)
    endpoint.parse(_reply(200, {"key": "DE-7"}))
    with pytest.raises(YandexUnexpectedReplyError, match="does not fit what ycli expects"):
        endpoint.parse(_reply(200, {"key": ["DE-7"]}))
