"""CLI composition root — reads the env once and hands raw primitives to the clients."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from rich.console import Console

if TYPE_CHECKING:
    import typer

from ycli.output import OutputFormat, SerializationStrategy
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.settings import AppConfig, Credentials
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.wiki.client import WikiClient


@dataclass
class AppContext:
    """Stored on ``ctx.obj`` by the root callback; lazy so ``--help`` needs no credentials."""

    output_format: OutputFormat
    _credentials: Credentials | None = None
    _config: AppConfig | None = None
    _console: Console | None = None
    _clients: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_typer_context(cls, ctx: typer.Context) -> AppContext:
        return ctx.obj

    @property
    def console(self) -> Console:
        if self._console is None:
            self._console = Console()
        return self._console

    @property
    def strategy(self) -> SerializationStrategy:
        return SerializationStrategy.from_format(self.output_format)

    def _client(self, name: str, factory: type) -> object:
        if name not in self._clients:
            self._credentials = self._credentials or Credentials()  # ty: ignore[missing-argument]  # raises if env unset
            self._config = self._config or AppConfig()
            self._clients[name] = factory(
                oauth_token=self._credentials.oauth_token,
                organization_id=self._credentials.organization_id,
                timeout_seconds=int(self._config.timeout_seconds),
                retries=self._config.retries,
            )
        return self._clients[name]

    @property
    def tracker(self) -> TrackerClient:
        return self._client("tracker", TrackerClient)  # type: ignore[return-value]  # ty: ignore[invalid-return-type]

    @property
    def wiki(self) -> WikiClient:
        return self._client("wiki", WikiClient)  # type: ignore[return-value]  # ty: ignore[invalid-return-type]

    @property
    def forms(self) -> FormsClient:
        return self._client("forms", FormsClient)  # type: ignore[return-value]  # ty: ignore[invalid-return-type]
