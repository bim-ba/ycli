"""``PlannedRequest`` — the request a ``--dry-run`` command would have sent, shown instead."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from ycli.yandex.core.endpoint import ENDPOINT_EXTENSION
from ycli.yandex.core.session import shown
from ycli.yandex.models import secret_keys

if TYPE_CHECKING:
    import httpx2


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


class PlannedRequest(BaseModel):
    """One HTTP request, as it would go out: method, URL and body (never the credentials)."""

    method: str
    url: str
    body: Any = None

    @classmethod
    def of(cls, request: httpx2.Request) -> PlannedRequest:
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
