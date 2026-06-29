"""Cross-cutting auth-status surface — the `auth status` CLI plus the `status_get` MCP tool.

Not a `<domain>/<resource>` package (ARCH-1 four-surface symmetry does not apply): it
aggregates the three domains' `me` probes into one report.
"""

from ycli.yandex.status.cli import app

__all__ = ["app"]
