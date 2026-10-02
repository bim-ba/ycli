"""TDD for TrackerClient composition root — sub-clients share one session."""

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issues.client import IssuesClient


def test_composes_subclients_over_shared_authed_session():
    client = TrackerClient(oauth_token="tok", organization_id="org")
    assert isinstance(client.issues, IssuesClient)
    core = client.issues._session._client  # Tracker issues run on the httpx2 core
    assert core.headers["X-Org-Id"] == "org"
    assert str(core.base_url) == "https://api.tracker.yandex.net/v3/"
    # Every resource shares the one core session.
    sessions = {id(value._session) for value in vars(client).values() if hasattr(value, "_session")}
    assert len(sessions) == 1
