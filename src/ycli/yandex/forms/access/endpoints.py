"""Forms ``/surveys/{id}/access`` operations, declared once (sans-IO).

All three writes are ``POST``s that do not add anything new: setting a level and granting a
user converge (sending twice changes nothing more), and revoking removes access.

Examples:
    >>> update("686d", {"action": "submit", "access": "common"}).effect
    <Effect.IDEMPOTENT_WRITE: 'idempotent_write'>
    >>> revoke("686d", {"action": "change"}).effect
    <Effect.DESTRUCTIVE: 'destructive'>
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Effect, Endpoint, segment
from ycli.yandex.forms.access.models import AccessGrant, AccessRevoke, AccessUpdate, Permission
from ycli.yandex.models import ItemList


def _access(survey_id: str) -> str:
    return f"surveys/{segment(survey_id)}/access"


def list_(survey_id: str) -> Endpoint[ItemList[Permission]]:
    return Endpoint(HTTPMethod.GET, _access(survey_id), ItemList[Permission])


def update(survey_id: str, body: AccessUpdate) -> Endpoint[ItemList[Permission]]:
    # violation(arch-3): POST sets an access level: sending twice converges
    return Endpoint(
        HTTPMethod.POST,
        _access(survey_id),
        ItemList[Permission],
        json=body,
        effect=Effect.IDEMPOTENT_WRITE,
        grants_access=True,
    )


def grant(survey_id: str, body: AccessGrant) -> Endpoint[ItemList[Permission]]:
    path = f"{_access(survey_id)}/grant"
    # violation(arch-3): POST grants access: granting twice converges
    return Endpoint(
        HTTPMethod.POST,
        path,
        ItemList[Permission],
        json=body,
        effect=Effect.IDEMPOTENT_WRITE,
        grants_access=True,
    )


def revoke(survey_id: str, body: AccessRevoke) -> Endpoint[ItemList[Permission]]:
    path = f"{_access(survey_id)}/revoke"
    # violation(arch-3): POST revokes access: it removes a permission
    return Endpoint(
        HTTPMethod.POST, path, ItemList[Permission], json=body, effect=Effect.DESTRUCTIVE
    )
