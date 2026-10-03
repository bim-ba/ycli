"""Tracker ``/queues/{id}/localFields`` operations (per-queue fields), declared once (sans-IO).

Examples:
    >>> get_local_field("ORG", "loc_field_key").path
    'queues/ORG/localFields/loc_field_key'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.localfields.models import LocalField


def _local_fields(queue_id: str) -> str:
    return f"queues/{segment(queue_id)}/localFields"


def list_local_fields(queue_id: str) -> Endpoint[ItemList[LocalField]]:
    return Endpoint("GET", _local_fields(queue_id), ItemList[LocalField])


def get_local_field(queue_id: str, field_key: str) -> Endpoint[LocalField]:
    return Endpoint("GET", f"{_local_fields(queue_id)}/{segment(field_key)}", LocalField)


def create_local_field(queue_id: str, body: dict[str, Any]) -> Endpoint[LocalField]:
    return Endpoint("POST", _local_fields(queue_id), LocalField, json=body)


def edit_local_field(queue_id: str, field_key: str, body: dict[str, Any]) -> Endpoint[LocalField]:
    """``PATCH …/localFields/{key}`` — unlike global fields, no ``?version=`` lock."""
    return Endpoint(
        "PATCH", f"{_local_fields(queue_id)}/{segment(field_key)}", LocalField, json=body
    )
