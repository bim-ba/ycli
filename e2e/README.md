# Live e2e scenarios

Unit tests prove that ycli sends the request we meant; these scenarios prove that what we meant is right. Each one runs the real `ycli -o json …` binary against the Yandex 360 **test organization** and checks the state every step reaches. Spec: [#129](https://github.com/bim-ba/ycli/issues/129).

They live outside `tests/`, so the 100% coverage gate and the fake credentials of `tests/conftest.py` do not apply, and a plain `uv run pytest` never collects them.

## Run locally

Use credentials of the test organization only: the scenarios create, change and delete objects.

```bash
set -a; . ./.env; set +a          # YANDEX_ID_OAUTH_TOKEN, YANDEX_ID_ORGANIZATION_ID
export YCLI_E2E=1                  # without it every live test is skipped
uv run pytest e2e --no-cov -n 0 -m "live and smoke"   # the pull-request subset
uv run pytest e2e --no-cov -n 0 -m live               # everything (the nightly run)
uv run pytest e2e --no-cov -n 0 -m live -k wiki       # one scenario
```

`--no-cov` is required: the repository's pytest options enforce coverage of `ycli`, which runs in a subprocess here. `-n 0` keeps the live scenarios serial instead of the four parallel workers the unit suite uses. `YCLI_E2E_QUEUE` overrides the Tracker sandbox queue (default `YCLIPAGE`).

## Scenario files

`scenarios/<service>/<name>.yaml`, validated by `models.py` (unknown keys fail):

| Key | Meaning |
|---|---|
| `name`, `smoke` | test id; `smoke: true` also runs on pull requests |
| `steps[].run` | arguments after `ycli -o json --yes`; `${RUN}`, `${QUEUE}`, `${FILES}` (the directory `e2e/files`) and saved names are substituted |
| `steps[].output` | `json` (default) or `text` for commands that print raw text, such as `wiki pages get` |
| `steps[].expect` | JMESPath expression → expected value; `unique(array)` is added for duplicate checks |
| `steps[].save` | name → JMESPath expression; later steps use `${name}` |
| `steps[].cleanup` | command run when the scenario ends, newest first, even after a failure |
| `steps[].disarms` | earlier step ids whose cleanup this step already did |
| `steps[].reads` | commands that only read, run right after the step and only by a recording run (below) |

Every object a run creates is named after `${RUN}` = `e2e-<unix seconds>-<4 hex>`. Tracker issues cannot be deleted through the API, so issue scenarios end with the issue closed in the sandbox queue.

`tests/tooling/test_e2e_scenarios.py` checks offline, on every pull request, that each file parses and each `run`, `cleanup` and read is a valid ycli command line.

## Recording replies

```bash
set -a; . ./.env; set +a
YCLI_E2E=1 uv run pytest e2e --no-cov -n 0 -p no:cacheprovider --record
```

`--record` runs the same scenarios through the CLI in this process instead of the installed binary, lets every request through to the real API and keeps the fullest good reply of each operation as `tests/fixtures/replies/<service>/<resource>/<method>.json`. A fixture is never edited by hand: record again and review the diff. `tests/contract/test_recorded_replies.py` then checks, offline, that the model of each operation reads its recorded reply.

The repository is public, so a reply is scrubbed before it is written (`scrub.py`), and what reaches the file is decided by a list of what is allowed, not by what looks personal:

| In the reply | In the file |
|---|---|
| a key the model of that position reads; in an object a model reads, also a name that is public already (a field of another model, a name in `scripts/api_snapshot/`) | kept |
| any other key, and every key of an object no model reads | `<unknown-N>`, numbered in the order of the names; a key of a map (`dict[str, X]`) becomes `<key-N>` |
| a string the model lists as a `Literal` or enum value there | kept |
| any other string | `<key>`; a date becomes one constant |
| a boolean, `null`, a number below 100 000 under a key that names no identifier | kept |
| any other number | 1 |
| a list | one item per distinct shape |

A fixture also counts the keys its model does not know (`unknown_keys`); the offline check fails when a model stops knowing a key it knew. Their names, and the reads that failed, go to the file `--record-report` names (outside the repository); the terminal shows numbers only.

While the `reads` of a step run, the command gets `--dry-run` and the network seam refuses, before sending, any request whose endpoint does not declare the effect `read`. `--record-to DIR` writes somewhere else than the committed fixtures.

## Janitor

A failed cleanup or a cancelled job can leave objects behind. The janitor closes open Tracker issues in the sandbox queue and deletes Wiki pages and Forms surveys whose name carries a run stamp older than the cutoff, at most `--max` per call, and prints each object it touches:

```bash
uv run python -m e2e.janitor --older-than 6h --max 200 --dry-run   # list only
uv run python -m e2e.janitor --older-than 6h --max 200
```

In CI the sweep after the scenarios takes `--runs-file`: each scenario appends its run name to
the file named by `YCLI_E2E_RUNS_FILE`, and only objects those runs named are removed, so a run
started meanwhile on a developer's machine keeps its own.

Objects starting with `e2e-` but without a run stamp are reported and left alone.

## CI

`.github/workflows/e2e.yml`: the smoke subset on pull requests from branches of this repository (forks get no secrets), every scenario nightly and on manual dispatch (optional `-k` input). Runs are serialized by the `yandex-e2e` concurrency group and read their credentials from the `yandex-e2e` environment. The OAuth token is not refreshed in CI: when the preflight `ycli auth status` fails, reissue the token and update the secret.
