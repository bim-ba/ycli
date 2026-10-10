"""Every operation that writes, planned through the SDK: `client.plan(...)` sends no write.

Its own file beside ``test_contract.py``: the cases and the way a case is served are that
module's.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from tests.contract import Case, Sibling
from tests.contract.test_contract import CASES, SERVICE_BY_NAME, _client, _serve
from ycli.cli.app import app
from ycli.yandex.core.endpoint import ENDPOINT_EXTENSION, Effect
from ycli.yandex.core.listing import Listing

if TYPE_CHECKING:
    from ycli.yandex.base import DomainClient


def _one_boundary(plan: object) -> object:
    """``plan`` with the boundary of a file upload, drawn anew for every request, made one."""
    return json.loads(re.sub(r"boundary=[0-9a-f]+", "boundary=x", json.dumps(plan)))


SDK_WRITE_CASES = [case for case in CASES if case.expected_effect != "read"]


@pytest.mark.parametrize("case", SDK_WRITE_CASES, ids=[case.id for case in SDK_WRITE_CASES])
def test_the_sdk_plans_every_write_and_sends_none(case: Case, monkeypatch):
    """`client.plan(...)` of every operation that writes: no write reaches the service.

    Whatever resource the call goes through, however deep, it talks through the view of the
    plan. Where the case has a command, the plan is the one `--dry-run -o json` prints.
    """
    for name, value in case.env.items():
        monkeypatch.setenv(name, value)
    api = _serve(monkeypatch, case)
    domain, resource, method = case.operation.split(".")

    def call(client: DomainClient) -> None:
        args = [getattr(client, a.resource) if isinstance(a, Sibling) else a for a in case.args]
        result = getattr(getattr(client, resource), method)(*args, **case.kwargs)
        if isinstance(result, Listing):
            result.collect()  # lazy: a listing that writes writes when it is read

    with _client(SERVICE_BY_NAME[domain]) as client:
        planned = client.plan(call)
    for sent in api.calls:
        assert sent.extensions[ENDPOINT_EXTENSION].effect is Effect.READ, f"sent {sent.method}"
    if case.cli is not None:
        _serve(monkeypatch, case)
        printed = CliRunner().invoke(app, ["--format", "json", "--dry-run", *case.cli])
        assert printed.exit_code == 0, printed.output
        by_sdk = planned.model_dump(by_alias=True, mode="json")
        assert _one_boundary(by_sdk) == _one_boundary(json.loads(printed.stdout_bytes))
