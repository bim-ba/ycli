"""``ycli doctor``: check, in order, what a working call needs and say what to fix.

The checks are the ones ``auth status`` makes (the owner from Yandex ID, the organization from
API 360, one probe per registered service) plus what a first run trips over: where the
credentials come from, which extras are installed and whether a newer release is out. A check
that cannot run after an earlier failure is ``skipped``, so one cause is reported once.
"""

from __future__ import annotations

from importlib.metadata import version
from importlib.util import find_spec
from typing import TYPE_CHECKING

from ycli.cli.errors import exit_code_for
from ycli.cli.exit_codes import ExitCode
from ycli.settings import ORGANIZATION_ID_ENV
from ycli.yandex.errors import YandexAuthError, YandexConnectionError, YandexError
from ycli.yandex.factory import build_client
from ycli.yandex.registry import SERVICES
from ycli.yandex.status.models import Check, DoctorReport
from ycli.yandex.status.release_client import DISTRIBUTION, is_newer, latest_release
from ycli.yandex.status.reporter import organization_status, probe_error
from ycli.yandex.status.token_client import TokenClient

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ycli.settings import AppConfig, Credentials

SIGN_IN = "run `ycli auth login`"
NO_CONNECTION = "no connection"
# The extras a person may be missing: the module each one installs, and what it adds.
EXTRAS = {"mcp": ("fastmcp", "the MCP server"), "jq": ("jq", "the `--jq` filter")}


class _Diagnosis:
    """The checks so far, the exit status of the first failure, and why later ones are skipped."""

    def __init__(self) -> None:
        self.checks: list[Check] = []
        self.exit_code = ExitCode.OK
        self.blocked = ""

    def passed(self, check: str, detail: str) -> None:
        self.checks.append(Check(check=check, status="ok", detail=detail))

    def warned(self, check: str, detail: str, fix: str) -> None:
        self.checks.append(Check(check=check, status="warn", detail=detail, fix=fix))

    def failed(self, check: str, detail: str, fix: str, exit_code: ExitCode) -> None:
        self.checks.append(Check(check=check, status="fail", detail=detail, fix=fix))
        if self.exit_code is ExitCode.OK:
            self.exit_code = exit_code

    def skipped(self, check: str, why: str = "") -> None:
        self.checks.append(Check(check=check, status="skipped", detail=why or self.blocked))

    def unreachable(self, check: str, error: YandexConnectionError, proxies: Sequence[str]) -> None:
        """A request that never completed: every later request would fail the same way."""
        proxy = f"; proxy variables set: {', '.join(proxies)}" if proxies else ""
        self.failed(
            check,
            f"no connection: {error}{proxy}",
            "check the network and the proxy settings",
            ExitCode.TRANSIENT,
        )
        self.blocked = NO_CONNECTION


def diagnose(
    credentials: Credentials | None,
    sources: Mapping[str, str],
    proxies: Sequence[str],
    config: AppConfig,
) -> tuple[DoctorReport, ExitCode]:
    """Every check in order, and the exit status: 0 unless a check failed.

    Args:
        credentials: The credentials, or ``None`` when they are not set.
        sources: Where each credential variable is set (``settings.credential_sources``).
        proxies: The names of the proxy variables that are set.
        config: The HTTP settings.

    Returns:
        The report and the exit status of its first failed check.
    """
    diagnosis = _Diagnosis()
    where = "; ".join(f"{name}: {source}" for name, source in sources.items())
    if credentials is None:
        diagnosis.failed("credentials", where, SIGN_IN, ExitCode.AUTH)
        diagnosis.blocked = "the credentials are not set"
        diagnosis.skipped("token")
        diagnosis.skipped("organization")
    else:
        diagnosis.passed("credentials", where)
        _check_owner(diagnosis, credentials, proxies, config)
    for service in SERVICES:
        _check_service(diagnosis, service.name, credentials, proxies, config)
    for extra, (module, adds) in EXTRAS.items():
        installed = find_spec(module) is not None
        hint = "installed" if installed else f"not installed: `yandex-cli[{extra}]` adds {adds}"
        diagnosis.passed(f"extra:{extra}", hint)
    _check_version(diagnosis)
    failed = diagnosis.exit_code is not ExitCode.OK
    return DoctorReport(ok=not failed, checks=diagnosis.checks), diagnosis.exit_code


def _check_version(diagnosis: _Diagnosis) -> None:
    """The installed version against the latest release on PyPI (no credentials are sent)."""
    installed = version(DISTRIBUTION)
    if diagnosis.blocked == NO_CONNECTION:
        diagnosis.skipped("version")
        return
    try:
        latest = latest_release()
    except YandexError as error:
        diagnosis.skipped("version", f"{installed} is installed; PyPI did not answer: {error}")
        return
    if is_newer(latest, installed):
        diagnosis.warned(
            "version",
            f"{installed} is installed, {latest} is out",
            f"`uv tool upgrade {DISTRIBUTION}`",
        )
    else:
        diagnosis.passed("version", f"{installed} is the latest release")


def _check_owner(
    diagnosis: _Diagnosis, credentials: Credentials, proxies: Sequence[str], config: AppConfig
) -> None:
    """Whether Yandex ID accepts the token, then whether the organization is one it can see."""
    token = credentials.oauth_token.get_secret_value()
    with TokenClient(oauth_token=token, http=config.http) as token_client:
        try:
            identity = token_client.identity()
        except YandexAuthError:
            diagnosis.failed("token", "Yandex ID rejected the token", SIGN_IN, ExitCode.AUTH)
            diagnosis.blocked = "the token was rejected"
        except YandexConnectionError as error:
            diagnosis.unreachable("token", error, proxies)
        except YandexError as error:  # the owner is context: the service probes give the verdict
            diagnosis.warned("token", f"owner unknown: {error}", "run `ycli doctor` again later")
        else:
            diagnosis.passed("token", f"belongs to {identity.login}")
        if diagnosis.blocked:
            diagnosis.skipped("organization")
            return
        organization = organization_status(token_client, credentials.organization_id)
    if organization.name:
        diagnosis.passed("organization", f"{organization.name} ({organization.id})")
    else:
        diagnosis.warned(
            "organization",
            f"{organization.id}, {organization.detail}",
            f"if the services below fail, check {ORGANIZATION_ID_ENV}: `ycli auth login` finds it",
        )


def _check_service(
    diagnosis: _Diagnosis,
    name: str,
    credentials: Credentials | None,
    proxies: Sequence[str],
    config: AppConfig,
) -> None:
    """The service's own probe, the one ``auth status`` runs."""
    check = f"service:{name}"
    if credentials is None or diagnosis.blocked:
        diagnosis.skipped(check)
        return
    service = next(service for service in SERVICES if service.name == name)
    with build_client(service.client_class(), credentials, config) as client:
        error = probe_error(client)
    if error is None:
        diagnosis.passed(check, "accepts the token")
    elif isinstance(error, YandexConnectionError):
        diagnosis.unreachable(check, error, proxies)
    elif isinstance(error, YandexAuthError):
        diagnosis.failed(
            check,
            "rejects the token",
            f"give your OAuth app the {name} permissions and sign in again, or ask an "
            f"administrator to enable {name} for the organization",
            ExitCode.AUTH,
        )
    else:
        diagnosis.failed(check, str(error), "run `ycli doctor` again later", exit_code_for(error))
