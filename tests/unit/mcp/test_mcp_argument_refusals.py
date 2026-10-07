"""A refusal of a tool's arguments says what is wrong and never repeats what was sent.

FastMCP answers arguments that do not fit with the text of pydantic's error, which quotes the
value given; for a missing field that is the whole object it is missing from, with any secret
the caller sent beside it. ``ArgumentRefusals`` writes the refusal instead.
"""

import asyncio
import importlib
import pkgutil
import typing
from typing import Annotated, Any

import pytest
from fastmcp import Client, FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.exceptions import ValidationError as ArgumentsRefused
from pydantic import BaseModel, SecretStr, TypeAdapter

import ycli.yandex
from tests.full_server import mcp
from ycli.mcp.server import ArgumentRefusals

MARK = "MARK7SECRET"  # made up: no test here holds a real secret
INJECTED = {"return", "client", "config"}


def _secret_paths(schema: dict, definitions: dict, path: tuple = (), seen: tuple = ()):
    """Yield the path to every password of ``schema``; ``[]`` stands for an item of a list."""
    if "$ref" in schema:
        name = schema["$ref"].rsplit("/", 1)[-1]
        if name not in seen:
            yield from _secret_paths(definitions[name], definitions, path, (*seen, name))
        return
    if schema.get("format") == "password":
        yield path
    for key in ("anyOf", "oneOf", "allOf"):
        for member in schema.get(key, []):
            yield from _secret_paths(member, definitions, path, seen)
    for name, member in (schema.get("properties") or {}).items():
        yield from _secret_paths(member, definitions, (*path, name), seen)
    if isinstance(schema.get("items"), dict):
        yield from _secret_paths(schema["items"], definitions, (*path, "[]"), seen)
    if isinstance(schema.get("additionalProperties"), dict):
        yield from _secret_paths(schema["additionalProperties"], definitions, (*path, "{}"), seen)


def _tools_with_a_secret() -> dict[str, list[tuple]]:
    """Every served tool that takes a secret, with the paths to its secrets, read from types.

    The types of the function, not the listed schema: a body over the listing's budget is
    listed as a free-form object, and is validated as its model all the same.
    """
    found: dict[str, list[tuple]] = {}
    for module in pkgutil.walk_packages(ycli.yandex.__path__, "ycli.yandex."):
        parts = module.name.split(".")
        if parts[-1] != "mcp" or len(parts) != 5:  # ycli.yandex.<service>.<resource>.mcp
            continue
        server = importlib.import_module(module.name).mcp
        for tool in asyncio.run(server.list_tools()):
            hints = typing.get_type_hints(tool.fn, include_extras=True)
            paths: set[tuple] = set()
            for name in hints.keys() - INJECTED:
                bare = typing.get_args(hints[name])[0] if _annotated(hints[name]) else hints[name]
                schema = TypeAdapter(bare).json_schema()
                paths |= {(name, *path) for path in _secret_paths(schema, schema.get("$defs", {}))}
            if paths:
                found[f"{parts[2]}_{tool.name}"] = sorted(paths)
    return found


def _annotated(hint: Any) -> bool:
    return typing.get_origin(hint) is Annotated


def _holding(path: tuple, leaf: Any) -> Any:
    """``leaf`` at ``path``: ``_holding(("a", "[]", "b"), 1) -> {"a": [{"b": 1}]}``."""
    value = leaf
    for key in reversed(path):
        value = [value] if key == "[]" else {"k": value} if key == "{}" else {key: value}
    return value


def _beside(path: tuple, extra: dict) -> Any:
    """The secret at ``path`` with ``extra`` keys beside it."""
    return _holding(path[:-1], {path[-1]: MARK, **extra})


CASES = {
    "only the secret": lambda path: _holding(path, MARK),
    "an unknown key beside it": lambda path: _beside(path, {"zz_unknown": 1}),
    "a secret of a wrong type": lambda path: _holding(path, [MARK]),
}
WITH_A_SECRET = _tools_with_a_secret()


async def _answer(server: FastMCP, tool: str, arguments: dict) -> str:
    """What the tool says to ``arguments``: the text of its error, or of its result."""
    async with Client(server) as client:
        try:
            return str(await client.call_tool(tool, arguments))
        except ToolError as refused:
            return str(refused)


def test_the_tools_that_take_a_secret_are_found_from_their_types():
    """Not a list of names: a new tool with a ``SecretStr`` in its request is found by itself."""
    assert "forms_surveys_create" in WITH_A_SECRET
    assert ("body", "api_keys", "[]", "value") in WITH_A_SECRET["forms_surveys_create"]
    assert WITH_A_SECRET.keys() <= {tool.name for tool in asyncio.run(mcp.list_tools())}


@pytest.mark.parametrize("case", CASES)
@pytest.mark.parametrize(
    ("tool", "path"),
    [(tool, path) for tool, paths in WITH_A_SECRET.items() for path in paths],
    ids=lambda value: value if isinstance(value, str) else ".".join(value),
)
async def test_a_refusal_does_not_repeat_a_secret_of_the_request(api, tool, path, case):
    """The defect: ``input_value={'value': 'MARK7SECRET'}`` in the refusal of the arguments."""
    said = await _answer(mcp, tool, CASES[case](path))
    assert MARK not in said, said


async def test_no_refusal_of_any_tool_quotes_the_input_or_links_to_pydantic(api):
    refusals = []
    for tool in await mcp.list_tools():
        said = await _answer(mcp, tool.name, {"zz_unknown": MARK})
        assert said.startswith("The arguments do not fit the tool:\n"), (tool.name, said)
        refusals.append(said)
    assert [
        said for said in refusals if "input_value" in said or "http" in said or MARK in said
    ] == []


async def test_a_refusal_names_the_path_and_what_is_wrong():
    said = await _answer(mcp, "forms_surveys_create", {"body": {"api_keys": [{"value": MARK}]}})
    assert said == "The arguments do not fit the tool:\n  body.api_keys.0.name: is required"


class _Key(BaseModel):
    name: str
    value: SecretStr


def _bare_server() -> FastMCP:
    server = FastMCP("bare")

    @server.tool
    def keep(key: _Key) -> str:
        return key.name

    return server


async def test_without_the_middleware_fastmcp_repeats_what_was_sent():
    """What the middleware is for; if FastMCP stops doing this, the middleware can go."""
    arguments = {"key": {"value": MARK}}
    assert f"input_value={{'value': '{MARK}'}}" in await _answer(_bare_server(), "keep", arguments)
    guarded = _bare_server()
    guarded.add_middleware(ArgumentRefusals())
    assert await _answer(guarded, "keep", arguments) == (
        "The arguments do not fit the tool:\n  key.name: is required"
    )


async def test_a_refusal_that_is_not_pydantics_is_left_as_it_is():
    """FastMCP raises its own validation error in other places too; there is nothing to rewrite."""
    server = FastMCP("own")
    server.add_middleware(ArgumentRefusals())

    @server.tool
    def refuse() -> str:
        raise ArgumentsRefused("not one of ours")

    assert "not one of ours" in await _answer(server, "refuse", {})
