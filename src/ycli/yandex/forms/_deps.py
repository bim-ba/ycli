"""FastMCP dependency provider for the forms subserver — builds a FormsClient per call."""
from ycli.yandex.forms.client import FormsClient

RO: dict[str, bool] = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True}
TAGS: set[str] = {"forms"}


def forms_client() -> FormsClient:
    """Provide an env-built FormsClient to forms MCP tools (FastMCP caches within a call)."""
    return FormsClient.from_env()
