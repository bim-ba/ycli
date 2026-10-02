"""``PlannedRequest`` — the request a ``--dry-run`` command would have sent, shown instead."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from ycli.yandex.core.session import shown

if TYPE_CHECKING:
    import httpx2


class PlannedRequest(BaseModel):
    """One HTTP request, as it would go out: method, URL and body (never the credentials)."""

    method: str
    url: str
    body: Any = None

    @classmethod
    def of(cls, request: httpx2.Request) -> PlannedRequest:
        """The plan for ``request``: secret query parameters masked, no headers at all.

        A JSON body is shown as the JSON it is; any other body (a file upload) only by its size
        and type, since its bytes are not something to print.

        Example:
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
        return cls(method=request.method, url=str(shown(request.url)), body=body)
