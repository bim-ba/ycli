"""status_get MCP tool — aggregates the three /me probes into one read-only report."""

from fastmcp import Client

from ycli.yandex.status import mcp as status_mcp

TRACKER_ME = "https://api.tracker.yandex.net/v3/myself"
FORMS_ME = "https://api.forms.yandex.net/v1/users/me"
WIKI_ME = "https://api.wiki.yandex.net/v1/users/me"


async def test_status_get_reports_all_valid(api, creds):
    api.add("GET", TRACKER_ME, json={"login": "alice"}, status=200)
    api.add("GET", WIKI_ME, json={"username": "alice"}, status=200)
    api.add("GET", FORMS_ME, json={"id": 1, "email": "alice@x"}, status=200)
    async with Client(status_mcp.mcp) as client:
        result = await client.call_tool("get", {})
    # Every service reports the same Account shape, so the round-trip keeps each field.
    services = {s.service: s for s in result.data.services}
    assert services["tracker"].valid is True
    assert services["tracker"].account.login == "alice"
    assert services["forms"].account.email == "alice@x"
    assert services["wiki"].account.login == "alice"


async def test_status_get_marks_invalid_on_401(api, creds):
    api.add("GET", TRACKER_ME, status=401)
    api.add("GET", WIKI_ME, json={"username": "alice"}, status=200)
    api.add("GET", FORMS_ME, json={"id": 1, "email": "alice@x"}, status=200)
    async with Client(status_mcp.mcp) as client:
        result = await client.call_tool("get", {})
    services = {s.service: s for s in result.data.services}
    assert services["tracker"].valid is False
    assert services["tracker"].detail == "token invalid or expired"


async def test_status_get_is_read_only():
    async with Client(status_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert "get" in tools
    assert tools["get"].annotations.read_only_hint is True


async def test_status_get_is_annotated_as_a_read():
    """status_get is the one tool outside a resource, so the contract test does not see it."""
    from ycli.yandex.mcp import RO

    async with Client(status_mcp.mcp) as client:
        tool = next(tool for tool in await client.list_tools() if tool.name == "get")
    hints = tool.annotations.model_dump(by_alias=True) if tool.annotations else {}
    assert {key: hints.get(key) for key in RO} == RO
