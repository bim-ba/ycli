"""``OutputFormat`` — the global ``--format`` choices (kept apart so the CLI root stays light)."""

import enum


class OutputFormat(enum.StrEnum):
    """CLI ``--format`` choices."""

    auto = "auto"
    json = "json"
    yaml = "yaml"
    pretty = "pretty"
