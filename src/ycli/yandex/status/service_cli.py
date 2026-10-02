"""`ycli <service> auth status` — one generic command, built from a registry ``Service``.

Each domain ``cli.py`` mounts ``service_auth_app(SERVICE)`` with one line, so every service has
the same command and none re-implements it. It probes only that service; ``ycli auth status``
probes them all and also says whose token it is.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import typer

from ycli.cli.exit_codes import ExitCode
from ycli.cli.output import ExitWith
from ycli.yandex.status.models import (
    ServiceAuthStatus,  # noqa: TC001  # typer reads the return type
)
from ycli.yandex.status.reporter import TOKEN_REJECTED, probe_service

if TYPE_CHECKING:
    from ycli.yandex.service import Service


def failure_code(statuses: list[ServiceAuthStatus]) -> ExitCode:
    """The exit status for failed probes: 4 (auth) when a service rejected the token, else 1.

    Args:
        statuses: The probe results of the failed services.

    Returns:
        The exit status.

    Examples:
        >>> failure_code([ServiceAuthStatus(service="wiki", detail=TOKEN_REJECTED)])
        <ExitCode.AUTH: 4>
        >>> failure_code([ServiceAuthStatus(service="wiki", detail="503 Service Unavailable")])
        <ExitCode.FAILURE: 1>
    """
    rejected = any(status.detail == TOKEN_REJECTED for status in statuses)
    return ExitCode.AUTH if rejected else ExitCode.FAILURE


def service_auth_app(service: Service) -> typer.Typer:
    """The ``auth`` group of ``service``'s CLI: ``auth status`` probes just that service."""
    app = typer.Typer(name="auth", help=f"Check that the token works for {service.name}.")

    @app.command(help=f"Probe {service.name} with its own read; exit 1 when the token is rejected.")
    def status(ctx: typer.Context) -> ServiceAuthStatus | ExitWith:
        # The root context builds the client from the credentials, so a missing variable ends in
        # the usual "Not signed in" message.
        client = ctx.find_root().obj.resolve(service.client_class())
        result = probe_service(service.name, client)
        return result if result.valid else ExitWith(result, exit_code=failure_code([result]))

    return app
