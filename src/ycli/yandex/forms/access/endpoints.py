"""Forms ``/surveys/{id}/access`` operations, declared once (sans-IO).

All three writes are ``POST``s that do not add anything new: setting a level and granting a
user converge (sending twice changes nothing more), and revoking removes access.

Examples:
    >>> set_access("686d", {"action": "submit", "access": "common"}).effect
    'idempotent_write'
    >>> revoke_access("686d", {"action": "change"}).effect
    'destructive'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.access.models import PermissionList


def _access(survey_id: str) -> str:
    return f"surveys/{segment(survey_id)}/access"


def get_access(survey_id: str) -> Endpoint[PermissionList]:
    return Endpoint("GET", _access(survey_id), PermissionList)


def set_access(survey_id: str, body: dict[str, Any]) -> Endpoint[PermissionList]:
    return Endpoint(
        "POST", _access(survey_id), PermissionList, json=body, effect="idempotent_write"
    )


def grant_access(survey_id: str, body: dict[str, Any]) -> Endpoint[PermissionList]:
    path = f"{_access(survey_id)}/grant"
    return Endpoint("POST", path, PermissionList, json=body, effect="idempotent_write")


def revoke_access(survey_id: str, body: dict[str, Any]) -> Endpoint[PermissionList]:
    path = f"{_access(survey_id)}/revoke"
    return Endpoint("POST", path, PermissionList, json=body, effect="destructive")
