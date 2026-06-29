"""Forms /users/me FastMCP tool (reads-only) — Depends DI, native error handling."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import RO, TAGS, forms_client
from ycli.yandex.forms.me.models import User

mcp = FastMCP("forms-me")


@mcp.tool(name="me_get", annotations={**RO, "title": "Get current Forms user"}, tags=TAGS)
def get(client: FormsClient = Depends(forms_client)) -> User:
    """The authenticated Yandex Forms user (a safe auth probe)."""
    result = client.me.get()
    # Forms models are fully lenient, so a 401/4xx deserializes into an all-None User
    # instead of raising. Guard so the auth probe actually fails on failure.
    if result.id is None:
        raise ValueError("auth probe failed — empty user (check YANDEX_ID_OAUTH_TOKEN)")
    return result
