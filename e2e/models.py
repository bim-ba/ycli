"""The scenario file format: a YAML list of real ``ycli`` commands and the state each must reach."""

from __future__ import annotations

from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Step(BaseModel):
    """One ``ycli -o json --yes <run>`` call and what its output must show.

    ``expect`` maps a JMESPath expression to the value it must yield; ``save`` maps a variable
    name to a JMESPath expression whose value later steps use as ``${name}``. ``cleanup`` is a
    command registered once the step succeeds and run last-in-first-out when the scenario ends;
    ``disarms`` names earlier steps whose cleanup this step already performed.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    run: str
    output: Literal["json", "text"] = Field(
        default="json", description="text: the command prints raw text (e.g. page markdown)."
    )
    expect: dict[str, Any] = Field(default_factory=dict)
    save: dict[str, str] = Field(default_factory=dict)
    cleanup: str | None = None
    disarms: tuple[str, ...] = ()


class Scenario(BaseModel):
    """A named sequence of steps; ``smoke`` scenarios also run on every pull request."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    smoke: bool = False
    steps: tuple[Step, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _steps_reference_earlier_cleanups(self) -> Self:
        """Step ids are unique, and ``disarms`` only names an earlier step that has a cleanup."""
        with_cleanup: set[str] = set()
        seen: set[str] = set()
        for step in self.steps:
            if step.id in seen:
                raise ValueError(f"duplicate step id {step.id!r}")
            for target in step.disarms:
                if target not in with_cleanup:
                    raise ValueError(f"step {step.id!r} disarms {target!r}: no earlier cleanup")
            seen.add(step.id)
            if step.cleanup is not None:
                with_cleanup.add(step.id)
        return self

    def commands(self) -> list[str]:
        """Every command template the scenario can run: each step's ``run`` and ``cleanup``."""
        return [
            command
            for step in self.steps
            for command in (step.run, step.cleanup)
            if command is not None
        ]
