"""DomainClient: one core session per domain client, closed with it; no empty credential."""

from http import HTTPMethod

import httpx2
import pytest
from pydantic import SecretStr, ValidationError

from tests.hosts import WIKI_BASE
from tests.mock_api import MockAPI
from ycli.yandex.base import DomainClient
from ycli.yandex.core.auth import IAMTokenAuth
from ycli.yandex.core.endpoint import Endpoint, Paged
from ycli.yandex.core.guard import RequestPlanned
from ycli.yandex.core.session import SyncSession
from ycli.yandex.errors import YandexError, YandexInvalidRequestError, YandexNotFoundError
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.registry import SERVICES
from ycli.yandex.tracker.boards.models import BoardUpdate
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.wiki.access.models import PageAccessCreate
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.cursor import WIKI_CURSOR


def test_an_empty_organization_is_refused_before_any_request():
    with pytest.raises(
        ValueError, match="TrackerClient needs an organization: set YANDEX_ID_ORGANIZATION_ID or "
    ):
        TrackerClient(oauth_token="t", organization_id="")


@pytest.mark.parametrize(
    "credential", [{}, {"oauth_token": ""}, {"oauth_token": "t", "auth": httpx2.Auth()}]
)
def test_exactly_one_way_to_sign_in_is_required(credential):
    with pytest.raises(ValueError, match="one of the two"):
        TrackerClient(organization_id="o", **credential)


def test_any_auth_signs_the_requests_in_place_of_the_oauth_token():
    api = MockAPI()
    api.add("GET", "https://api.tracker.yandex.net/v3/myself", json={"login": "ivan"})
    auth = IAMTokenAuth(SecretStr("t1.secret"))
    with TrackerClient(auth=auth, organization_id="o", transport=api.transport()) as client:
        client.me.get()
    assert api.calls[0].headers["Authorization"] == "Bearer t1.secret"


def test_leaving_the_with_block_closes_the_session():
    with TrackerClient(oauth_token="t", organization_id="o") as client:
        core = client.issues._session._client
        assert not core.is_closed
        assert client.queues._session is client.issues._session
    assert core.is_closed


@pytest.mark.parametrize(
    ("client_class", "url"),
    [
        (TrackerClient, "https://api.tracker.yandex.net/v3/myself"),
        (WikiClient, "https://api.wiki.yandex.net/v1/users/me"),
        (FormsClient, "https://api.forms.yandex.net/v1/users/me"),
    ],
)
def test_a_probe_is_one_read_of_the_services_own_me_endpoint(api, client_class, url):
    api.add("GET", url, json={})
    with client_class(oauth_token="t", organization_id="o") as client:
        client.probe()
    assert [str(call.url) for call in api.calls] == [url]


def test_a_client_sends_any_endpoint_through_its_session(api):
    api.add("GET", f"{WIKI_BASE}/x", json={"results": [1]})
    with WikiClient(oauth_token="t", organization_id="o") as client:
        assert client.send(Endpoint(HTTPMethod.GET, "x", dict)) == {"results": [1]}


def test_a_client_walks_any_listing_through_its_session(api):
    api.add("GET", f"{WIKI_BASE}/x", json={"results": [1, 2], "next_cursor": "c"})
    api.add("GET", f"{WIKI_BASE}/x", json={"results": [3]})
    paged = Paged(Endpoint(HTTPMethod.GET, "x", dict), WIKI_CURSOR, lambda page: page["results"])
    with WikiClient(oauth_token="t", organization_id="o") as client:
        assert list(client.iterate(paged, limit=3)) == [1, 2, 3]


BOARD = "https://api.tracker.yandex.net/v3/boards/31"


def test_a_plan_is_the_first_write_of_a_call_and_nothing_of_it_is_sent(api):
    """`plan`: what the call reads before its first write is read; the write is given back."""
    api.add("GET", BOARD, json={"id": 31, "name": "Old"})
    api.add("PATCH", BOARD, json={"id": 31})
    api.add("DELETE", BOARD, status=204)

    def rename_then_delete(tracker: TrackerClient) -> None:
        name = tracker.boards.get(31).name
        tracker.boards.update(31, BoardUpdate(name=f"{name}!"))
        tracker.boards.delete(31)  # never reached: the plan is of the first write

    with TrackerClient(oauth_token="t", organization_id="o") as tracker:
        planned = tracker.plan(rename_then_delete)
        assert (planned.method, planned.url, planned.body) == ("PATCH", BOARD, {"name": "Old!"})
        assert planned.grants_access is False
        assert [call.method for call in api.calls] == ["GET"]
        # The client itself is as it was: the same call through it is sent.
        tracker.boards.delete(31)
        assert [call.method for call in api.calls] == ["GET", "DELETE"]


def test_a_plan_of_a_call_that_writes_nothing_is_an_error_and_a_grant_says_what_it_is(api):
    api.add("GET", BOARD, json={"id": 31})
    tracker = TrackerClient(oauth_token="t", organization_id="o")
    refused = pytest.raises(YandexInvalidRequestError, match="sends no write: nothing to plan")
    with tracker, refused:
        tracker.plan(lambda tracker: tracker.boards.get(31))
    body = PageAccessCreate.model_validate({"role": "editor", "user": {"uid": "9001"}})
    with WikiClient(oauth_token="t", organization_id="o") as wiki:
        planned = wiki.plan(lambda wiki: wiki.access.create(7, body))
    assert planned.grants_access is True and planned.method == "POST"
    assert [call.method for call in api.calls] == ["GET"]


def test_a_view_with_other_options_shares_the_connections_and_changes_only_its_calls(api):
    """`with_options`: a timeout and a number of retries for the calls made through the view."""
    api.add("GET", BOARD, status=500, json={})
    with TrackerClient(oauth_token="t", organization_id="o") as tracker:
        view = tracker.with_options(timeout_seconds=120, retries=0)
        assert type(view) is TrackerClient and view is not tracker
        assert view.boards._session._client is tracker.boards._session._client
        with pytest.raises(YandexError):
            view.boards.get(31)
        assert len(api.calls) == 1  # not tried again
        assert api.calls[0].extensions["timeout"]["read"] == 120
        # The client it came from keeps its own.
        assert tracker._session._attempts == 4 and tracker._session._timeout_seconds is None
        # One option changed keeps the other: a view of a view.
        again = view.with_options(retries=2)
        assert (again._session._timeout_seconds, again._session._attempts) == (120, 3)
        with pytest.raises(ValidationError):
            tracker.with_options(retries=-1)
        with pytest.raises(ValidationError):
            tracker.with_options(timeout_seconds=0)
        # A view has no connections of its own to close.
        with view:
            pass
        assert not tracker.boards._session._client.is_closed
    assert tracker.boards._session._client.is_closed


def test_dry_run_can_be_turned_on_and_off_for_a_view(api):
    api.add("DELETE", BOARD, status=204)
    with TrackerClient(oauth_token="t", organization_id="o") as tracker:
        careful = tracker.with_options(dry_run=True)
        with pytest.raises(RequestPlanned):
            careful.boards.delete(31)
        assert api.calls == []
        careful.with_options(dry_run=False).boards.delete(31)
        assert [call.method for call in api.calls] == ["DELETE"]


def _clients() -> list[DomainClient]:
    """One client of every service, signed in the way the service takes."""
    made: list[DomainClient] = []
    for service in SERVICES:
        client_class = service.client_class()
        auth = None if service.profile.oauth_token else IAMTokenAuth(SecretStr("t"))
        token = "t" if service.profile.oauth_token else None
        made.append(
            client_class(
                oauth_token=token, auth=auth, organization_id="o", cloud_organization_id="c"
            )
        )
    return made


def _session_holders(client: DomainClient) -> dict[str, tuple[object, SyncSession]]:
    """Every object reachable from ``client`` that holds a session: its path, itself, the session.

    Walked through attributes, and through lists, tuples and dicts of them, to any depth: a
    resource of a resource, or a helper that was handed the session, is found as well.
    """
    found: dict[str, tuple[object, SyncSession]] = {}
    seen: set[int] = set()
    queue: list[tuple[str, object]] = [("client", client)]
    while queue:
        path, thing = queue.pop()
        if id(thing) in seen or isinstance(thing, SyncSession | str | bytes | int | type):
            continue
        seen.add(id(thing))
        parts: list[tuple[str, object]] = []
        if isinstance(thing, dict):
            parts = [(f"{path}[{key!r}]", value) for key, value in thing.items()]
        elif isinstance(thing, list | tuple | set | frozenset):
            parts = [(f"{path}[{index}]", value) for index, value in enumerate(thing)]
        elif hasattr(thing, "__dict__"):
            parts = [(f"{path}.{name}", value) for name, value in vars(thing).items()]
        for name, value in parts:
            if isinstance(value, SyncSession):
                found[name] = (thing, value)
            elif type(value).__module__.startswith("ycli.") or isinstance(
                value, dict | list | tuple | set | frozenset
            ):
                queue.append((name, value))
    return found


@pytest.mark.parametrize("client", _clients(), ids=lambda client: type(client).__name__)
def test_everything_reachable_from_a_view_talks_through_the_session_of_the_view(client):
    """`plan` is safe only if no part of a view still holds the session of its client.

    A sub-client that `with_options` did not rebuild would send a real write from inside
    `plan`. Each holder of a session, at any depth, is looked at and named.
    """
    with client:
        view = client.with_options(dry_run=True)
        of_client, of_view = _session_holders(client), _session_holders(view)
        assert of_view.keys() == of_client.keys() and len(of_view) > 5
        assert view._session is not client._session
        wrong = [
            path
            for path, (holder, session) in of_view.items()
            if session is not view._session
            or (holder is of_client[path][0] and holder is not client)
        ]
        assert not wrong
        assert all(session is client._session for _, session in of_client.values())


def test_the_walk_over_a_view_sees_a_resource_that_was_not_rebuilt():
    """What the walk is for, on a client made to do it: the stale resource is named."""

    class Forgetful(TrackerClient):
        def _wire(self, session: SyncSession) -> None:
            super()._wire(session)
            if not hasattr(self, "kept"):
                self.kept = self.boards  # set once, outside what a view rebuilds
            self.nested = [{"deep": self.kept}]

    with Forgetful(oauth_token="t", organization_id="o") as client:
        view = client.with_options(dry_run=True)
        stale = [
            path
            for path, (_, session) in _session_holders(view).items()
            if session is not view._session
        ]
        # One stale object, named by the first path it was reached by, however deep.
        assert stale in (["client.kept._session"], ["client.nested[0]['deep']._session"])


def test_a_plan_and_a_view_leave_the_client_as_it_was(api):
    """The other direction: after a plan, and beside a dry-run view, the client still sends."""
    api.add("DELETE", BOARD, status=204)
    with TrackerClient(oauth_token="t", organization_id="o") as tracker:
        tracker.plan(lambda tracker: tracker.boards.delete(31))
        careful = tracker.with_options(dry_run=True)
        with pytest.raises(RequestPlanned):
            careful.boards.delete(31)
        assert api.calls == []
        tracker.boards.delete(31)  # the client was not turned into a dry run
        careful.with_options(dry_run=False).boards.delete(31)  # nor is a view of it one for good
        assert [call.method for call in api.calls] == ["DELETE", "DELETE"]
        assert tracker._session._guard is None


def test_what_a_call_raises_before_its_first_write_is_raised_as_itself(api):
    """A read inside the call that fails is that failure, not "nothing to plan"."""
    api.add("GET", BOARD, status=404, json={"errorMessages": ["no such board"]})
    api.add("DELETE", BOARD, status=204)

    def read_then_delete(tracker: TrackerClient) -> None:
        tracker.boards.get(31)
        tracker.boards.delete(31)

    with TrackerClient(oauth_token="t", organization_id="o") as tracker:
        with pytest.raises(YandexNotFoundError):
            tracker.plan(read_then_delete)

        def fails(tracker: TrackerClient) -> None:
            raise KeyError("a mistake of the caller's own")

        with pytest.raises(KeyError):
            tracker.plan(fails)
    assert [call.method for call in api.calls] == ["GET"]
