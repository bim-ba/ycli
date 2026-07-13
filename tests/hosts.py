"""Shared API-base-URL constants for `responses` mocks — one per Yandex 360 domain.

Each domain test file imports the one it needs, aliased back to the local name `BASE`
it already uses in ~951 `f"{BASE}/..."` mock-URL call sites (e.g.
``from tests.hosts import TRACKER_BASE as BASE``), so no call site changes.
"""

TRACKER_BASE = "https://api.tracker.yandex.net/v3"
WIKI_BASE = "https://api.wiki.yandex.net/v1"
FORMS_BASE = "https://api.forms.yandex.net/v1"
