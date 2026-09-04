"""Forms /users/me FastMCP tool (reads-only) — Depends DI, native error handling."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import RO, TAGS, forms_client
from ycli.yandex.forms.me.models import User
from ycli.yandex.models import require_found

mcp = FastMCP("forms-me")


@mcp.tool(name="me_get", annotations={**RO, "title": "Get current Forms user"}, tags=TAGS)
def get(client: FormsClient = Depends(forms_client)) -> User:
    """The authenticated Yandex Forms user (a safe auth probe)."""
    result = client.me.get()
    # Forms models are fully lenient, so a 401/4xx deserializes into an all-None User
    # instead of raising. Guard so the auth probe actually fails on failure.
    return require_found(
        result,
        sentinel=lambda r: r.id is None,
        message="auth probe failed — empty user (check configured credentials)",
    )
