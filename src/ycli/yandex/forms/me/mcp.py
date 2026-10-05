"""Forms /users/me FastMCP tool (reads-only) — Depends DI, native error handling."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import RO, forms_client
from ycli.yandex.forms.me.models import User

mcp = FastMCP("forms-me")


@mcp.tool(name="me_get", annotations={**RO, "title": "Get current Forms user"})
def get(client: FormsClient = Depends(forms_client)) -> User:
    """The authenticated Yandex Forms user (a safe auth probe)."""
    return client.me.get()
