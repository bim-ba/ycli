"""The one place e2e reads its own configuration from the environment."""

from __future__ import annotations

import os

QUEUE_VARIABLE = "YCLI_E2E_QUEUE"
DEFAULT_QUEUE = "YCLIPAGE"  # the owner's sandbox queue: Tracker issues cannot be deleted


# What only the owner of the organization can name: a scenario variable -> the environment
# variable that gives it. A step that needs one of them is skipped while it is not set.
OPTIONAL_VARIABLES = {
    # Someone else to grant access to: a Yandex uid. Nobody is granted anything without it.
    "GRANTEE": "YCLI_E2E_GRANTEE",
    # A second sandbox queue: issues are moved into it, and it is deleted and restored.
    "QUEUE_2": "YCLI_E2E_QUEUE_2",
    # A local field and a trigger kept in the sandbox queue for the run to edit: neither can
    # be deleted through the API, so a run must not make its own.
    "LOCAL_FIELD": "YCLI_E2E_LOCAL_FIELD",
    "TRIGGER": "YCLI_E2E_TRIGGER",
}


def optional_variables() -> dict[str, str]:
    """The optional scenario variables that are set: ``{"QUEUE_2": "YCLIMOVE"}``."""
    return {
        name: value
        for name, variable in OPTIONAL_VARIABLES.items()
        if (value := os.environ.get(variable))
    }


def sandbox_queue() -> str:
    """The Tracker queue scenarios write to: ``$YCLI_E2E_QUEUE``, else ``YCLIPAGE``."""
    return os.environ.get(QUEUE_VARIABLE, DEFAULT_QUEUE)
