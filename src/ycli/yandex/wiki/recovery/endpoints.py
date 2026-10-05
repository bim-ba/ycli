"""Wiki ``/recovery_tokens``, declared once (sans-IO).

Examples:
    >>> recover("a1b2").path
    'recovery_tokens/a1b2/recover'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.wiki.recovery.models import RecoveredPage


def recover(token: str) -> Endpoint[RecoveredPage]:
    return Endpoint("POST", f"recovery_tokens/{segment(token)}/recover", RecoveredPage)
