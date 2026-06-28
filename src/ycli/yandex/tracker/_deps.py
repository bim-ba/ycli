"""FastMCP dependency provider for the tracker subserver — builds a TrackerClient per call."""
from ycli.yandex.tracker.client import TrackerClient

RO: dict[str, bool] = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True}
TAGS: set[str] = {"tracker"}


def tracker_client() -> TrackerClient:
    """Provide an env-built TrackerClient to tracker MCP tools (FastMCP caches within a call)."""
    return TrackerClient.from_env()
