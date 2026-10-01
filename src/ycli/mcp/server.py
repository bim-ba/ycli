"""Root Yandex 360 FastMCP server — mounts the per-domain subservers.

Run over stdio for LLM-agent clients: ``ycli mcp start`` (or ``python -m ycli.mcp``).
Tools are namespaced per registered service (``tracker_*``, ``wiki_*``, ``forms_*``). Reads
and writes; ``--read-only`` serves the reads-only view.
"""

from fastmcp import FastMCP

from ycli.yandex.mcp import WRITE_TAG
from ycli.yandex.registry import SERVICES
from ycli.yandex.status.mcp import mcp as status_mcp

mcp = FastMCP(
    "yandex",
    instructions=(
        "Read/write access to Yandex 360. Tools are namespaced per service: "
        + "; ".join(f"{service.name}_* — {service.help}" for service in SERVICES)
        + ". Every tool carries honest annotations: reads have readOnlyHint=true; writes have "
        "readOnlyHint=false and an explicit destructiveHint — treat destructiveHint=true tools "
        "(delete/clear/abort) with care. Credentials come from the YANDEX_ID_OAUTH_TOKEN and "
        "YANDEX_ID_ORGANIZATION_ID environment variables."
    ),
)
for service in SERVICES:
    mcp.mount(service.mcp_server(), namespace=service.name)
mcp.mount(status_mcp, namespace="status")


def main(read_only: bool = False) -> None:
    """Run the root server over stdio (the console-script entry point).

    ``read_only=True`` hides every write-tagged tool, restoring the pre-write surface.

    Example:
        >>> main()  # doctest: +SKIP
    """
    if read_only:
        mcp.disable(tags={WRITE_TAG})
    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
