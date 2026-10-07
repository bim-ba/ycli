"""DataLens MCP resources: what a user attaches."""

from ycli.yandex.datalens.dependencies import TAGS
from ycli.yandex.mcp import guide, new_server

mcp = new_server("datalens-resources")


@mcp.resource(
    "ycli://guide",
    name="guide",
    title="How to work with Yandex DataLens through ycli",
    mime_type="text/markdown",
    tags=TAGS,
)
def datalens_guide() -> str:
    """How to work with Yandex DataLens through these tools: how to sign in, and what is wrapped."""
    return guide("ycli.yandex.datalens.mcp")
