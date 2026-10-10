"""Shared FastMCP tool annotations + the per-request client/config providers.

Providers run on every tool call (FastMCP ``Depends``), so a rotated token or an edited
``.env`` takes effect on the next call without restarting the server, and nothing is cached
at module level. Building a domain client costs a few milliseconds (TrackerClient ~9 ms),
negligible next to the HTTP round trip it serves.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from importlib.resources import files
from typing import TYPE_CHECKING, Annotated, Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.exceptions import ValidationError as ArgumentsRefused
from fastmcp.server.dependencies import get_access_token, get_http_request
from fastmcp.server.middleware import Middleware
from fastmcp.server.transforms import Transform
from fastmcp.tools.base import ToolResult
from pydantic import Field, SecretStr, ValidationError
from pydantic_core import to_jsonable_python

from ycli.settings import (
    AppConfig,
    Credentials,
    MCPHTTPConfig,
    ProfileError,
    missing_credentials,
)
from ycli.yandex.core.continuation import HANDLES, NOTHING_ELSE, RULE
from ycli.yandex.core.guard import Guard, PlannedRequest, RequestPlanned
from ycli.yandex.errors import next_step
from ycli.yandex.factory import build_client
from ycli.yandex.models import field_error

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Sequence
    from contextlib import AbstractContextManager

    import mcp.types as mt
    from fastmcp.server.auth import AuthProvider
    from fastmcp.server.middleware import CallNext, MiddlewareContext
    from fastmcp.server.transforms import GetToolNext
    from fastmcp.tools import Tool
    from fastmcp.utilities.versions import VersionSpec

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
# Meta of a tool an agent needs before any other (`status_get`, `schema_get`): a client that
# hides tools behind a search step keeps it in sight. Claude Code reads this key
# (https://code.claude.com/docs/en/mcp, "Exempt a server from deferral"); others pass it by.
ALWAYS_LOAD: dict[str, bool] = {"anthropic/alwaysLoad": True}
# Meta of a tool whose operation grants access (``Endpoint.grants_access``): a client that
# honours it asks a person on every call, whatever mode it runs in, and denies the call where
# nobody can be asked. Claude Code reads this key (https://code.claude.com/docs/en/mcp,
# "Require approval for a specific tool", v2.1.214 or later); others pass it by, so the
# description of the tool says it in words (``ycli.mcp.listing.GrantsSaid``).
GRANTS_ACCESS: dict[str, bool] = {"anthropic/requiresUserInteraction": True}
GRANTS_ACCESS_SAID = "Grants access: a client that honours the mark asks a person on every call."
# Meta keys of a prompt and of a resource template: the root-server tool names a prompt's
# text tells the model to call, and the read tool a resource repeats. The server offers
# neither when one of those tools is not served (ycli.mcp.listing.ServedWithTheirTools).
NEEDS_TOOLS = "ycli_needs_tools"
REPEATS_TOOL = "ycli_repeats_tool"
# The tail of every listing tool's `limit` description. It names the setting, not its value,
# so the text stays true when HTTPConfig.max_tool_items or the environment changes the cap.
LIMIT_CAP = "omitted means the configured cap of a tool (YCLI__HTTP__MAX_TOOL_ITEMS)."
# The other two handles of a listing, the same on every tool that has `limit` (#502).
All = Annotated[
    bool,
    Field(
        description="Return everything, ignoring the cap. A long listing is better taken in "
        "pieces: `limit`, then `next`."
    ),
]
Next = Annotated[
    str | None,
    Field(
        description="Go on from where an earlier call stopped, with the `next` it returned: "
        f"{RULE}."
    ),
]
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
        ...         [survey.id for survey in client.surveys.list(limit=500)]
        ['686d0a1b2c3d4e5f00000001']
    """

    @contextmanager
    def provide() -> Iterator[C]:
        asked = _DRY_RUN.get()
        # Under `dry_run` the client's own guard stops the first write: nothing a tool does
        # with the client can send one. The call is told that its client is the guarded one.
        guard = Guard(dry_run=True) if asked is not None else None
        with build_client(client_cls, caller_credentials(), app_config(), guard=guard) as client:
            if asked is not None:
                asked.guarded = True
            try:
                yield client
            except RequestPlanned as planned:
                # The write the guard stopped is the answer of the call, not a failure of it:
                # told on as an error FastMCP does not log, with no traceback of the signal.
                raise _Planned(planned.plan) from None

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
        given = context.message.arguments or {}
        if given.get("next") is not None and context.fastmcp_context is not None:
            # A token carries its listing: a filter given anew would be passed over silently.
            tool = await context.fastmcp_context.fastmcp.get_tool(context.message.name)
            needed = set(tool.parameters.get("required", [])) if tool else set(given)
            beside = sorted(
                name
                for name, value in given.items()
                if value is not None and name not in needed | HANDLES
            )
            if beside:
                raise ToolError(f"{NOTHING_ELSE} (given: {', '.join(beside)})")
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


class _Planned(ToolError):  # noqa: N818  # the answer of a call, not an error of it
    """A call under ``dry_run`` that reached its first write; ``plan`` is that write.

    A ``ToolError`` so that FastMCP hands it on as it is, and at a level below every level a
    log is read at: a plan is what was asked for.
    """

    def __init__(self, plan: PlannedRequest) -> None:
        super().__init__("planned, not sent", log_level=logging.NOTSET + 1)
        self.plan = plan


@dataclass
class _DryRunAsked:
    """One call that asked for a plan; ``guarded`` once its client was built with the guard.

    An object and not a flag: a tool that is not a coroutine runs in a thread with a copy of
    the context, and what the copy is told there has to be seen here.
    """

    guarded: bool = False


# Set for the one call that asked for a plan, and for nothing after it.
_DRY_RUN: ContextVar[_DryRunAsked | None] = ContextVar("ycli_dry_run", default=None)
DRY_RUN = "dry_run"
#: The one description of `dry_run`, on every tool that writes.
DRY_RUN_SAID = (
    "Send nothing: answer `{dry_run: true, request}`, the first write the tool would make "
    "(null: none)."
)
# FastMCP's mark of an output schema whose answer is not an object and goes under `result`.
_WRAPS = "x-fastmcp-wrap-result"
# What a tool answers under `dry_run`, beside its own answer in its output schema.
PLAN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "dry_run": {"const": True},
        "request": {"type": ["object", "null"]},
        # There only when the request would grant access: such a call asks a person.
        "grants_access": {"const": True},
    },
    "required": ["dry_run", "request"],
    "additionalProperties": False,
}


def _writes(tool: Tool) -> bool:
    """Whether ``tool`` says of itself that it writes: only such a tool has a plan."""
    return tool.annotations is not None and tool.annotations.read_only_hint is False


class DryRun(Middleware):
    """Answers a tool called with ``dry_run`` by the request it would send, sending none.

    One place for every tool that writes: the argument is taken out of the call here, the
    client the tool is given is built with the core's guard (:func:`client_provider`), and
    the write the guard stopped is answered as the plan. A tool that only reads has no such
    argument, and is told so like any argument it does not have.

    :func:`new_server` adds it to every server of ycli.
    """

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        """The tool's result, or under ``dry_run`` the request it would have sent."""
        given = dict(context.message.arguments or {})
        inside = sorted(name for name, value in given.items() if _says_dry_run(value))
        if not (DRY_RUN in given or inside) or context.fastmcp_context is None:
            return await call_next(context)
        tool = await context.fastmcp_context.fastmcp.get_tool(context.message.name)
        if tool is None or not _writes(tool):
            return await call_next(context)  # refused below as an argument it does not have
        if inside:
            # One who nests it believes they are planning: that must not end in a write.
            raise ToolError(
                f"`{DRY_RUN}` is the tool's own argument: give it beside `{inside[0]}`, "
                "not inside it"
            )
        asked = given.pop(DRY_RUN)
        if not isinstance(asked, bool):
            raise ToolError("The arguments do not fit the tool:\n  dry_run: true or false")
        without = context.copy(message=context.message.model_copy(update={"arguments": given}))
        if not asked:
            return await call_next(without)
        call = _DryRunAsked()
        token = _DRY_RUN.set(call)
        try:
            await call_next(without)
        except _Planned as planned:
            return _planned(planned.plan, tool)
        finally:
            _DRY_RUN.reset(token)
        if not call.guarded:
            # Its client was not the guarded one, so what it sent is not known: never a plan.
            raise ToolError(f"{context.message.name} cannot be run with dry_run: it ran for real")
        return _planned(None, tool)  # the guard let every request through: all were reads


#: The argument, and the spellings of it one might write inside a body in its place.
_SPELLED = frozenset({DRY_RUN, "dryRun", "dry-run"})


def _says_dry_run(value: object) -> bool:
    """Whether ``value``, an argument of a call, has a key that spells ``dry_run`` at any depth."""
    if isinstance(value, dict):
        return bool(_SPELLED & value.keys()) or any(map(_says_dry_run, value.values()))
    return isinstance(value, list) and any(map(_says_dry_run, value))


def _planned(request: PlannedRequest | None, tool: Tool) -> ToolResult:
    """The plan as an answer of ``tool``, lying where the tool's own answers lie.

    Under ``result`` for a tool that answers a list, as FastMCP puts those. The request is
    written out by the serializer FastMCP writes every answer with, the model's own.
    """
    plan: dict[str, Any] = {DRY_RUN: True, "request": request}
    if request is not None and request.grants_access:
        plan["grants_access"] = True
    written = to_jsonable_python(plan, by_alias=True)
    wrapped = bool(tool.output_schema and tool.output_schema.get(_WRAPS))
    return ToolResult(structured_content={"result": written} if wrapped else written)


class DryRunOffered(Transform):
    """Lists ``dry_run`` on every tool that writes, and the plan beside its own answer.

    One statement for all of them: no tool declares the argument, and none of them could
    forget it. A server mounted in another passes its tools through here twice, which changes
    nothing the second time.
    """

    @staticmethod
    def _offered(tool: Tool) -> Tool:
        if not _writes(tool) or DRY_RUN in tool.parameters.get("properties", {}):
            return tool
        argument = {"type": "boolean", "default": False, "description": DRY_RUN_SAID}
        properties = {**tool.parameters.get("properties", {}), DRY_RUN: argument}
        changed: dict[str, Any] = {"parameters": {**tool.parameters, "properties": properties}}
        own = tool.output_schema
        # The plan first: it is told by `dry_run: true` and takes no other key, so an answer of
        # the tool is never read as one, while the tool's own models take any object.
        if own is not None and own.get(_WRAPS):
            answer = {"anyOf": [PLAN_SCHEMA, own["properties"]["result"]]}
            changed["output_schema"] = {
                **own,
                "properties": {**own["properties"], "result": answer},
            }
        elif own is not None:
            # The definitions the tool's schema refers to stay at the root, where its
            # references look for them; the plan has none of its own to clash with them.
            beside = {key: value for key, value in own.items() if key != "$defs"}
            defs = {"$defs": own["$defs"]} if "$defs" in own else {}
            changed["output_schema"] = {"type": "object", "anyOf": [PLAN_SCHEMA, beside], **defs}
        return tool.model_copy(update=changed)

    async def list_tools(self, tools: Sequence[Tool]) -> Sequence[Tool]:
        """The tools, each one that writes offering ``dry_run``."""
        return [self._offered(tool) for tool in tools]

    async def get_tool(
        self, name: str, call_next: GetToolNext, *, version: VersionSpec | None = None
    ) -> Tool | None:
        """The tool ``name``, offering ``dry_run`` when it writes."""
        tool = await call_next(name, version=version)
        return None if tool is None else self._offered(tool)


class NextSteps(Middleware):
    """Ends a tool's error with the next step the CLI prints under ``Hint:``.

    An agent that gets a 403, a 404 or a 429 is told what a person is told
    (:func:`~ycli.yandex.errors.next_step`): one place holds the words. An error with no next
    step is left to FastMCP as it is.
    """

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        """The tool's result; an error that has a next step says it."""
        try:
            return await call_next(context)
        except ToolError as failed:
            # FastMCP has worded the tool's failure already and keeps what failed as its cause.
            hint = next_step(failed.__cause__)
            # A server this one is mounted in gets the error with the hint under it already.
            if hint is None or str(failed).endswith(hint):
                raise
            raise ToolError(f"{failed}\nHint: {hint}") from failed.__cause__


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
    server.add_middleware(DryRun())
    server.add_middleware(ArgumentRefusals())
    server.add_transform(DryRunOffered())
    server.add_middleware(NextSteps())
    return server
