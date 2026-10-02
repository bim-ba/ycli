# Testing conventions

What a resource ships with, which test catches what, and how the suite stays honest. Agreed in
[#94](https://github.com/bim-ba/ycli/issues/94); the parts marked *E2* arrive as the domains
move to the httpx2 core.

## Kinds of tests

| Kind | What it proves | How it is written |
|---|---|---|
| Wire | method, path, query, body and response parsing of each operation; two pages for a listing | per resource, against `MockAPI` (`tests/mock_api.py`); *E2*: generated from the endpoint declarations |
| CLI / MCP smoke | the command or tool sends the same request; MCP hints match the endpoint's effect | `ARCH3_EFFECT_CASES` today (one row per core tool); *E2*: one `Case` per operation drives both |
| Registry & architecture | parity, layers, effects, one output path, single sources, DI, typed boundaries | `tests/test_architecture.py`, import-linter, signature snapshots — small and hand-written |
| Unit | logic only: validators, auth flows, paginators, error mapping, settings | by hand, next to the code it covers (`tests/yandex/core/`, `tests/yandex/test_settings.py`) |
| Special behaviour | `--wait` polling, uploads, unusual error shapes | by hand, only where the generic cases cannot reach |
| Live e2e | the real API accepts what ycli sends and reaches the expected state | YAML scenarios in `e2e/` run against the test organization, outside the coverage gate; see [`e2e/README.md`](../../e2e/README.md) |

A resource on the core adds its endpoint declarations, one effect case per MCP tool, and JSON
fixtures for its responses. Until the generated wire and smoke tests land (E2), it also carries
per-surface test files.

## Mocking HTTP

- Resources on the httpx2 core: the `api` fixture (`tests/conftest.py`) answers through
  `httpx2.MockTransport` via the one seam `ycli.yandex.core.session.default_transport`. An autouse
  fixture keeps every other core request offline, so a missing stub fails loudly.
- Resources still on uplink: `responses`, until they move (E2).
- `MockAPI` mirrors the `responses` API (`api.add(method, url, json=…)`, `api.calls`,
  `api.body(i)`), so moving a test is a mechanical swap.

## Rules

- **A check is proven by a bite.** A new or changed guard ships with a test that feeds it the
  defect it exists for (`…_bites`); older guards in `tests/test_architecture.py` gain one when
  they are next touched.
- **Retries never sleep in tests.** `stamina.set_testing` (autouse) keeps the attempt count and
  drops the waits.
- **Coverage stays at 100% of lines and branches** (`branch = true`, `--cov-fail-under=100`). It
  proves code ran, not that it is right; the kinds above are what make it meaningful.
