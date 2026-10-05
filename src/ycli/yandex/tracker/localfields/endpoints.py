"""Tracker ``/queues/{id}/localFields`` operations (per-queue fields), declared once (sans-IO).

Examples:
    >>> get("ORG", "loc_field_key").path
    'queues/ORG/localFields/loc_field_key'
"""

from __future__ import annotations

from http import HTTPMethod
from typing import TYPE_CHECKING

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.localfields.models import LocalField, LocalFieldUpdate

if TYPE_CHECKING:
    from ycli.yandex.tracker.models import FieldCreate


def _local_fields(queue_id: str) -> str:
    return f"queues/{segment(queue_id)}/localFields"


def list_(queue_id: str) -> Endpoint[ItemList[LocalField]]:
    return Endpoint(HTTPMethod.GET, _local_fields(queue_id), ItemList[LocalField])


def get(queue_id: str, field_key: str) -> Endpoint[LocalField]:
    return Endpoint(HTTPMethod.GET, f"{_local_fields(queue_id)}/{segment(field_key)}", LocalField)


def create(queue_id: str, body: FieldCreate) -> Endpoint[LocalField]:
    return Endpoint(HTTPMethod.POST, _local_fields(queue_id), LocalField, json=body)


def update(queue_id: str, field_key: str, body: LocalFieldUpdate) -> Endpoint[LocalField]:
    """``PATCH …/localFields/{key}`` — unlike global fields, no ``?version=`` lock."""
    return Endpoint(
        HTTPMethod.PATCH, f"{_local_fields(queue_id)}/{segment(field_key)}", LocalField, json=body
    )
