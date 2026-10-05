---
description: "Every ycli environment variable, setting and exit code."
type: reference
---

# Configuration

ycli reads its settings from the environment, or from a `.env` file in the working directory.
An invalid value fails at startup, naming the variable (exit code 2).

## Credentials

| Variable | Meaning |
|---|---|
| `YANDEX_ID_OAUTH_TOKEN` | a Yandex OAuth token with Tracker, Wiki and Forms access (fallback name `YCLI__AUTH__OAUTH_TOKEN`) |
| `YANDEX_CLOUD_IAM_TOKEN` | a ready IAM token, in place of the OAuth token; it lives up to 12 hours. Exactly one way to sign in is set: a second one is an error (exit code 2) |
| `YANDEX_CLOUD_SERVICE_ACCOUNT_KEY_FILE` | the path of a service account's authorized key (`yc iam key create --output key.json`), in place of a token; ycli exchanges it for IAM tokens and renews them. Needs the `service-account` extra |
| `YANDEX_CLOUD_SERVICE_ACCOUNT_KEY` | the same key as its JSON text, for a secret store that hands out values rather than files |
| `YANDEX_ID_ORGANIZATION_ID` | the Yandex 360 organization id, sent as `X-Org-Id` (fallback name `YCLI__AUTH__ORGANIZATION_ID`) |
| `YANDEX_CLOUD_ORGANIZATION_ID` | a Yandex Cloud organization id, sent as `X-Cloud-Org-Id`. One organization of either kind is required; with both set, Tracker, Wiki and Forms get the Yandex 360 one |
| `YCLI_PROFILE` | the name of a saved profile to take the token and the organization from, in place of the variables above; `--profile` wins over it (see [Authenticate](../how-to/authenticate.md#keep-several-organizations)) |
| `YANDEX_OAUTH_CLIENT_ID` | your OAuth app's id, for `ycli auth login` |
| `YANDEX_OAUTH_CLIENT_SECRET` | your OAuth app's secret: enables the device flow of `ycli auth login` |

An exported but empty variable counts as unset. See [Authenticate](../how-to/authenticate.md).

## Settings

Optional settings follow the `YCLI__<GROUP>__<SETTING>` pattern. An empty one counts as unset too.

| Variable | Default | Meaning |
|---|---|---|
| `YCLI__HTTP__TIMEOUT_SECONDS` | `30` | per-request timeout, seconds (> 0) |
| `YCLI__HTTP__RETRIES` | `3` | retries of an idempotent request after a 429 or a 5xx (≥ 0) |
| `YCLI__HTTP__MAX_ITEMS` | `500` | item cap of a listing without `--limit` or `--all` (> 0) |
| `YCLI__HTTP__MAX_PAGES` | `1000` | page cap of one listing: a listing that never ends stops here with a warning (> 0) |
| `YCLI__HTTP__MAX_RETRY_AFTER_SECONDS` | `60` | longest pause a 429 may ask for in `Retry-After`; a longer one fails at once (> 0) |
| `YCLI__HTTP__MAX_WAIT_SECONDS` | `1380` | how long `--wait` polls a long operation (an export, a clone, a bulk change) before it gives up; the operation itself keeps running (> 0) |
| `YCLI__LOGGING__LEVEL` | `WARNING` | `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`; `-v` means `INFO` (every HTTP request), `-vv` means `DEBUG` |
| `YCLI__LOGGING__FORMAT` | `text` | `text` or `json` (one object per line); logs always go to stderr |

The settings of the HTTP transport (`YCLI__MCP__*`) are in
[Self-host over HTTP](../how-to/self-host-over-http.md).

## Exit codes

A failed command exits with a code that says what kind of failure it was, so a script can branch
without parsing the message.

| Code | Meaning | When |
|---|---|---|
| 0 | ok | the command succeeded |
| 1 | failure | any other failure: a 4xx the API rejected, an unmapped error, a declined confirmation |
| 2 | usage | a bad command line or an invalid `YCLI__…` setting |
| 3 | not found | the API answered 404, or the token cannot see the object |
| 4 | auth | 401 or 403, or no credentials |
| 5 | rate limited | the API answered 429 and the retries ran out (the hint shows `Retry-After`) |
| 6 | transient | a 5xx, a timeout or a lost connection: worth retrying later |
