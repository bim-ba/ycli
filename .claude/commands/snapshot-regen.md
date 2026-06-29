---
description: Regenerate CLI/MCP surface snapshots after an intentional public-surface change (ARCH-6).
---

Run this command whenever the CLI command tree or the MCP tool list changes deliberately.
ARCH-6 requires that snapshot drift is always intentional — never silent.

1. Regenerate snapshots:

   ```
   uv run python -m tests.snapshots --update
   ```

2. Review the diff to confirm the change is intentional:

   ```
   git diff tests/snapshots/
   ```

   Check that every added, removed, or renamed command/tool corresponds to a deliberate change
   you just made. If you see a command or tool that you did NOT intend to change, stop — that
   is a silent public-surface regression. Revert the snapshot update, find the unintended
   change, and fix it before proceeding.

3. Confirm the snapshot tests pass with the new baseline:

   ```
   uv run pytest tests/test_snapshots.py
   ```

4. Stage the updated snapshots alongside your feature code so the PR diff shows both the
   implementation change and the surface change together (`git add tests/snapshots/`).

> **Reminder:** a snapshot diff that is NOT intentional means a public-surface change slipped in
> undetected. Treat any unexpected diff as a bug, not a formality to accept.
