"""TDD for TrackerClient composition root — sub-clients share one session."""
import responses
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issues.client import IssuesClient


def test_composes_subclients_over_shared_authed_session():
    client = TrackerClient(oauth_token="tok", organization_id="org")
    assert isinstance(client.issues, IssuesClient)
    for sub in (client.issues, client.comments, client.links, client.transitions, client.worklog,
                client.changelog, client.priorities, client.issuetypes, client.linktypes):
        assert sub._session.headers["Authorization"] == "OAuth tok"
        assert sub._session.headers["X-Org-Id"] == "org"


@responses.activate
def test_tracker_deps_factory_builds_from_env(monkeypatch):
    """_deps.tracker_client() reads env and returns a working TrackerClient."""
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    from ycli.yandex.tracker._deps import tracker_client
    responses.add(responses.GET, "https://api.tracker.yandex.net/v3/priorities", json=[], status=200)
    client = tracker_client()
    assert isinstance(client, TrackerClient)
    result = client.priorities.list()
    assert result.root == []
