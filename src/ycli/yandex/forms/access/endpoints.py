"""Forms ``/surveys/{id}/access`` operations, declared once (sans-IO).

All three writes are ``POST``s that do not add anything new: setting a level and granting a
user converge (sending twice changes nothing more), and revoking removes access.

Examples:
    >>> update("686d", {"action": "submit", "access": "common"}).effect
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


def list_(survey_id: str) -> Endpoint[ItemList[Permission]]:
    return Endpoint("GET", _access(survey_id), ItemList[Permission])


def update(survey_id: str, body: AccessUpdate) -> Endpoint[ItemList[Permission]]:
    # violation(arch-3): POST sets an access level: sending twice converges
    return Endpoint(
        "POST", _access(survey_id), ItemList[Permission], json=body, effect="idempotent_write"
    )


def grant(survey_id: str, body: AccessGrant) -> Endpoint[ItemList[Permission]]:
    path = f"{_access(survey_id)}/grant"
    # violation(arch-3): POST grants access: granting twice converges
    return Endpoint("POST", path, ItemList[Permission], json=body, effect="idempotent_write")


def revoke(survey_id: str, body: AccessRevoke) -> Endpoint[ItemList[Permission]]:
    path = f"{_access(survey_id)}/revoke"
    # violation(arch-3): POST revokes access: it removes a permission
    return Endpoint("POST", path, ItemList[Permission], json=body, effect="destructive")
