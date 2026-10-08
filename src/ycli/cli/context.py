"""CLI composition root — reads the environment once per invocation and builds what commands need.

Stored on ``ctx.obj`` by the root callback. Everything is lazy, so ``--help`` and commands that
make no API call never need credentials.
"""

from dataclasses import dataclass, field
from typing import Any, cast

from ycli.cli.body_fields import CallerFields
from ycli.cli.guard import SendGuard, guard_of
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
    # One for the invocation: the caller's fields go into one body only.
    _caller_fields: CallerFields | None = None

    @property
    def profile(self) -> str | None:
        """The ``--profile`` option of this invocation, on either side of the subcommand."""
        return self.options.get("profile")

    @property
    def caller_fields(self) -> CallerFields:
        """What ``--body-file`` and ``-F`` gave, shared by the guard and the commands that ask."""
        if self._caller_fields is None:
            self._caller_fields = CallerFields(self.options)
        return self._caller_fields

    @staticmethod
    def provides(kind: object) -> bool:
        """Whether a parameter annotated ``kind`` is filled by :meth:`resolve`."""
        return kind in {AppConfig, CallerFields} or (
            isinstance(kind, type) and issubclass(kind, DomainClient)
        )

    @staticmethod
    def sends(kind: object) -> bool:
        """Whether a command given ``kind`` can send a request body: a client or the fields."""
        return kind is not AppConfig

    def resolve[T](self, kind: type[T]) -> T:
        """The ``kind`` instance for this invocation: the config, or a client built once."""
        if kind is AppConfig:
            return cast("T", self.config)
        if kind is CallerFields:
            return cast("T", self.caller_fields)
        if not issubclass(kind, DomainClient):
            raise TypeError(
                f"AppContext provides AppConfig, CallerFields and domain clients, not {kind!r}"
            )
        if kind not in self._clients:
            # Raises a ValidationError naming the missing variables when credentials are unset,
            # a ProfileError when the named profile cannot be used.
            self._credentials = self._credentials or Credentials.load(self.profile)
            # Built when a command first reaches for a client: the leaf's options are in by then.
            self._clients[kind] = build_client(
                kind,
                self._credentials,
                self.config,
                before_send=SendGuard(self.caller_fields),
                guard=guard_of(self.options),
            )
        return cast("T", self._clients[kind])
