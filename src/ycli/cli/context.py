"""CLI composition root — reads the environment once per invocation and builds what commands need.

Stored on ``ctx.obj`` by the root callback. Everything is lazy, so ``--help`` and commands that
make no API call never need credentials.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import cast

from ycli.settings import AppConfig, Credentials
from ycli.yandex.base import DomainClient
from ycli.yandex.factory import ClientFactory


@dataclass
class AppContext:
    """Resolves a command's dependencies: the app config and any SDK domain client."""

    config: AppConfig = field(default_factory=AppConfig)
    _credentials: Credentials | None = None
    _clients: dict[type, DomainClient] = field(default_factory=dict)

    @staticmethod
    def provides(kind: object) -> bool:
        """Whether a parameter annotated ``kind`` is filled by :meth:`resolve`."""
        return kind is AppConfig or (isinstance(kind, type) and issubclass(kind, DomainClient))

    def resolve[T](self, kind: type[T]) -> T:
        """The ``kind`` instance for this invocation: the config, or a client built once."""
        if kind is AppConfig:
            return cast("T", self.config)
        if kind not in self._clients:
            # Raises a ValidationError naming the missing variables when credentials are unset.
            self._credentials = self._credentials or Credentials()  # ty: ignore[missing-argument]
            self._clients[kind] = ClientFactory.build(kind, self._credentials, self.config)  # ty: ignore[invalid-assignment]
        return cast("T", self._clients[kind])
