# Live e2e scenarios

Unit tests prove that ycli sends the request we meant; these scenarios prove that what we meant is right. Each one runs the real `ycli -o json …` binary against the Yandex 360 **test organization** and checks the state every step reaches. Spec: [#129](https://github.com/bim-ba/ycli/issues/129).

They live outside `tests/`, so the 100% coverage gate and the fake credentials of `tests/conftest.py` do not apply, and a plain `uv run pytest` never collects them.

## Run locally

Use credentials of the test organization only: the scenarios create, change and delete objects.

```bash
set -a; . ./.env; set +a          # YANDEX_ID_OAUTH_TOKEN, YANDEX_ID_ORGANIZATION_ID
export YCLI_E2E=1                  # without it every live test is skipped
uv run pytest e2e --no-cov -m "live and smoke"   # the pull-request subset
uv run pytest e2e --no-cov -m live               # everything (the nightly run)
uv run pytest e2e --no-cov -m live -k wiki       # one scenario
```

`--no-cov` is required: the repository's pytest options enforce coverage of `ycli`, which runs in a subprocess here. `YCLI_E2E_QUEUE` overrides the Tracker sandbox queue (default `YCLIPAGE`).

## Scenario files

`scenarios/<service>/<name>.yaml`, validated by `models.py` (unknown keys fail):

| Key | Meaning |
|---|---|
| `name`, `smoke` | test id; `smoke: true` also runs on pull requests |
| `steps[].run` | arguments after `ycli -o json`; `${RUN}`, `${QUEUE}` and saved names are substituted |
| `steps[].output` | `json` (default) or `text` for commands that print raw text, such as `wiki pages get` |
| `steps[].expect` | JMESPath expression → expected value; `unique(array)` is added for duplicate checks |
| `steps[].save` | name → JMESPath expression; later steps use `${name}` |
| `steps[].cleanup` | command run when the scenario ends, newest first, even after a failure |
| `steps[].disarms` | earlier step ids whose cleanup this step already did |

Every object a run creates is named after `${RUN}` = `e2e-<unix seconds>-<4 hex>`. Tracker issues cannot be deleted through the API, so issue scenarios end with the issue closed in the sandbox queue.

`tests/test_e2e_scenarios.py` checks offline, on every pull request, that each file parses and each `run`/`cleanup` is a valid ycli command line.

## Janitor

A failed cleanup or a cancelled job can leave objects behind. The janitor closes open Tracker issues in the sandbox queue and deletes Wiki pages and Forms surveys whose name carries a run stamp older than the cutoff, at most `--max` per call, and prints each object it touches:

```bash
uv run python -m e2e.janitor --older-than 6h --max 200 --dry-run   # list only
uv run python -m e2e.janitor --older-than 6h --max 200
```

Objects starting with `e2e-` but without a run stamp are reported and left alone.

## CI

`.github/workflows/e2e.yml`: the smoke subset on pull requests from branches of this repository (forks get no secrets), every scenario nightly and on manual dispatch (optional `-k` input). Runs are serialized by the `yandex-e2e` concurrency group and read their credentials from the `yandex-e2e` environment. The OAuth token is not refreshed in CI: when the preflight `ycli auth status` fails, reissue the token and update the secret.
