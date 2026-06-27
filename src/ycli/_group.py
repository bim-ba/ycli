"""A Typer/Click group that appends a difflib 'Did you mean?' hint on unknown commands."""
from __future__ import annotations

import difflib
from typing import Any

import typer.core


class SuggestGroup(typer.core.TyperGroup):
    """On an unknown subcommand, fail with the closest valid name suggested."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Take over suggestion logic ourselves; disable typer's built-in duplicate.
        kwargs["suggest_commands"] = False
        super().__init__(*args, **kwargs)

    def get_command(self, ctx: Any, cmd_name: str) -> Any:
        command = super().get_command(ctx, cmd_name)
        if command is not None:
            return command
        matches = difflib.get_close_matches(cmd_name, self.list_commands(ctx), n=1)
        hint = f" Did you mean '{matches[0]}'?" if matches else ""
        ctx.fail(f"No such command '{cmd_name}'.{hint}")
