"""Cross-cutting auth surface — `auth status`/`login`, `<service> auth status`, `status_get`.

Not a `<domain>/<resource>` package (ARCH-1 four-surface symmetry does not apply): it reports
whose token it is (Yandex ID), the organization (API 360) and one probe per registered service
(each domain client's own ``probe()``). Import the CLI from ``ycli.yandex.status.cli``:
re-exporting it here would pull Typer into the MCP server.
"""
