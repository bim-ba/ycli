"""Wiki ``/pages/{id}/access``, declared once (sans-IO).

``prevent_selflock`` asks the API to refuse a change that would lock the caller out of the page;
it is sent only when set, because ``false`` is the API's default.

Example:
    >>> delete_access(7, "9", prevent_selflock=True).params
    {'prevent_selflock': True}
    >>> update_access(7, "9", {"role": "reader"}, prevent_selflock=False).effect
    'idempotent_write'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.wiki.access.models import PageAccess


def _selflock(prevent_selflock: bool) -> dict[str, bool | None]:
    return {"prevent_selflock": True if prevent_selflock else None}


def create_access(page_id: int, body: dict[str, Any]) -> Endpoint[PageAccess]:
    return Endpoint("POST", f"pages/{segment(page_id)}/access", PageAccess, json=body)


def update_access(
    page_id: int, access_id: str, body: dict[str, Any], *, prevent_selflock: bool
) -> Endpoint[PageAccess]:
    path = f"pages/{segment(page_id)}/access/{segment(access_id)}"
    return Endpoint(
        "POST",
        path,
        PageAccess,
        params=_selflock(prevent_selflock),
        json=body,
        effect="idempotent_write",
    )


def delete_access(page_id: int, access_id: str, *, prevent_selflock: bool) -> Endpoint[None]:
    path = f"pages/{segment(page_id)}/access/{segment(access_id)}"
    return Endpoint("DELETE", path, params=_selflock(prevent_selflock))


def clear_access(page_id: int, *, prevent_selflock: bool) -> Endpoint[None]:
    return Endpoint(
        "DELETE", f"pages/{segment(page_id)}/access", params=_selflock(prevent_selflock)
    )
