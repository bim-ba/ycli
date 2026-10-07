"""``ExitCode`` — the process exit status of ``ycli``, one value per kind of failure.

Kept apart (no imports) so the root ``--help`` can list the table without loading the rest of
the CLI; ``ycli.cli.errors.exit_code_for`` maps an exception onto it, the README documents it.
"""

import enum


class ExitCode(enum.IntEnum):
    """What a script can branch on: ``0`` ok, then one code per kind of failure."""

    OK = 0
    FAILURE = 1  # any other failure: a 4xx the API rejected, an unmapped error
    USAGE = 2  # a bad command line, or an invalid configuration
    NOT_FOUND = 3  # the API answered 404
    AUTH = 4  # 401/403, or no credentials at all
    RATE_LIMITED = 5  # the API answered 429 and retries ran out
    TRANSIENT = 6  # a 5xx, a timeout or a lost connection: worth trying again later
    CHANGES = 7  # nothing failed: `sync status --exit-code` found files that were edited


def exit_codes_summary() -> str:
    """The table on one line, for ``--help``.

    Returns:
        One ``<value> <name>`` entry per exit code, joined by `` · ``.

    Examples:
        >>> listed = exit_codes_summary().split(" · ")
        >>> listed[:4]
        ['0 ok', '1 failure', '2 usage', '3 not found']
        >>> listed[4:]
        ['4 auth', '5 rate limited', '6 transient', '7 changes']
    """
    return " · ".join(f"{code.value} {code.name.lower().replace('_', ' ')}" for code in ExitCode)
