"""TDD for TrackerClient composition root — sub-clients share one session."""
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issues.client import IssuesClient


def test_composes_subclients_over_shared_authed_session():
    client = TrackerClient(oauth_token="tok", organization_id="org")
    assert isinstance(client.issues, IssuesClient)
    for sub in (client.issues, client.comments, client.links, client.transitions, client.worklog,
                client.changelog, client.priorities, client.issuetypes, client.linktypes):
        assert sub._session.headers["Authorization"] == "OAuth tok"
        assert sub._session.headers["X-Org-Id"] == "org"


def test_from_env_builds_authed_root(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    client = TrackerClient.from_env()
    assert client.issues._session.headers["Authorization"] == "OAuth tok"
    assert client.issues._session.headers["X-Org-Id"] == "org"
