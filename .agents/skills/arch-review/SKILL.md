---
name: arch-review
description: >-
  Use when reviewing the current diff against the ARCHITECTURE.md invariants
  before merge; states PASS/FAIL per invariant with file:line evidence.
---
# Architecture review

Codex has no project-scoped slash commands; this is the skill form of the repo's
`/arch-review` command, kept in sync with `.rulesync/commands/arch-review.md`.

Review the working diff (`git diff main...HEAD`) strictly against `ARCHITECTURE.md`; it holds
each rule's wording, check and exceptions, so read it rather than this summary. For each
invariant, state **PASS/FAIL** with `file:line` evidence:

- **ARCH-1 — Surface parity.** Every new SDK operation is wrapped on both the CLI and MCP, or
  added to `ARCH1_SURFACE_ASYMMETRIES` with a reason.
- **ARCH-2 — Layers.** The core imports no service or surface; no HTTP library in
  `cli.py`/`mcp.py`/`models.py`; `fastmcp` only in MCP modules; MCP never imports the CLI.
- **ARCH-3 — Honest effects.** A new core endpoint states its effect when the method misleads
  (`POST …/_search` reads); every tool's hints match its effect (core: `ARCH3_EFFECT_CASES`
  entry added; uplink: verb maps); writes carry the `write` tag.
- **ARCH-4 — One output path.** Commands return results; nothing in a `cli.py` writes stdout.
- **ARCH-5 — Single sources of truth.** No second copy of the version, env access, org header,
  an API host or a default.
- **ARCH-6 — Versioned surface.** Snapshot changes (names and signatures) are intentional.
- **ARCH-7 — Dependency injection.** Settings are built only in `ARCH7_ROOTS`.
- **ARCH-8 — Typed boundaries.** MCP write bodies are typed models; errors map through
  `errors.error_for_status` only.

Also flag **semantic drift** the checks can't see: business logic in `cli.py` that belongs in
the client; a client bypassing the session or transport; a new ad-hoc output path; an asymmetric
resource. If any invariant changed, confirm `ARCHITECTURE.md` and its check changed in the same
diff — if not, that is a FAIL (silent invariant change). End with: **APPROVE** or
**REQUEST CHANGES** + the specific fixes.
