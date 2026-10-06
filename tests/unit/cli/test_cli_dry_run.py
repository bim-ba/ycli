"""``--dry-run`` — a write is not sent; the request it would send is printed instead."""

import json
from http import HTTPMethod

import httpx2
import pytest
import typer.main
from pydantic import BaseModel, Field, SecretStr
from typer.testing import CliRunner

from tests.hosts import TRACKER_BASE, WIKI_BASE
from tests.mock_api import MockAPI
from ycli.cli.app import app
from ycli.cli.body_fields import CallerFields
from ycli.cli.guard import DryRunPlanned, SendGuard
from ycli.cli.planned_request import PlannedRequest
from ycli.settings import HTTPConfig
from ycli.yandex.core.auth import OAuthTokenAuth
from ycli.yandex.core.endpoint import Effect, Endpoint
from ycli.yandex.core.profile import ServiceProfile
from ycli.yandex.core.session import connect
from ycli.yandex.models import RequestBody, secret_keys

runner = CliRunner()
BOARD_URL = f"{TRACKER_BASE}/boards/7"


def test_a_json_body_is_shown_as_json_and_a_secret_parameter_is_masked():
    request = httpx2.Request("POST", "https://api.test/v1/items?apikey=hunter2", json={"a": [1]})
    plan = PlannedRequest.of(request)
    assert plan.method == "POST"
    assert plan.url == "https://api.test/v1/items?apikey=%2A%2A%2A"
    assert plan.body == {"a": [1]}
    assert "hunter2" not in plan.model_dump_json()


def test_a_body_declared_json_that_is_not_is_described_not_parsed():
    request = httpx2.Request(
        "POST",
        "https://api.test/v1/x",
        content=b"plain note",
        headers={"Content-Type": "application/json"},
    )
    assert PlannedRequest.of(request).body == "<10 bytes, application/json>"


def test_a_request_without_a_body_plans_none():
    assert PlannedRequest.of(httpx2.Request("DELETE", "https://api.test/v1/items/7")).body is None


@pytest.mark.parametrize(
    ("kwargs", "described"),
    [
        (
            {"content": b"0123456789", "headers": {"Content-Type": "image/png"}},
            "<10 bytes, image/png>",
        ),
        ({"content": b"abc"}, "<3 bytes, no content type>"),
    ],
)
def test_a_file_body_is_described_not_printed(kwargs, described):
    assert (
        PlannedRequest.of(httpx2.Request("PUT", "https://api.test/v1/up", **kwargs)).body
        == described
    )


def test_a_multipart_body_is_described_by_its_size_and_type():
    request = httpx2.Request("POST", "https://api.test/v1/up", files={"file": ("a.txt", b"hello")})
    body = PlannedRequest.of(request).body
    assert isinstance(body, str)
    assert body.startswith("<") and "multipart/form-data" in body


def test_a_plan_has_no_authorization_header():
    request = httpx2.Request(
        "POST", "https://api.test/v1/x", headers={"Authorization": "OAuth s3cr3t"}
    )
    assert "s3cr3t" not in PlannedRequest.of(request).model_dump_json()


# --- the guard ---------------------------------------------------------------------------------


def _session(api: MockAPI, guard: SendGuard):
    return connect(
        ServiceProfile("https://api.test/v1"),
        auth=OAuthTokenAuth(SecretStr("t")),
        http=HTTPConfig(retries=0),
        transport=api.transport(),
        before_send=guard,
    )


def test_reads_go_through_and_the_first_write_is_the_plan():
    api = MockAPI()
    api.add("GET", "https://api.test/v1/items", json=[1])
    session = _session(api, SendGuard({"dry_run": True}, CallerFields({"dry_run": True})))
    assert session.send(Endpoint(HTTPMethod.GET, "items", list[int])) == [1]
    with pytest.raises(DryRunPlanned) as planned:
        session.send(Endpoint(HTTPMethod.PATCH, "items/1", json={"a": 1}))
    assert (planned.value.plan.method, planned.value.plan.body) == ("PATCH", {"a": 1})
    assert [call.method for call in api.calls] == ["GET"]  # the write never went out


@pytest.mark.parametrize("effect", ["write", "idempotent_write", "destructive"])
def test_every_kind_of_write_is_planned_and_a_dry_run_needs_no_yes(effect):
    request = httpx2.Request("POST", "https://api.test/v1/items")
    with pytest.raises(DryRunPlanned):
        SendGuard({"dry_run": True}, CallerFields({"dry_run": True}))(effect, request)


# --- through the CLI ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "args",
    [
        ["--dry-run", "tracker", "boards", "delete", "7"],
        ["tracker", "boards", "delete", "7", "--dry-run"],
    ],
)
def test_a_dry_run_prints_the_request_and_sends_nothing(api, args):
    result = runner.invoke(app, ["-o", "json", *args])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {"method": "DELETE", "url": BOARD_URL, "body": None}
    assert api.calls == []


def test_a_dry_run_shows_the_body_of_a_write(api):
    result = runner.invoke(
        app, ["--dry-run", "-o", "json", "tracker", "boards", "create", "--name", "Roadmap"]
    )
    assert result.exit_code == 0, result.output
    plan = json.loads(result.stdout)
    assert (plan["method"], plan["url"]) == ("POST", f"{TRACKER_BASE}/liveBoards/")
    assert plan["body"]["name"] == "Roadmap"
    assert "OAuth" not in result.output  # no credentials in the plan
    assert api.calls == []


def test_a_dry_run_goes_through_the_normal_output_path(api):
    result = runner.invoke(app, ["--dry-run", "-o", "yaml", "tracker", "boards", "delete", "7"])
    assert "method: DELETE\n" in result.stdout


def test_a_read_still_runs_under_dry_run(api):
    api.add("GET", BOARD_URL, json={"id": 7, "name": "B"})
    result = runner.invoke(app, ["--dry-run", "tracker", "boards", "get", "7"])
    assert result.exit_code == 0, result.output
    assert [call.method for call in api.calls] == ["GET"]


def test_wiki_move_keeps_its_server_side_check_under_its_new_name(api):
    """``--validate-only`` is the API's own ``dry_run`` parameter; ``--dry-run`` is the global."""
    api.add("POST", f"{WIKI_BASE}/pages/move", json={"operation": {"id": "op-1"}})
    sent = runner.invoke(
        app, ["wiki", "pages", "move", "a/b", "a/c", "--validate-only", "--no-wait"]
    )
    assert sent.exit_code == 0, sent.output
    assert api.calls[0].url.params["dry_run"] == "true"

    planned = runner.invoke(app, ["-o", "json", "wiki", "pages", "move", "a/b", "a/c", "--dry-run"])
    assert planned.exit_code == 0, planned.output
    assert "dry_run" not in json.loads(planned.stdout)["url"]
    assert len(api.calls) == 1


def test_the_help_of_dry_run_says_only_the_first_write_is_shown():
    root = typer.main.get_command(app)
    help_text = next(getattr(param, "help", "") for param in root.params if param.name == "dry_run")
    assert "only the first write of a command is shown" in help_text


class _Login(RequestBody):
    user: str
    password: SecretStr


class _Connection(RequestBody):
    host: str
    logins: list[_Login]
    api_token: SecretStr | None = Field(default=None, alias="apiToken")
    headers: dict[str, SecretStr] | None = None


def _planned(json: object) -> PlannedRequest:
    endpoint = Endpoint(HTTPMethod.POST, "connections", json=json)
    with httpx2.Client(base_url="https://api.test/v1/") as client:
        return PlannedRequest.of(endpoint.request(client))


def test_a_dry_run_masks_what_the_body_model_marks_as_a_secret():
    """#388: a plan is printed to a terminal and a CI log; a password is not."""
    body = _Connection.model_validate(
        {
            "host": "db",
            "logins": [{"user": "reader", "password": "S3cret"}],
            "apiToken": "t0ken",
            "headers": {"Authorization": "Bearer x"},
        }
    )
    assert _planned(body).body == {
        "host": "db",
        "logins": [{"user": "reader", "password": "***"}],
        "apiToken": "***",
        "headers": "***",
    }
    assert secret_keys(_Connection) == {"password", "apiToken", "headers"}


def test_the_mask_bites():
    """Both sides: the same body with no model behind it is printed as it is."""
    plain = {"host": "db", "password": "S3cret"}
    assert _planned(plain).body == plain
    assert _planned(_Login(user="reader", password=SecretStr("S3cret"))).body["password"] == "***"


def test_a_secret_given_by_a_field_flag_is_masked_like_one_given_to_the_model():
    """``-F`` and ``--body-file`` join the body after the model: the key is masked all the same."""
    options = {"dry_run": True, "field": ["proxy[password]=x", "proxy[port]=1"]}
    guard = SendGuard(options, CallerFields(options))
    endpoint = Endpoint(HTTPMethod.POST, "connections", json=_Connection(host="db", logins=[]))
    with httpx2.Client(base_url="https://api.test/v1/") as client:
        request = endpoint.request(client)
        with pytest.raises(DryRunPlanned) as planned:
            guard(Effect.WRITE, request)
    assert planned.value.plan.body["proxy"] == {"password": "***", "port": 1}


def test_a_generated_connection_carries_the_marks_of_its_specification():
    """The document's secrets and two maps it leaves unmarked; a path, a certificate are none."""
    from ycli.yandex.datalens.schemas import connection

    marked = {
        name
        for model in vars(connection).values()
        if isinstance(model, type) and issubclass(model, BaseModel)
        for name in secret_keys(model)
    }
    assert marked == {
        *("password", "token", "access_token", "refresh_token", "client_secret"),
        *("credentials", "auth_header", "jwt", "secret_headers", "extra_credentials"),
    }
