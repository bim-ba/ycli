"""`ycli <service> auth status` — one generic command, built from a registry ``Service``.

Each domain ``cli.py`` mounts ``service_auth_app(SERVICE)`` with one line, so every service has
the same command and none re-implements it. It probes only that service; ``ycli auth status``
probes them all and also says whose token it is.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import typer

from ycli.cli.output import ExitWith
from ycli.yandex.status.models import (
    ServiceAuthStatus,  # noqa: TC001  # typer reads the return type
)
from ycli.yandex.status.reporter import probe_service

if TYPE_CHECKING:
    from ycli.yandex.service import Service


def service_auth_app(service: Service) -> typer.Typer:
    """The ``auth`` group of ``service``'s CLI: ``auth status`` probes just that service."""
    app = typer.Typer(name="auth", help=f"Check that the token works for {service.name}.")

    @app.command(help=f"Probe {service.name} with its own read; exit 1 when the token is rejected.")
    def status(ctx: typer.Context) -> ServiceAuthStatus | ExitWith:
        # The root context builds the client from the credentials, so a missing variable ends in
        # the usual "Not signed in" message.
        client = ctx.find_root().obj.resolve(service.client_class())
        result = probe_service(service.name, client)
        return result if result.valid else ExitWith(result)

    return app
