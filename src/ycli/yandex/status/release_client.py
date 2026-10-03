"""The latest released version of ycli, read from PyPI for ``ycli doctor``.

The one request ycli sends to a host that is not Yandex's. It carries no credentials: the
session is built with an auth that adds nothing, and PyPI's JSON API needs none.
"""

from __future__ import annotations

import httpx2
from pydantic import Field

from ycli.settings import RELEASE_CHECK_HTTP
from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.core.profile import ServiceProfile
from ycli.yandex.core.session import connect
from ycli.yandex.models import APIModel

PYPI = ServiceProfile("https://pypi.org", org_header=None)
DISTRIBUTION = "yandex-cli"


class _Info(APIModel):
    version: str = Field(description="The latest released version.")


class _Project(APIModel):
    info: _Info = Field(description="The project's metadata.")


def latest_release() -> str:
    """``GET https://pypi.org/pypi/yandex-cli/json``: the latest released version.

    One attempt with a short timeout, so a slow PyPI never holds the report.

    Returns:
        The version, for example ``"0.46.0"``.
    """
    session = connect(PYPI, auth=httpx2.Auth(), http=RELEASE_CHECK_HTTP)
    try:
        return session.send(Endpoint("GET", f"pypi/{DISTRIBUTION}/json", _Project)).info.version
    finally:
        session.close()


def is_newer(latest: str, installed: str) -> bool:
    """Whether ``latest`` is a later ``X.Y.Z`` than ``installed``; anything else is not.

    Args:
        latest: The latest released version.
        installed: The installed version.

    Returns:
        ``True`` when both are plain ``X.Y.Z`` and ``latest`` is the later one.

    Examples:
        >>> is_newer("0.47.0", "0.46.2"), is_newer("0.46.0", "0.46.0"), is_newer("1.0rc1", "0.9.0")
        (True, False, False)
    """
    try:
        return _numbers(latest) > _numbers(installed)
    except ValueError:
        return False


def _numbers(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))
