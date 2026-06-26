"""TDD for TrackerClient composition root — sub-clients share one session."""
import requests

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issues.client import IssuesClient


def test_composes_subclients_over_one_session():
    s = requests.Session()
    c = TrackerClient(session=s)
    assert isinstance(c.issues, IssuesClient)
    for sub in (c.issues, c.comments, c.links, c.transitions, c.worklog,
                c.changelog, c.priorities, c.issuetypes, c.linktypes):
        assert sub._session is s


def test_from_env_builds_authed_root(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    c = TrackerClient.from_env()
    assert c.issues._session.headers["Authorization"] == "OAuth tok"
    assert c.issues._session.headers["X-Org-Id"] == "org"
