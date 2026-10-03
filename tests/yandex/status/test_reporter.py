"""The report: the owner, the organization and one probe per service, each failing on its own."""

import json
import logging

import pytest
from pydantic import SecretStr

from ycli.settings import AppConfig, Credentials
from ycli.yandex.status.reporter import build_report

ID_URL = "https://login.yandex.ru/info"
ORG_URL = "https://api360.yandex.net/directory/v1/org"
TRACKER_ME = "https://api.tracker.yandex.net/v3/myself"
WIKI_ME = "https://api.wiki.yandex.net/v1/users/me"
FORMS_ME = "https://api.forms.yandex.net/v1/users/me"

CREDENTIALS = Credentials(oauth_token=SecretStr("tok"), organization_id="42")


_ANSWERS = {
    "identity": (ID_URL, {"json": {"id": "7", "login": "ivan"}}),
    "organizations": (
        ORG_URL,
        {"json": {"organizations": [{"id": 41, "name": "Beta"}, {"id": 42, "name": "Acme"}]}},
    ),
    "tracker": (TRACKER_ME, {"json": {"login": "ivan"}}),
    "wiki": (WIKI_ME, {"json": {"username": "ivan"}}),
    "forms": (FORMS_ME, {"json": {"email": "ivan@x"}}),
}


def _report(api, **replaced):
    """The report with every read answering, except those in ``replaced`` (name -> answer)."""
    for name, (url, answer) in _ANSWERS.items():
        api.add("GET", url, **replaced.get(name, answer))
    return build_report(CREDENTIALS, AppConfig())


def test_the_report_names_the_owner_the_organization_and_every_service(api):
    report = _report(api)
    assert report.configured is True
    assert report.identity is not None
    assert (report.identity.id, report.identity.login) == ("7", "ivan")
    assert report.organization is not None
    assert (report.organization.id, report.organization.name) == ("42", "Acme")
    assert report.organization.detail == ""
    assert [(s.service, s.valid, s.detail) for s in report.services] == [
        ("tracker", True, ""),
        ("wiki", True, ""),
        ("forms", True, ""),
    ]


def test_the_report_dumps_with_the_agreed_shape(api):
    dumped = json.loads(_report(api).model_dump_json())
    assert set(dumped) == {
        "configured",
        "credential",
        "profile",
        "identity",
        "organization",
        "services",
    }
    assert dumped["credential"] == "oauth"
    assert dumped["organization"] == {"id": "42", "name": "Acme", "detail": ""}
    assert dumped["services"][0] == {"service": "tracker", "valid": True, "detail": ""}


@pytest.mark.parametrize("status", [401, 403])
def test_without_the_directory_scope_the_organization_keeps_its_id_and_names_the_scope(api, status):
    organizations = {"json": {"message": "No required scope"}, "status": status}
    organization = _report(api, organizations=organizations).organization
    assert organization is not None
    assert organization.id == "42"
    assert organization.name is None
    assert "directory:read_organization" in organization.detail


def test_an_organization_the_token_does_not_list_keeps_its_id_with_a_note(api):
    organizations = {"json": {"organizations": [{"id": 1, "name": "Other"}]}}
    organization = _report(api, organizations=organizations).organization
    assert organization is not None
    assert (organization.id, organization.name) == ("42", None)
    assert "do not list it" in organization.detail


def test_an_api_360_outage_is_a_note_not_a_crash(api):
    report = _report(api, organizations={"content": b"<html>down</html>", "status": 503})
    assert report.organization is not None
    assert report.organization.name is None
    assert "503" in report.organization.detail
    assert all(s.valid for s in report.services)


@pytest.mark.parametrize("status", [401, 503])
def test_an_unreadable_owner_leaves_the_report_without_one_and_logs_why(api, caplog, status):
    with caplog.at_level(logging.WARNING, logger="ycli.status"):
        report = _report(api, identity={"content": b"nope", "status": status})
    assert report.identity is None
    assert str(status) in caplog.text
    assert all(s.valid for s in report.services)


@pytest.mark.parametrize("service", ["tracker", "wiki", "forms"])
@pytest.mark.parametrize(("status", "detail"), [(401, "token invalid or expired"), (422, "422")])
def test_one_failing_service_does_not_hide_the_others(api, service, status, detail):
    failing = {"json": {"message": "no"}, "status": status}
    by_name = {s.service: s for s in _report(api, **{service: failing}).services}
    assert by_name[service].valid is False
    assert detail in by_name[service].detail
    assert all(s.valid for name, s in by_name.items() if name != service)


def test_an_iam_token_is_reported_without_asking_yandex_id_or_api_360(api):
    for name in ("tracker", "wiki", "forms"):
        api.add("GET", _ANSWERS[name][0], **_ANSWERS[name][1])
    credentials = Credentials(oauth_token=None, iam_token=SecretStr("t1.x"), organization_id="42")
    report = build_report(credentials, AppConfig())
    assert (report.credential, report.identity) == ("iam", None)
    assert report.organization is not None
    assert (report.organization.id, report.organization.name) == ("42", None)
    assert "OAuth token only" in report.organization.detail
    assert all(service.valid for service in report.services)
    assert {call.headers["Authorization"] for call in api.calls} == {"Bearer t1.x"}
    assert not any(call.url.host in {"login.yandex.ru", "api360.yandex.net"} for call in api.calls)
