"""Forms ``/surveys/{id}/hooks`` operations, declared once (sans-IO).

Examples:
    >>> get_hook("686d", 11).path
    'surveys/686d/hooks/11'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.hooks.models import Hook, HookList


def _hooks(survey_id: str) -> str:
    return f"surveys/{segment(survey_id)}/hooks"


def list_hooks(survey_id: str) -> Endpoint[HookList]:
    return Endpoint("GET", _hooks(survey_id), HookList)


def get_hook(survey_id: str, hook_id: int) -> Endpoint[Hook]:
    return Endpoint("GET", f"{_hooks(survey_id)}/{segment(hook_id)}", Hook)


def create_hook(survey_id: str, body: dict[str, Any]) -> Endpoint[Hook]:
    return Endpoint("POST", _hooks(survey_id), Hook, json=body)


def modify_hook(survey_id: str, hook_id: int, body: dict[str, Any]) -> Endpoint[Hook]:
    return Endpoint("PATCH", f"{_hooks(survey_id)}/{segment(hook_id)}", Hook, json=body)


def delete_hook(survey_id: str, hook_id: int) -> Endpoint[None]:
    return Endpoint("DELETE", f"{_hooks(survey_id)}/{segment(hook_id)}")
