# Changelog

All notable changes to this project are documented here, newest first, following
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). From v0.2.0 on, every
entry below is generated automatically by
[python-semantic-release](https://python-semantic-release.readthedocs.io/) from the
[Conventional Commits](https://www.conventionalcommits.org/) on `main` — do not edit
released sections by hand.

<!-- version list -->

## v0.9.0 (2026-06-29)

### Bug Fixes

- **status**: Discriminate the auth me union to survive the MCP round-trip
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

### Build System

- Make the demo render pretty, realistic output ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Render demo output from committed fixtures, not hand-typed text
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Sync uv.lock project version to 0.8.1 ([#15](https://github.com/bim-ba/ycli/pull/15),
  [`b442d41`](https://github.com/bim-ba/ycli/commit/b442d4157a72605d221eadd8cc296efb53b86481))

### Code Style

- Collapse the test_settings monkeypatch line (ruff format)
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

### Continuous Integration

- Drop the CI-bypass marker from the demo-GIF auto-commit
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Mint a GitHub App token for PSR so it can push past branch protection
  ([#17](https://github.com/bim-ba/ycli/pull/17),
  [`e0674b5`](https://github.com/bim-ba/ycli/commit/e0674b5136a3b53071cfdb10d3ceae8b6dec4e14))

### Documentation

- Add module docstrings to the four empty __init__.py files
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Add round-4 architecture refactor design spec ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Add round-4 implementation plan (6 tasks) ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Regenerate demo GIF ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- **readme**: Match badge style to DeepWiki (flat, logos, semantic colors)
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

### Features

- Remove the raw issues 'full' accessor and RawMapping
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Round-4 architecture refactor (remove RawMapping/full, status & mcp packages, pagination generics,
  reproducible demo) ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Status package with native me + read-only status_get MCP tool
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

### Refactoring

- Drop underscore prefixes from internal yandex modules
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Flatten API ref wrappers to scalars via BeforeValidator
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Move the MCP server + CLI into a ycli.mcp package ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Simplify the pretty renderer to lay out flat models
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Type pagination strategies with PEP 695 generics ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- **cli**: Drop the lazy __getattr__ shim; reference ycli.cli.app explicitly
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- **cli**: Group cli/context/output into the ycli.cli package
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- **cli**: Split domain _args.py into _types.py + _utils.py
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

### Testing

- Align changelog/wiki-comments model test names with the flat-field shape
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Cover render.py unknown-command path + tighten renderer list test
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Harden status_get wiki assertion + doc/typing nits ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))


## v0.8.1 (2026-06-29)

### Bug Fixes

- Detect mcp sub-app via registered_groups in post-build smoke test
  ([#14](https://github.com/bim-ba/ycli/pull/14),
  [`5175d2f`](https://github.com/bim-ba/ycli/commit/5175d2f02e71e8ad03f02f58b3c83d82153cd5a1))


## v0.8.0 (2026-06-29)

### Bug Fixes

- **arch-4**: Route issues full through Serializer; forbid json.dumps outside output.py
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **tracker**: Model transition target status (to) faithfully; realistic _execute test fixtures
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

### Build System

- Add ty type checker (advisory CI gate while ty is beta)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Sync uv.lock project version to 0.7.0 ([#11](https://github.com/bim-ba/ycli/pull/11),
  [`e7788b5`](https://github.com/bim-ba/ycli/commit/e7788b5e4cf3488f6f8b72b91a260a5baa8393f3))

### Chores

- Commit graphify code-graph routine and built graph snapshot
  ([#13](https://github.com/bim-ba/ycli/pull/13),
  [`0972035`](https://github.com/bim-ba/ycli/commit/0972035194e580f91d6ff233a5ddd0561396a100))

- **graph**: Gitignore graphify output; /codegraph-regen command (local index)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

### Code Style

- Adopt ruff formatter (mechanical reformat, no behavior change)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Enable ruff lint (E,W,F,I,N,UP,B,A,C4,SIM,PTH,RUF) with autofix
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Ratchet ruff ANN+TC (annotations + type-checking imports)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **ruff**: Suppress B008 for fastmcp Depends via config, drop 25 inline noqa
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

### Documentation

- Add Task D5 (align issues count CLI<->MCP surface) to round-3 plan
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Design spec for round-3 (tooling, composition/DI, surface, conventions, infra)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Fix stale idioms in README/CLAUDE/skills; update demo tape+shim; regen gif
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Implementation plan for round-3 (A tooling, B DI, C transport, D dedup, E surface, F infra)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Regenerate demo GIF [skip ci] ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **conventions**: Correct resources.md enforcement table (APIModel/naming are code-review only)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **drift**: Seed drift log with three round-2/round-3 genuine entries
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **mcp**: Write tool-metadata standard; scaffold comment; assert description+output schema
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **readme**: Minimalist flat-square badges + DeepWiki + PyPI
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

### Features

- Round-3 architecture + tooling refactor (ARCH-1..11, ruff+ty, mcp sub-app)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **arch**: Add ARCH-11 doc-drift guard and close drift-log entry
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **cli**: Mcp Typer sub-app (mcp start/methods); delete mcp_launcher; regen snapshots
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **commands**: /snapshot-regen and /release-checklist
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **tracker**: Align issues_count MCP tool with the CLI's query/filter capability
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **tracker**: Model transitions execute as TransitionList; render via Serializer
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

### Refactoring

- Hoist settings to top-level ycli.settings; update ARCH-8 path
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Move APIModel base into ycli.yandex.models (thin top-level)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Rename auth.py->status.py (keep 'auth status'); fold probes into ServiceProbe
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **conventions**: Me models -> APIModel; drop dead forms/_models; rename surveys models;
  resources.md ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **di**: ClientFactory + cached MCP factory; collapse _deps; slim AppContext
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **di**: Inject AppConfig via Depends(app_config)/AppContext.config; no on-the-fly settings
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **output**: Decompose PrettyStrategy into RichCell + split list-table builders
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **output**: Remove Tracker-only deeplink (ARCH-5 leak); defer general deeplink design
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **pagination**: Hoist single-page list wrapper into collect_single_page helper
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **transport**: _raise_typed as Transport staticmethod; extract _authorization seam
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))


## v0.7.0 (2026-06-28)

### Build System

- Sync uv.lock project version to 0.6.0
  ([`c9ec02e`](https://github.com/bim-ba/ycli/commit/c9ec02e2f42ac3b8a55f2a5bf7c5ad4990d03636))

### Code Style

- **transport**: Restore PEP8 blank line; assert base= applies hook+adapter
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

### Documentation

- Design spec for round-2 architecture refactor (DI, serialization, pagination, ARCH rules)
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- Implementation plan for round-2 architecture refactor (13 tasks, 6 phases)
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- Rename ApiModel -> APIModel in round-2 spec ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- Revise MCP DI to per-domain @functools.cache factory (fastmcp-canonical)
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- Revise round-2 spec — raw-arg clients + Serializer service
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **arch**: Align ARCH-10 Check with enforcement (max_items not grep-enforced — HTTP 500 collision)
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **arch**: ARCH-4 serialization confinement; add ARCH-7..10 (DI, single config, typed errors,
  no-shadow) ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

### Features

- Round-2 architecture refactor (raw-arg DI, Serializer, pagination strategies, ARCH-7..10)
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **config**: Add YCLI_MAX_ITEMS pagination cap (default 500)
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **forms**: Answers list_all via NextUrlStrategy, bounded by --limit/--all
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **pagination**: PaginationStrategy ABC + SinglePage/Cursor/NextUrl strategies
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **wiki**: Auto-paginate pages descendants (CursorStrategy) → flat PageRefList; --limit/--all
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **wiki,forms**: Unwrap comments/attachments/surveys envelopes to flat RootModel collections
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

### Refactoring

- **cli**: Dedupe KeyArg into _args.py; standardize _group anchors; modernize scaffold template
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **di**: Raw-arg composition clients + AppContext; rewrite CLI call sites via Serializer; drop
  cliformat/_clideps/from_env(CLI) ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **mcp**: Per-domain @cache client factories (fastmcp canonical); delete from_env/FromEnvSession
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **models**: Consolidate four _Lenient bases into a single APIModel
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **output**: Add Serializer service + SerializationStrategy.from_format; fold helpers into
  PrettyStrategy ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **transport**: Raw oauth_token arg + bare-session base injection; inline org header
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

### Testing

- **forms**: Limit-spans-pages drain test; assert single-fetch on page-1 cap
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **models**: Exercise APIModel lenient parsing at runtime, not just config
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **output**: Assert from_format covers all four formats; dedupe io import
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **tracker**: Stub TrackerClient via raw args, not a pre-authed session
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **wiki**: De-duplicate list tests via page_size assertion; PEP8 blank lines
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **wiki**: Drop dead import; --all test drains two pages; assert page_size=100
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))


## v0.6.0 (2026-06-28)

### Build System

- Sync uv.lock project version to 0.5.0
  ([`e2f63de`](https://github.com/bim-ba/ycli/commit/e2f63de7348b9343a0c3c8e71bdd96470f72a2ce))

### Features

- Internals cleanup — env settings, transport, output strategies, multi-service auth, wiki me,
  config fixes
  ([`5d45127`](https://github.com/bim-ba/ycli/commit/5d451274f3798a85cb9061ab36af35dc9b3630a1))


## v0.5.0 (2026-06-28)

### Build System

- Sync uv.lock project version to 0.4.0
  ([`ddb8dfe`](https://github.com/bim-ba/ycli/commit/ddb8dfe40b144dc7aa54f06eb632ecf652af50ed))

### Features

- Track C — UX quick-wins (typed errors, MCP metadata, completion, tracker me, auth status, key
  links)
  ([`a19cad7`](https://github.com/bim-ba/ycli/commit/a19cad7484dc22dc8883928d8e2f3a20a3f45747))


## v0.4.0 (2026-06-27)

### Features

- Track B — AI-infra hardening (CI-skip guard, gitleaks, bundled plugin MCP, release/conventions
  docs)
  ([`5ae61ad`](https://github.com/bim-ba/ycli/commit/5ae61ad938631c76daf6202e1318bbbd6f1d5623))


## v0.3.0 (2026-06-27)

### Features

- Architecture guardrails enforcing the six ARCH invariants
  ([`6bbc381`](https://github.com/bim-ba/ycli/commit/6bbc38148a9a0b930171210351166a7cac51b128))


## v0.2.1 (2026-06-27)

### Bug Fixes

- Ship PEP 561 py.typed marker so type checkers see ycli's types
  ([`22986e4`](https://github.com/bim-ba/ycli/commit/22986e4c0992e580112e99a16f0bc1d8492eea29))

### Continuous Integration

- Re-trigger release pipeline for the pending py.typed fix
  ([`69458c1`](https://github.com/bim-ba/ycli/commit/69458c1a3b91661aa798f16eb4d86f31d9469084))


## v0.2.0 (2026-06-27)

### Continuous Integration

- Automate releases with python-semantic-release
  ([`982256e`](https://github.com/bim-ba/ycli/commit/982256e98baf3df3023ef0bfca7ffa39ae1ff617))

### Features

- Global --format/-o for CLI output (auto/json/yaml/pretty)
  ([`ccab9a3`](https://github.com/bim-ba/ycli/commit/ccab9a3ebffcde5752a2a580bce23439abf13f02))


## [0.1.0] — 2026-06-27

### Added
- Initial release: Yandex 360 toolkit for **Tracker**, **Wiki**, and **Forms**.
- Four surfaces from one codebase: Typer **CLI** (`ycli` / `yandex-cli`), FastMCP **server**
  (`ycli mcp`, read-only, `[mcp]` extra), importable **Python SDK** (`ycli.yandex.*`), and a
  **Claude Code plugin** (`plugins/yandex-360/`).
- Published on PyPI as **`yandex-cli`** (`uv add yandex-cli`, or `yandex-cli[mcp]` for the server).
- Test suite at 100% coverage with `responses`-stubbed HTTP.
