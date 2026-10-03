"""IssuesClient guards the contract table cannot reach."""

import pytest

from ycli.yandex.errors import YandexClientError
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issues.models import IssueSearch, IssueUpdate


def test_a_key_cannot_reach_another_endpoint(api):
    # Escaping is not enough: Tracker decodes %2F, so PATCH issues/..%2Fqueues%2FDE edits queue DE.
    with (
        TrackerClient(oauth_token="t", organization_id="o") as client,
        pytest.raises(YandexClientError, match="leaves its endpoint"),
    ):
        client.issues.update("../queues/DE", IssueUpdate(description="x"))
    assert api.calls == []


def test_search_rejects_a_non_positive_limit():
    with (
        TrackerClient(oauth_token="t", organization_id="o") as client,
        pytest.raises(ValueError, match="positive"),
    ):
        client.issues.search(IssueSearch(query="q"), limit=0)
