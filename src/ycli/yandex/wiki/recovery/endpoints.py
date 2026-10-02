"""Wiki ``/recovery_tokens``, declared once (sans-IO).

Example:
    >>> restore_page("a1b2").path
    'recovery_tokens/a1b2/recover'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.wiki.recovery.models import RecoveredPage


def restore_page(token: str) -> Endpoint[RecoveredPage]:
    return Endpoint("POST", f"recovery_tokens/{segment(token)}/recover", RecoveredPage)
