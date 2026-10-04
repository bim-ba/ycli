"""Forms ``/surveys/{id}/access`` operations, declared once (sans-IO).

All three writes are ``POST``s that do not add anything new: setting a level and granting a
user converge (sending twice changes nothing more), and revoking removes access.

Examples:
    >>> set_("686d", {"action": "submit", "access": "common"}).effect
    'idempotent_write'
    >>> revoke("686d", {"action": "change"}).effect
    'destructive'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.access.models import AccessGrant, AccessRevoke, AccessUpdate, Permission
from ycli.yandex.models import ItemList


def _access(survey_id: str) -> str:
    return f"surveys/{segment(survey_id)}/access"


def get(survey_id: str) -> Endpoint[ItemList[Permission]]:
    return Endpoint("GET", _access(survey_id), ItemList[Permission])


def set_(survey_id: str, body: AccessUpdate) -> Endpoint[ItemList[Permission]]:
    return Endpoint(
        "POST", _access(survey_id), ItemList[Permission], json=body, effect="idempotent_write"
    )


def grant(survey_id: str, body: AccessGrant) -> Endpoint[ItemList[Permission]]:
    path = f"{_access(survey_id)}/grant"
    return Endpoint("POST", path, ItemList[Permission], json=body, effect="idempotent_write")


def revoke(survey_id: str, body: AccessRevoke) -> Endpoint[ItemList[Permission]]:
    path = f"{_access(survey_id)}/revoke"
    return Endpoint("POST", path, ItemList[Permission], json=body, effect="destructive")
