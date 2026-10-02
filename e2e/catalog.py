"""Where scenarios live and how a file becomes a :class:`Scenario` (shared with the guard)."""

from __future__ import annotations

from pathlib import Path

import yaml

from e2e.models import Scenario

SCENARIO_DIRECTORY = Path(__file__).parent / "scenarios"


def scenario_paths(directory: Path = SCENARIO_DIRECTORY) -> list[Path]:
    """Every ``<service>/<name>.yaml`` under ``directory``, sorted for stable test ids."""
    return sorted(directory.glob("**/*.yaml"))


def load(path: Path) -> Scenario:
    """Parse one scenario file; a typo'd key fails here, offline (``extra="forbid"``)."""
    return Scenario.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
