"""Shared FastMCP tool annotations + the per-request client/config providers.

Providers run on every tool call (FastMCP ``Depends``), so a rotated token or an edited
``.env`` takes effect on the next call without restarting the server, and nothing is cached
at module level. Building a domain client costs a few milliseconds (TrackerClient ~9 ms),
negligible next to the HTTP round trip it serves.
"""

from __future__ import annotations

from contextlib import contextmanager
from importlib.resources import files
from typing import TYPE_CHECKING, Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.exceptions import ValidationError as ArgumentsRefused
from fastmcp.server.dependencies import get_access_token, get_http_request
from fastmcp.server.middleware import Middleware
from pydantic import SecretStr, ValidationError

from ycli.settings import (
    AppConfig,
    Credentials,
    MCPHTTPConfig,
    ProfileError,
    missing_credentials,
)
from ycli.yandex.factory import build_client
from ycli.yandex.models import field_error

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from contextlib import AbstractContextManager

    import mcp.types as mt
    from fastmcp.server.auth import AuthProvider
    from fastmcp.server.middleware import CallNext, MiddlewareContext
    from fastmcp.tools.base import ToolResult

    from ycli.yandex.base import DomainClient

RO: dict[str, bool] = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True}
# Write-tool annotation sets (ARCH-3 annotation honesty). The MCP-spec default for an
# unannotated tool is destructiveHint=true, so every write declares its hints explicitly:
# WRITE = additive create-style call; WRITE_IDEMPOTENT = PATCH-style edit (safe to repeat);
# DESTRUCTIVE = delete/clear/abort (removes data irreversibly).
WRITE: dict[str, bool] = {
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": True,
}
WRITE_IDEMPOTENT: dict[str, bool] = {**WRITE, "idempotentHint": True}
DESTRUCTIVE: dict[str, bool] = {**WRITE, "destructiveHint": True}
# Tag carried by every write tool — `ycli mcp start --read-only` disables it wholesale.
WRITE_TAG = "write"
# Meta keys of a prompt and of a resource template: the root-server tool names a prompt's
# text tells the model to call, and the read tool a resource repeats. The server offers
# neither when one of those tools is not served (ycli.mcp.listing.ServedWithTheirTools).
NEEDS_TOOLS = "ycli_needs_tools"
REPEATS_TOOL = "ycli_repeats_tool"
# The tail of every listing tool's `limit` description. It names the setting, not its value,
# so the text stays true when HTTPConfig.max_items or the environment changes the cap.
LIMIT_CAP = "omitted means the configured cap (YCLI__HTTP__MAX_ITEMS)."
# The most a tool's input schema may weigh, as ``len(json.dumps(schema))`` of what the server
# lists. A client reads every tool's schema before the first call, and some cut a large one
# short; a body that would take a tool over the budget is declared with :class:`OverBudget`.
SCHEMA_BUDGET_BYTES = 32_768
# The key of a parameter's schema that names the model to read with ``schema_get``.
SCHEMA_ADDRESS = "x-ycli-schema"


class OverBudget:
    """Marks a tool parameter whose schema would take the tool over ``SCHEMA_BUDGET_BYTES``.

    ``body: Annotated[Subscription, OverBudget(SUBSCRIPTION, "The integration.")]`` lists the
    parameter as a free-form object and says where its schema is; the value is still
    validated by the model, so the tool receives a typed body and a call
    with a wrong field is refused with the field's path. ``address`` is ``module:name`` of the
    model or the named union, as the service registry writes addresses; the ``schema_get`` tool
    serves it, one definition at a time. The description is given here, not in a ``Field``:
    what the marker writes is the whole of the parameter's schema.

    Examples:
        >>> from typing import Annotated
        >>> from pydantic import TypeAdapter
        >>> from ycli.yandex.status.models import Check
        >>> marked = Annotated[Check, OverBudget("ycli.yandex.status.models:Check", "A check.")]
        >>> schema = TypeAdapter(marked).json_schema()
        >>> schema["type"], schema["x-ycli-schema"]
        ('object', 'ycli.yandex.status.models:Check')
        >>> schema["description"].startswith("A check. Its schema is not listed here")
        True
    """

    def __init__(self, address: str, description: str) -> None:
        self.address = address
        self.description = description

    def __get_pydantic_json_schema__(self, core_schema: object, handler: object) -> dict[str, Any]:
        """The parameter as the listing shows it: free-form, with the address of its schema."""
        name = self.address.rpartition(":")[2]
        service = self.address.split(".")[2]
        return {
            "type": "object",
            "description": (
                f"{self.description} Its schema is not listed here: read `{name}` with "
                f'schema_get(service="{service}", name="{name}"), then the definitions it '
                "refers to."
            ),
            SCHEMA_ADDRESS: self.address,
        }


def guide(package: str) -> str:
    """The guide shipped in ``package`` as ``guide.md``: the plugin's skill for that service.

    The file is a link to the plugin's ``SKILL.md`` in the repository and a copy of it in the
    wheel, so a client without the plugin reads the same text.

    Args:
        package: The package that holds ``guide.md``, e.g. ``ycli.yandex.tracker.mcp``.

    Returns:
        The guide's Markdown.

    Examples:
        >>> guide("ycli.yandex.tracker.mcp").splitlines()[1]
        'name: yandex-360-tracker'
    """
    return files(package).joinpath("guide.md").read_text(encoding="utf-8")


def caller_credentials() -> Credentials:
    """The credentials of one tool call: the caller's own Yandex token over HTTP, else the env.

    Over HTTP the server's OAuth layer has already signed the caller in through Yandex ID and
    holds their Yandex token (the MCP client only ever holds the server's own token, so nothing
    the client sends is passed on). The organization is the server's configured one. An HTTP
    call without a signed-in caller is refused: it never falls back to the environment's token.
    Over stdio the active profile's file, or else the process environment and ``.env``, is
    read, per call.

    FastMCP hides any other exception behind "Failed to resolve dependency 'client'", which
    tells an agent nothing, so every failure here is a ``ToolError`` naming what is missing.
    """
    caller = get_access_token()
    if caller is not None:
        # The organization the server checked at start (MCPHTTPConfig), so both agree.
        organization_id = MCPHTTPConfig().organization_id  # ty: ignore[missing-argument]
        # The caller's own token only: an IAM token in the server's environment is not theirs.
        return Credentials(
            oauth_token=SecretStr(caller.token), iam_token=None, organization_id=organization_id
        )
    if _over_http():
        raise ToolError("Not signed in: this HTTP request carries no authenticated caller.")
    try:
        return Credentials.load()
    except ProfileError as exc:
        raise ToolError(f"Invalid configuration: {exc}") from exc
    except ValidationError as exc:
        missing = missing_credentials(exc)
        if not missing:
            if exc.title != Credentials.__name__:
                raise
            # Two tokens at once: the error says which.
            raise ToolError(f"Invalid configuration: {exc.errors()[0]['msg']}") from exc
        raise ToolError(
            f"Not signed in — {', '.join(missing)} "
            f"{'are' if len(missing) > 1 else 'is'} not set. Set them in the environment the "
            "MCP server runs in (or its .env), or run `ycli auth login` to obtain a token."
        ) from exc


def _over_http() -> bool:
    """Whether the current tool call arrived over HTTP (``False`` over stdio)."""
    try:
        get_http_request()
    except RuntimeError:
        return False
    return True


def app_config() -> AppConfig:
    """The app config for one tool call (read per call, like the credentials)."""
    return AppConfig()


def client_provider[C: DomainClient](
    client_cls: type[C],
) -> Callable[[], AbstractContextManager[C]]:
    """A zero-argument provider for ``Depends`` that builds ``client_cls`` for each call.

    ``Depends`` enters the context manager before the tool runs and exits it after, so the
    client's connection pools close when the call ends.

    Examples:
        >>> from unittest.mock import patch
        >>> from ycli.settings import Credentials
        >>> from ycli.yandex.forms.client import FormsClient
        >>> forms_client = client_provider(FormsClient)
        >>> credentials = Credentials(oauth_token="token", organization_id="org")
        >>> with patch("ycli.yandex.mcp.caller_credentials", return_value=credentials):
        ...     with forms_client() as client:
        ...         [survey.id for survey in client.surveys.list(limit=500).root]
        ['686d0a1b2c3d4e5f00000001']
    """

    @contextmanager
    def provide() -> Iterator[C]:
        with build_client(client_cls, caller_credentials(), app_config()) as client:
            yield client

    return provide


class ArgumentRefusals(Middleware):
    """Says what is wrong with a tool's arguments without repeating what was sent.

    FastMCP answers arguments that do not fit with the text of pydantic's error, which quotes
    the value given: for a field that is missing, the whole object it is missing from, and
    with it a password or a key the caller sent beside it. This writes the refusal as the CLI
    does, :func:`~ycli.yandex.models.field_error`: the path and what is wrong, nothing else.
    A request the tool's body could not build from arguments that fit is said the same way,
    under the CLI's heading: FastMCP alone answers it "Invalid request parameters".

    :func:`new_server` adds it to every server of ycli.
    """

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        """The tool's result; arguments that do not fit are refused with our own text."""
        try:
            return await call_next(context)
        except ArgumentsRefused as refused:
            if not isinstance(refused.__cause__, ValidationError):
                raise
            wrong = refused.__cause__.errors(include_input=False, include_url=False)
            # ``from None``: the cause holds the arguments, and a client may be shown it.
            raise ToolError(
                "The arguments do not fit the tool:\n" + "\n".join(map(field_error, wrong))
            ) from None
        except ValidationError as unbuilt:
            # The arguments fit, and the request they make does not (a read that names both a
            # branch and a revision): FastMCP would answer "Invalid request parameters" alone.
            wrong = unbuilt.errors(include_input=False, include_url=False)
            raise ToolError(
                "The request cannot be built:\n" + "\n".join(map(field_error, wrong))
            ) from None


def new_server(
    name: str, *, instructions: str | None = None, auth: AuthProvider | None = None
) -> FastMCP:
    """A server of ycli: the root one, a service's, a resource's. Every one is built here.

    What all of them must do is added in this one place, so a server run alone does it as the
    root server does: today :class:`ArgumentRefusals`. One mounted in another carries it
    twice, which changes nothing: the inner one has already written the refusal.
    The function goes when it adds nothing to ``FastMCP(name)``.

    Args:
        name: The server's name.
        instructions: What a client is told about the server.
        auth: The sign-in provider for HTTP; ``None`` over stdio.

    Returns:
        The server, with nothing mounted and no tool yet.

    Examples:
        >>> new_server("forms-surveys").name
        'forms-surveys'
    """
    server = FastMCP(name, instructions=instructions, auth=auth)
    server.add_middleware(ArgumentRefusals())
    return server
