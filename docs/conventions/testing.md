# Testing conventions

What a resource ships with, which test catches what, and how the suite stays honest. Agreed in
[the test decision on #95](https://github.com/bim-ba/ycli/issues/95#issuecomment-5938982896).

## Kinds of tests

| Kind | What it proves | How it is written |
|---|---|---|
| Contract | the SDK, CLI and MCP reach each operation with the same requests (method, path, query, body), carrying the credentials; MCP hints match the strongest effect sent; the SDK keeps what the API returned; the CLI prints the SDK result and MCP returns the same data, also when the API answers with an empty object | one `Case` per way of reaching an operation in `tests/yandex/<domain>/<resource>/cases.py`, all driven by `tests/test_contract.py` |
| Registry & architecture | parity, layers, effects, one output path, single sources, DI, typed boundaries | `tests/architecture/`, import-linter, signature snapshots — small and hand-written |
| Models | logic on a model that no contract case reaches | a resource has no `test_models.py` of its own: that a reply parses into its models (aliases, unions, validators) is proved by the contract cases, which check the SDK result against the reply. One is written only for a line or branch nothing else covers, and holds only those tests (`tests/yandex/tracker/links/test_models.py`, the `Link` properties). That every field is described is checked once for all models (`tests/test_conventions.py::test_every_model_field_has_a_description`) |
| Unit | logic only: validators, auth flows, paginators, error mapping, settings | by hand, next to the code it covers (`tests/yandex/core/`, `tests/yandex/test_settings.py`) |
| Special behaviour | errors, multi-step flows (`--wait` polling), guards that refuse a request, paging quirks of one API | by hand, only where a contract case cannot reach |
| Live e2e | the real API accepts what ycli sends and reaches the expected state | YAML scenarios in `e2e/` run against the test organization, outside the coverage gate; see [`e2e/README.md`](../../e2e/README.md) |

A resource on the core ships its endpoint declarations, its contract cases and its models. It
has no per-surface `test_client.py` / `test_cli.py` / `test_mcp.py` repeating the same request
three times: a resource stops carrying those as soon as its cases exist. Each pagination kind is
tested once, in `tests/yandex/core/`, not per resource.

## Writing contract cases

- **Fail-closed coverage.** Every operation, CLI command and MCP tool of a resource on the core
  needs a case, and every operation must be reached by at least one CLI and one MCP case unless
  its client method is marked `# violation(arch-1)`. A case of an operation that does not exist fails too.
- **Distinct values.** Give every case its own ids and fully populated bodies, with every option
  set to a non-default value. A value shared by two parameters, or an option left at its
  default, lets a surface that swaps or drops it pass.
- **Literal expectations.** Write the expected method, path, query and body as literals, never
  computed from the endpoint declarations or the models they test.
- **Several requests.** A case lists every exchange in order; a tool that reads and then writes is
  checked against the strongest effect of all its requests.
- **One surface only.** A case may set `cli=None` or `mcp=None` when another case of the same
  operation covers that surface (a CLI-only default, say).
- **Results.** The SDK result is checked against the reply: a parsed model keeps the reply's
  values, a listing keeps every page's items, bytes match exactly. State `output=` for a result
  no reply holds (an `Ack` the client makes up, a listing a limit cuts short, an envelope merged
  from pages) and `cli_output=` for a command that prints only part of the result. `env=` sets
  variables for the CLI and MCP runs (a small `YCLI__HTTP__MAX_ITEMS` proves `--all` lifts the cap).

## Mocking HTTP

- The `api` fixture (`tests/conftest.py`) answers through
  `httpx2.MockTransport` via the one seam `ycli.yandex.core.session.default_transport`. An autouse
  fixture keeps every other core request offline, so a missing stub fails loudly.
- `MockAPI` takes `api.add(method, url, json=…)` answers and records `api.calls`
  (`api.body(i)` parses a JSON body).

## Rules

- **A check is proven by a bite.** A new or changed guard ships with a test that feeds it the
  defect it exists for (`…_bites`); older guards in `tests/architecture/` gain one when
  they are next touched.
- **Retries never sleep in tests.** `stamina.set_testing` (autouse) keeps the attempt count and
  drops the waits.
- **Coverage stays at 100% of lines and branches** (`branch = true`, `--cov-fail-under=100`). It
  proves code ran, not that it is right; the kinds above are what make it meaningful.
