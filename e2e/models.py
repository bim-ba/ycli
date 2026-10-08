"""The scenario file format: a YAML list of real ``ycli`` commands and the state each must reach."""

from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Retry(BaseModel):
    """Run a step again when it fails in the one way named, a few times, with a pause.

    For a refusal the service itself calls passing (Tracker answers a change of a sprint's
    state with ``412 ... try again`` now and then, whatever came before). ``when`` is a piece
    of the failure's text: any other failure fails the step at once. A run says at its end
    which steps were retried and how many times, so the refusal stays seen.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    when: str = Field(min_length=1)
    times: int = Field(default=2, ge=1, le=5)
    pause_seconds: float = Field(default=5, ge=0, le=60)


class Step(BaseModel):
    """One ``ycli -o json --yes <run>`` call and what its output must show.

    ``expect`` maps a JMESPath expression to the value it must yield; ``save`` maps a variable
    name to a JMESPath expression whose value later steps use as ``${name}``. Both may use the
    variables set so far. ``cleanup`` is a
    command registered once the step succeeds and run last-in-first-out when the scenario ends;
    ``disarms`` names earlier steps whose cleanup this step already performed.

    ``reads`` are commands that only read, run right after the step, while what it made still
    exists, and only by a run that records replies (``pytest e2e --record``): each adds the
    reply of one more operation, and none may change the server.

    ``retry`` runs the step again on one named failure (:class:`Retry`).

    ``needs`` names variables only the owner of the organization can give (``QUEUE_2``,
    ``GRANTEE``; ``e2e/settings.py``): while one is not set the step is skipped, with its
    cleanup and its reads, and the run says so. A step that uses what a skipped step saved
    needs the same variable.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    run: str
    output: Literal["json", "text", "bytes"] = Field(
        default="json",
        description="text: the command prints raw text (e.g. page markdown). bytes: it prints "
        "a file; `expect` sees `size` and `head` (the first 16 bytes, in hex).",
    )
    expect: dict[str, Any] = Field(default_factory=dict)
    save: dict[str, str] = Field(default_factory=dict)
    cleanup: str | None = None
    disarms: tuple[str, ...] = ()
    reads: tuple[str, ...] = ()
    needs: tuple[str, ...] = ()
    retry: Retry | None = None


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
        """Every command template the scenario can run: ``run``, ``cleanup`` and the reads."""
        return [
            command
            for step in self.steps
            for command in (step.run, step.cleanup, *step.reads)
            if command is not None
        ]
