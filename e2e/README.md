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

A scenario runs when the environment holds what the profile of its service takes, and is skipped with the reason otherwise: Tracker, Wiki and Forms take the pair above; DataLens takes neither.

## DataLens: by hand only

DataLens takes an IAM token of Yandex Cloud and a Cloud organization, and no OAuth token; ycli refuses two tokens at once, so its scenarios are a run of their own, without `.env`. There is no nightly run for it: CI has no token DataLens takes (the service account has no DataLens seat, and a person's token is not kept in the secrets).

```bash
unset YANDEX_ID_OAUTH_TOKEN YANDEX_ID_ORGANIZATION_ID
export YANDEX_CLOUD_IAM_TOKEN=$(yc iam create-token)      # once per shell; it lives 12 hours
export YANDEX_CLOUD_ORGANIZATION_ID=bpfbl73plaftcqukf7uu  # the owner's organization: put your own
export YCLI_E2E=1
uv run pytest e2e --no-cov -n 0 --service datalens            # the scenarios
uv run pytest e2e --no-cov -n 0 --service datalens --record   # and record the replies
```

The token is a person's: it reaches every organization that person is in, and only `YANDEX_CLOUD_ORGANIZATION_ID` picks the one the scenarios work in. They make a collection, nest two more and two workbooks in it, make an empty dataset in one of them (the entry that is renamed and locked), and delete all of it; entries that exist already are only read.

A second scenario, `datalens/workbook-transfer`, exports a workbook holding one empty dataset and makes a new workbook from the export.

A third, `datalens/embedding`, gives a workbook a key for embedding, embeds an entry with it, and deletes both. The private key the API returns is never written anywhere: a recording keeps `<privateKey>` in its place.

A fourth, `datalens/shared-entries-and-audit`, makes a dataset in a collection (a shared entry), adds a role on it to the caller and takes it back, and asks the audit what changed and what the caller may do.

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
| `steps[].needs` | variables only the owner of the organization can give (below); while one is not set the step is skipped, and the run lists what it skipped |
| `steps[].reads` | commands that only read, run right after the step and only by a recording run (below) |

Some steps need something a run must not make or pick for itself. Each is an environment variable, and a step that needs one that is not set is skipped:

| Variable (in a scenario) | What it names |
|---|---|
| `YCLI_E2E_GRANTEE` (`${GRANTEE}`) | the Yandex uid of someone else to grant access to; nobody is granted anything without it |
| `YCLI_E2E_QUEUE_2` (`${QUEUE_2}`) | a second sandbox queue: issues are moved into it, and it is deleted and restored |
| `YCLI_E2E_LOCAL_FIELD` (`${LOCAL_FIELD}`), `YCLI_E2E_TRIGGER` (`${TRIGGER}`) | a local field and a trigger kept in the sandbox queue for a run to edit; the API cannot delete either, so a run does not create its own |

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
| a boolean, `null`, a number below 100 000 under a key that is known and names no identifier | kept |
| any other number | 1 |
| a list | one item per distinct shape |

A fixture also counts the keys its model does not know (`unknown_keys`); the offline check fails when a model stops knowing a key it knew. Their names, and the reads that failed, go to the file `--record-report` names (outside the repository); the terminal shows numbers only.

While the `reads` of a step run, the command gets `--dry-run` and the network seam refuses, before sending, any request whose endpoint does not declare the effect `read`. `--record-to DIR` writes somewhere else than the committed fixtures. `--record-pause SECONDS` (1 by default) is the wait before each command: a command in this process follows the one before faster than Tracker settles after a write, and on a day when Tracker answers slowly a longer pause (2.5) is what makes the run pass. Record a whole service, not one scenario: the fullest reply is picked among the replies of one run, so a run of one scenario overwrites a fixture another scenario filled better.

Before a write is tried on something that already exists, read the whole state it can touch, not only the part you mean to change, and keep it: an undo is checked against that. A revoke is not always the inverse of its grant (in Tracker, taking a user out of a queue's `read` took it out of `write` too).

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

`.github/workflows/e2e.yml`: the smoke subset on pull requests from branches of this repository (forks get no secrets), every scenario nightly and on manual dispatch (optional `-k` input). A nightly or manual run is one job per service (`pytest e2e --service wiki`), side by side: no scenario reaches into another service, and within a service the scenarios run one after another. A `prepare` job goes first, once: it checks the token and removes what earlier runs left behind; each service job then removes only what it named itself. Runs are serialized by the `yandex-e2e` concurrency group and read their credentials from the `yandex-e2e` environment. The OAuth token is not refreshed in CI: when the preflight `ycli auth status` fails, reissue the token and update the secret.
