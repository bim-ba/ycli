---
description: "Run ycli in GitHub Actions or GitLab CI: comment on a Yandex Tracker issue after a deploy, with secrets and exit codes."
type: how-to
---

# Use in CI

Run ycli in a pipeline to comment on an issue after a deploy, move it along its workflow or read a page. A pipeline needs three things: ycli itself, the two credentials as secrets, and commands that never wait for a person.

## Credentials

Store `YANDEX_ID_OAUTH_TOKEN` and `YANDEX_ID_ORGANIZATION_ID` as secrets of the pipeline and expose them as environment variables of the job. The token is a person's OAuth token (see [Authenticate](authenticate.md)). The working path for a pipeline today is an account created for automation: add a user to the organization for it, give that user only what the pipeline does, and issue its OAuth token.

A Yandex Cloud service account cannot stand in for that user. Yandex does not allow one for [Wiki](https://yandex.ru/support/wiki/en/api-ref/access) and [Forms](https://yandex.ru/support/forms/en/api-ref/access) at all, and for [Tracker](https://yandex.ru/support/tracker/en/api/access) only in a Yandex Cloud organization after a request to Yandex support. A ready IAM token of a user works in place of the OAuth token (`YANDEX_CLOUD_IAM_TOKEN`, see [Authenticate](authenticate.md#use-an-iam-token)), but it lives up to 12 hours, so it suits a job that issues one at its start, not a stored secret.

## GitHub Actions

```yaml
name: notify-tracker
on:
  workflow_dispatch:

jobs:
  comment:
    runs-on: ubuntu-latest
    env:
      YANDEX_ID_OAUTH_TOKEN: ${{ secrets.YANDEX_ID_OAUTH_TOKEN }}
      YANDEX_ID_ORGANIZATION_ID: ${{ secrets.YANDEX_ID_ORGANIZATION_ID }}
    steps:
      - uses: astral-sh/setup-uv@v10.2.0
      - run: uvx yandex-cli==0.113.2 tracker comments create TRACKER-1 --text "Deployed ${GITHUB_SHA::7}"
```

`uvx yandex-cli==<version>` runs that version without installing anything else. Pin the version: a pipeline should not change behaviour when a new release comes out.

A ready-made GitHub Action is planned: follow [#210](https://github.com/bim-ba/ycli/issues/210).

## GitLab CI

The image's entrypoint is `ycli`, so clear it to get a shell for `script`:

```yaml
comment:
  image:
    name: ghcr.io/bim-ba/ycli:0.113.2
    entrypoint: [""]
  script:
    - ycli tracker comments create TRACKER-1 --text "Deployed $CI_COMMIT_SHORT_SHA"
```

Set the two variables in **Settings → CI/CD → Variables**, masked.

## Any other runner

With Docker, pass the variables by name so their values stay out of the command line:

```bash
docker run --rm -e YANDEX_ID_OAUTH_TOKEN -e YANDEX_ID_ORGANIZATION_ID \
  ghcr.io/bim-ba/ycli:0.113.2 tracker comments create TRACKER-1 --text "Deployed"
```

## Commands that do not wait

- **Deletes need `--yes`.** A command that destroys data asks for confirmation; with no terminal it exits with code 2 instead. Pass `--yes` when the pipeline is meant to delete.
- **Output is JSON.** Without a terminal ycli prints JSON, so `jq` reads it: `ycli tracker issues get TRACKER-1 | jq .key`.
- **Try it first.** `--dry-run` prints the request a write would send and sends nothing.

## Fail the job for the right reason

Each kind of failure has its own [exit code](../reference/configuration.md#exit-codes). A pipeline usually retries a transient failure and stops on the rest:

```bash
ycli tracker comments create TRACKER-1 --text "Deployed" || status=$?
case "${status:-0}" in
  0) ;;
  5|6) echo "Tracker is busy or down, retry later"; exit 75 ;;
  4) echo "The token is missing or rejected"; exit 1 ;;
  *) exit "$status" ;;
esac
```

*Checked on 2026-10-03: the Docker commands and the cleared entrypoint run against a real organization; the GitHub Actions and GitLab jobs were not run.*
