"""Cross-cutting auth-status surface — the `auth status` CLI plus the `status_get` MCP tool.

Not a `<domain>/<resource>` package (ARCH-1 four-surface symmetry does not apply): it probes
every registered service's `me` endpoint and reports one identity per service. Import the CLI
from ``ycli.yandex.status.cli``: re-exporting it here would pull Typer into the MCP server.
"""
