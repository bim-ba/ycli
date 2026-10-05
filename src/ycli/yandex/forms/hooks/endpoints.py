"""Forms ``/surveys/{id}/hooks`` operations, declared once (sans-IO).

Examples:
    >>> get("686d", 11).path
    'surveys/686d/hooks/11'
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.hooks.models import Hook, HookCreate, HookUpdate
from ycli.yandex.models import ItemList


def _hooks(survey_id: str) -> str:
    return f"surveys/{segment(survey_id)}/hooks"


def list_(survey_id: str) -> Endpoint[ItemList[Hook]]:
    return Endpoint(HTTPMethod.GET, _hooks(survey_id), ItemList[Hook])


def get(survey_id: str, hook_id: int) -> Endpoint[Hook]:
    return Endpoint(HTTPMethod.GET, f"{_hooks(survey_id)}/{segment(hook_id)}", Hook)


def create(survey_id: str, body: HookCreate) -> Endpoint[Hook]:
    return Endpoint(HTTPMethod.POST, _hooks(survey_id), Hook, json=body)


def update(survey_id: str, hook_id: int, body: HookUpdate) -> Endpoint[Hook]:
    return Endpoint(HTTPMethod.PATCH, f"{_hooks(survey_id)}/{segment(hook_id)}", Hook, json=body)


def delete(survey_id: str, hook_id: int) -> Endpoint[None]:
    return Endpoint(HTTPMethod.DELETE, f"{_hooks(survey_id)}/{segment(hook_id)}")
