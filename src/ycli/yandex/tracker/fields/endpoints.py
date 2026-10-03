"""Tracker ``/fields`` operations (global fields and their categories), declared once (sans-IO).

Examples:
    >>> update_field("ruName", {"name": {"ru": "Имя"}}, version=3).params
    {'version': 3}
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.fields.models import (
    CustomField,
    FieldCategoryCreate,
    FieldCategoryRecord,
    FieldCategoryUpdate,
    FieldUpdate,
)

if TYPE_CHECKING:
    from ycli.yandex.tracker.models import FieldCreate


def list_fields() -> Endpoint[ItemList[CustomField]]:
    return Endpoint("GET", "fields", ItemList[CustomField])


def get_field(field_id: str) -> Endpoint[CustomField]:
    return Endpoint("GET", f"fields/{segment(field_id)}", CustomField)


def create_field(body: FieldCreate) -> Endpoint[CustomField]:
    return Endpoint("POST", "fields", CustomField, json=body)


def update_field(
    field_id: str, body: FieldUpdate, *, version: int | None = None
) -> Endpoint[CustomField]:
    """``PATCH /fields/{id}?version=`` — ``version`` is the optimistic lock, sent when set."""
    return Endpoint(
        "PATCH", f"fields/{segment(field_id)}", CustomField, json=body, params={"version": version}
    )


def create_category(body: FieldCategoryCreate) -> Endpoint[FieldCategoryRecord]:
    return Endpoint("POST", "fields/categories", FieldCategoryRecord, json=body)


def update_category(
    category_id: str, body: FieldCategoryUpdate, *, version: int | None = None
) -> Endpoint[FieldCategoryRecord]:
    return Endpoint(
        "PATCH",
        f"fields/categories/{segment(category_id)}",
        FieldCategoryRecord,
        json=body,
        params={"version": version},
    )
