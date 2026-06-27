# Skills & commands conventions

How to name and author Claude Code skills (shipped in the `yandex-360` plugin) and
slash-commands (repo-local, under `.claude/commands/`). New skills/commands MUST follow
this; it is the spec the architecture review and any future authoring pass check against.

## Naming

- **Plugin skills** live in `plugins/yandex-360/skills/<name>/SKILL.md`. Names are
  `yandex-360` (the umbrella entry point) and `yandex-360-<domain>` per service —
  `yandex-360-tracker`, `yandex-360-wiki`, `yandex-360-forms`. A new domain skill follows
  the same `yandex-360-<domain>` pattern.
- **Repo slash-commands** live in `.claude/commands/<name>.md`. Names are kebab-case
  `verb-noun` — the existing `/new-endpoint` and `/arch-review` are the worked examples. A
  new command names the action first (`generate-…`, `check-…`, `review-…`).

## Frontmatter

- `SKILL.md` requires YAML frontmatter with `name` and `description`. The `description`
  starts with "Use when …" and names the triggering situation, so the agent can match it
  (e.g. "Use when creating, reading, or transitioning Yandex Tracker issues …").
- A slash-command `.md` requires a `description:` frontmatter line — one sentence, present
  tense, stating what the command does (see `.claude/commands/arch-review.md`).

## Directory layout (skills)

A skill directory contains:

- `SKILL.md` — the entry point (always loaded when the skill activates).
- `rules/NN-*.md` (optional) — **always-on** behavior, numbered for order
  (`01-workflow.md`). Use `rules/` only for guidance the agent must follow every time the
  skill is active.
- `references/*.md` (optional) — **on-demand** lookups the agent reads when it needs them
  (quick-reference tables, API quirk catalogues). Use `references/` for material that is
  too large or situational to always load.

Rule of thumb: if the agent must obey it on every task, it is a `rule`; if it looks it up
when relevant, it is a `reference`.

## Placement

- Repo-only developer tooling (generators, review gates) → `.claude/commands/`. These are
  not distributed with the plugin.
- User-facing domain capability (driving Tracker/Wiki/Forms) → `plugins/yandex-360/skills/`.

## Authoring checklist

Before committing a new skill or command, confirm:

- [ ] Name follows the scheme above (`yandex-360-<domain>` skill, or kebab `verb-noun` command).
- [ ] Frontmatter is complete; the description starts with "Use when …" (skills) or states the action (commands).
- [ ] It is in the correct place (repo command vs plugin skill).
- [ ] `rules/` holds only always-on behavior; situational material is in `references/`.
- [ ] A new plugin skill is listed in the plugin README's skills table and routed from the `yandex-360` umbrella skill where relevant.
