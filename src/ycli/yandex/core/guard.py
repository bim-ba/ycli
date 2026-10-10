"""What stands between an operation and the network: show it, or ask, before it is sent.

Every request of every surface goes through a session, and a session asks its :class:`Guard`
once per operation, before the first attempt. The rule lives here; a surface only says how to
ask: the CLI on a terminal and with ``--yes``, a caller of the SDK with a function of its own.

- a read goes out;
- with ``dry_run`` a write does not: :class:`RequestPlanned` carries the request it would
  have sent, and the surface shows it in place of a result;
- an operation that destroys data, or grants access, is confirmed first, where there is
  someone to ask.

Examples:
    >>> import httpx2
    >>> from http import HTTPMethod
    >>> from ycli.yandex.core.endpoint import Endpoint
    >>> delete = Endpoint(HTTPMethod.DELETE, "boards/7")
    >>> request = httpx2.Request("DELETE", "https://api.test/v3/boards/7")
    >>> Guard(confirm=lambda plan: plan.method != "DELETE").check(delete, request)
    Traceback (most recent call last):
    ...
    ycli.yandex.errors.YandexDeclinedError: DELETE https://api.test/v3/boards/7 was not confirmed; \
nothing was sent
"""

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Self

import httpx2
from pydantic import BaseModel, Field, PrivateAttr

from ycli.yandex.core.endpoint import ENDPOINT_EXTENSION, Effect, Endpoint
from ycli.yandex.core.session import shown
from ycli.yandex.errors import YandexDeclinedError
from ycli.yandex.models import APIModel, secret_keys


def _masked(body: Any, secrets: frozenset[str]) -> Any:
    """``body`` with the value under every key of ``secrets`` replaced by ``***``, at any depth.

    Args:
        body: The JSON of a request body.
        secrets: The keys whose values are not printed.

    Returns:
        A copy of ``body`` with those values masked.

    Examples:
        >>> _masked({"host": "db", "auth": [{"password": "S3cret"}]}, frozenset({"password"}))
        {'host': 'db', 'auth': [{'password': '***'}]}
    """
    if isinstance(body, dict):
        return {
            key: "***" if key in secrets else _masked(value, secrets) for key, value in body.items()
        }
    if isinstance(body, list):
        return [_masked(item, secrets) for item in body]
    return body


class PlannedRequest(APIModel):
    """One HTTP request, as it would go out: method, URL and body (never the credentials)."""

    method: str = Field(description="The HTTP method.")
    url: str = Field(description="The address, with a secret in its query masked.")
    body: Any = Field(default=None, description="The body, with every secret in it masked.")
    # For the one who asks, so the question says what it is about: no field of the plan, so
    # it is in no dump of it and in no table.
    _grants_access: bool = PrivateAttr(default=False)

    @property
    def grants_access(self) -> bool:
        """Whether the request grants access, as its operation says."""
        return self._grants_access

    @classmethod
    def of(cls, request: httpx2.Request) -> Self:
        """The plan for ``request``: secrets masked, no headers at all.

        A JSON body is shown as the JSON it is; any other body (a file upload) only by its size
        and type, since its bytes are not something to print. A secret is a query parameter
        that carries one, and a key of the body that the request's model marks as one
        (``ycli.yandex.models.secret_keys``): a password of a connection is printed as ``***``,
        whether a flag, ``-F`` or ``--body-file`` gave it. The plan is printed to a terminal
        and to the log of a CI run, where a secret must not be.

        Args:
            request: The request about to be sent.

        Returns:
            The plan for ``request``.

        Examples:
            >>> import httpx2
            >>> request = httpx2.Request(
            ...     "PATCH", "https://api.test/v1/issues/DE-1?token=x", json={"summary": "New"}
            ... )
            >>> plan = PlannedRequest.of(request)
            >>> plan.method, plan.url, plan.body
            ('PATCH', 'https://api.test/v1/issues/DE-1?token=%2A%2A%2A', {'summary': 'New'})
        """
        data = request.read()
        content_type = request.headers.get("content-type", "")
        body: Any
        if not data:
            body = None
        else:
            try:
                body = json.loads(data) if "json" in content_type else None
            except ValueError:  # declared JSON that is not (``ycli api --input`` of any file)
                body = None
            if body is None:
                body = f"<{len(data)} bytes, {content_type or 'no content type'}>"
        sent = getattr(request.extensions.get(ENDPOINT_EXTENSION), "json", None)
        secrets = secret_keys(type(sent)) if isinstance(sent, BaseModel) else frozenset()
        return cls(method=request.method, url=str(shown(request.url)), body=_masked(body, secrets))


class RequestPlanned(Exception):  # noqa: N818  # a signal that stops a call, not an error
    """Stops a call at its first write under ``dry_run``; ``plan`` is what it would have sent."""

    def __init__(self, plan: PlannedRequest) -> None:
        super().__init__(f"{plan.method} {plan.url}")
        self.plan = plan


def _plan(endpoint: Endpoint[Any], request: httpx2.Request) -> PlannedRequest:
    """The plan of ``request``, told whether its operation grants access.

    Told of a plan that is only shown as well as of one that is asked about: the one who is
    shown it may be the one asked next.
    """
    plan = PlannedRequest.of(request)
    plan._grants_access = endpoint.grants_access
    return plan


@dataclass(frozen=True)
class Guard:
    """The rule every write goes through, the same for every surface.

    Args:
        dry_run: Send no write: stop at the first one and show it.
        confirm: Asked before an operation that destroys data or grants access, with the
            request about to go out; ``False`` keeps it from being sent. ``None``: nobody to
            ask, so it is sent.
    """

    dry_run: bool = False
    confirm: Callable[[PlannedRequest], bool] | None = None

    def check(self, endpoint: Endpoint[Any], request: httpx2.Request) -> None:
        """Pass a read; plan a write under ``dry_run``; confirm what destroys or grants.

        Args:
            endpoint: The operation about to be sent.
            request: The request built for it, as it would go out.

        Raises:
            RequestPlanned: A write under ``dry_run``; it carries the request not sent.
            YandexDeclinedError: The one asked did not confirm; nothing was sent.
        """
        if endpoint.effect is Effect.READ:
            return
        if self.dry_run:
            raise RequestPlanned(_plan(endpoint, request))
        asked_about = endpoint.effect is Effect.DESTRUCTIVE or endpoint.grants_access
        if not asked_about or self.confirm is None:
            return
        plan = _plan(endpoint, request)
        if not self.confirm(plan):
            raise YandexDeclinedError(
                f"{plan.method} {plan.url} was not confirmed; nothing was sent", url=plan.url
            )
