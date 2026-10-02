"""TDD for TrackerClient composition root — sub-clients share one session."""

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issues.client import IssuesClient


def test_composes_subclients_over_shared_authed_session():
    client = TrackerClient(oauth_token="tok", organization_id="org")
    assert isinstance(client.issues, IssuesClient)
    core = client.issues._session._client  # Tracker issues run on the httpx2 core
    assert core.headers["X-Org-Id"] == "org"
    assert str(core.base_url) == "https://api.tracker.yandex.net/v3/"
    for sub in (
        client.comments,
        client.links,
        client.transitions,
        client.worklog,
        client.changelog,
    ):
        assert sub._session.headers["Authorization"] == "OAuth tok"
        assert sub._session.headers["X-Org-Id"] == "org"
