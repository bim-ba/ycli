"""``MockAPI`` — canned answers for the httpx2 core, served through ``httpx2.MockTransport``.

Shaped like the ``responses`` library the uplink tests use, so moving a test means swapping
``responses.add`` for ``api.add``: register ``(method, url)`` answers, read ``api.calls`` back.
The query string is ignored when matching (assert on ``api.calls[i].url.params`` instead), and
several answers for one route are served in order, the last one repeating.

Example:
    >>> api = MockAPI()
    >>> api.add("GET", "https://x.test/v1/me", json={"login": "alice"})
    >>> httpx2.Client(transport=api.transport()).get("https://x.test/v1/me?a=1").json()
    {'login': 'alice'}
"""

from __future__ import annotations

import json as jsonlib
from collections import defaultdict
from typing import Any

import httpx2


class MockAPI:
    def __init__(self) -> None:
        self._routes: dict[tuple[str, str], list[httpx2.Response]] = defaultdict(list)
        self.calls: list[httpx2.Request] = []

    def add(
        self,
        method: str,
        url: str,
        *,
        json: Any = None,
        status: int = 200,
        headers: dict[str, str] | None = None,
        content: bytes | None = None,
    ) -> None:
        """Answer ``method url`` with ``json`` (or raw ``content``) and ``status``."""
        if content is None and json is not None:
            content = jsonlib.dumps(json).encode()
            headers = {"Content-Type": "application/json", **(headers or {})}
        response = httpx2.Response(status, headers=headers, content=content or b"")
        self._routes[(method.upper(), url)].append(response)

    def handle(self, request: httpx2.Request) -> httpx2.Response:
        self.calls.append(request)
        url = str(request.url.copy_with(query=None))
        answers = self._routes.get((request.method, url))
        if not answers:
            raise AssertionError(f"unexpected request: {request.method} {request.url}")
        answer = answers.pop(0) if len(answers) > 1 else answers[0]
        return httpx2.Response(answer.status_code, headers=answer.headers, content=answer.content)

    def transport(self) -> httpx2.MockTransport:
        return httpx2.MockTransport(self.handle)

    def body(self, index: int = -1) -> Any:
        """The JSON body of call ``index`` (default: the last one)."""
        return jsonlib.loads(self.calls[index].content)
