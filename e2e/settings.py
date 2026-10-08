"""The one place e2e reads its own configuration from the environment."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from ycli.settings import (
    CLOUD_ORGANIZATION_ID_ENV,
    IAM_TOKEN_ENV,
    OAUTH_TOKEN_ENV,
    ORGANIZATION_ID_ENV,
    SERVICE_ACCOUNT_KEY_ENV,
    SERVICE_ACCOUNT_KEY_FILE_ENV,
)

if TYPE_CHECKING:
    from ycli.yandex.core.profile import ServiceProfile

QUEUE_VARIABLE = "YCLI_E2E_QUEUE"
DEFAULT_QUEUE = "YCLIPAGE"  # the owner's sandbox queue: Tracker issues cannot be deleted


# What only the owner of the organization can name: a scenario variable -> the environment
# variable that gives it. A step that needs one of them is skipped while it is not set.
OPTIONAL_VARIABLES = {
    # Someone else to grant access to: a Yandex uid. Nobody is granted anything without it.
    "GRANTEE": "YCLI_E2E_GRANTEE",
    # A second sandbox queue: issues are moved into it, and it is deleted and restored.
    "QUEUE_2": "YCLI_E2E_QUEUE_2",
    # The key of a queue to make, once: a deleted queue keeps its key, so a run names none.
    "NEW_QUEUE": "YCLI_E2E_NEW_QUEUE",
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


# Every variable whose value must never show in a log: the runner cuts them out of excerpts.
CREDENTIAL_VARIABLES = (
    OAUTH_TOKEN_ENV,
    IAM_TOKEN_ENV,
    SERVICE_ACCOUNT_KEY_ENV,
    ORGANIZATION_ID_ENV,
    CLOUD_ORGANIZATION_ID_ENV,
)


def missing_credentials(profile: ServiceProfile) -> str | None:
    """What the environment lacks to reach a service with this profile; ``None`` when nothing.

    The profile says it all: whether the service takes an OAuth token besides the ways of
    Yandex Cloud, and which kind of organization it is asked for. One way to sign in and one
    organization the service takes are enough.
    """
    ways = [IAM_TOKEN_ENV, SERVICE_ACCOUNT_KEY_FILE_ENV, SERVICE_ACCOUNT_KEY_ENV]
    if profile.oauth_token:
        ways.insert(0, OAUTH_TOKEN_ENV)
    organizations = [
        variable
        for header, variable in (
            (profile.org_header, ORGANIZATION_ID_ENV),
            (profile.cloud_org_header, CLOUD_ORGANIZATION_ID_ENV),
        )
        if header is not None
    ]
    lacking = [
        " or ".join(group) for group in (ways, organizations) if not any(map(os.environ.get, group))
    ]
    return "set " + " and ".join(lacking) if lacking else None


def sandbox_queue() -> str:
    """The Tracker queue scenarios write to: ``$YCLI_E2E_QUEUE``, else ``YCLIPAGE``."""
    return os.environ.get(QUEUE_VARIABLE, DEFAULT_QUEUE)
