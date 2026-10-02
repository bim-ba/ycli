"""Tracker issue ``/remotelinks`` operations, declared once (sans-IO).

Examples:
    >>> create_remote_link("JUNE-2", {"key": "TEST-17"}, "true").params
    {'backlink': 'true'}
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.remotelinks.models import RemoteLink, RemoteLinkList


def list_remote_links(issue_key: str) -> Endpoint[RemoteLinkList]:
    return Endpoint("GET", f"issues/{segment(issue_key)}/remotelinks", RemoteLinkList)


def create_remote_link(
    issue_key: str, body: dict[str, Any], backlink: str | None
) -> Endpoint[RemoteLink]:
    path = f"issues/{segment(issue_key)}/remotelinks"
    return Endpoint("POST", path, RemoteLink, json=body, params={"backlink": backlink})


def delete_remote_link(issue_key: str, link_id: str) -> Endpoint[None]:
    return Endpoint("DELETE", f"issues/{segment(issue_key)}/remotelinks/{segment(link_id)}")
