"""CLI composition root — reads the environment once per invocation and builds what commands need.

Stored on ``ctx.obj`` by the root callback. Everything is lazy, so ``--help`` and commands that
make no API call never need credentials.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

from ycli.cli.guard import SendGuard
from ycli.settings import AppConfig, Credentials
from ycli.yandex.base import DomainClient
from ycli.yandex.factory import build_client


@dataclass
class AppContext:
    """Resolves a command's dependencies: the app config and any SDK domain client."""

    config: AppConfig = field(default_factory=AppConfig)
    # The root command's parsed global options (``--yes``…), the live mapping the guard reads.
    options: dict[str, Any] = field(default_factory=dict)
    _credentials: Credentials | None = None
    _clients: dict[type, DomainClient] = field(default_factory=dict)

    @property
    def profile(self) -> str | None:
        """The ``--profile`` option of this invocation, on either side of the subcommand."""
        return self.options.get("profile")

    @staticmethod
    def provides(kind: object) -> bool:
        """Whether a parameter annotated ``kind`` is filled by :meth:`resolve`."""
        return kind is AppConfig or (isinstance(kind, type) and issubclass(kind, DomainClient))

    def resolve[T](self, kind: type[T]) -> T:
        """The ``kind`` instance for this invocation: the config, or a client built once."""
        if kind is AppConfig:
            return cast("T", self.config)
        if not issubclass(kind, DomainClient):
            raise TypeError(f"AppContext provides AppConfig and domain clients, not {kind!r}")
        if kind not in self._clients:
            # Raises a ValidationError naming the missing variables when credentials are unset,
            # a ProfileError when the named profile cannot be used.
            self._credentials = self._credentials or Credentials.load(self.profile)
            self._clients[kind] = build_client(
                kind, self._credentials, self.config, before_send=SendGuard(self.options)
            )
        return cast("T", self._clients[kind])
