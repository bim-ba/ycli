---
description: "Use the Yandex Tracker, Wiki and Forms CLI in shell scripts: JSON output, jq filters, dry runs, exit codes, shell completion."
type: how-to
---

# Script the CLI

## Get JSON

At a terminal ycli prints tables; piped, it prints JSON. Force a format with the global `--format` / `-o` (`auto`, `json`, `yaml`, `pretty`), before or after the command:

```bash
ycli tracker issues get TRACKER-1 | jq .        # JSON, because the output is piped
ycli -o yaml wiki pages get onboarding
ycli wiki pages get onboarding -o json
```

The keys are the API's own field names (`createdAt` in Tracker, `created_at` in Wiki), so the filters in Yandex's documentation work as they are.

## Filter the output

ycli has no filter of its own: pipe the JSON to [jq](https://jqlang.org).

```bash
ycli tracker issues get TRACKER-1 -o json | jq -r .summary
ycli tracker issues search 'Queue: TEST' -o json | jq -r '.[].key'
```

`-o json` makes the format explicit; without it a pipe gets JSON anyway.

## Delete without a prompt

A command that destroys data asks for confirmation at a terminal. In a script there is no one to ask, so it fails with exit code 2 until you pass `--yes` / `-y`:

```bash
ycli tracker boards delete 7 --yes
```

## Preview a write

`--dry-run` sends no write and prints the request instead (method, URL, body, never the token), through the same `-o`, and exits 0. A secret in the body, such as the password of a DataLens connection, is printed as `***`, so the output is safe in a CI log. Give such a value from a file outside the repository, mode 600: in `--body-file`, or as one field with `-F password=@secret.txt`. Typed on a command line it stays in the shell history. Write the file of one field with no line break at its end (`printf %s 'secret' > secret.txt`), or the break goes out with the secret. Reads still run, so a command that reads and then writes shows only its first write.

```bash
ycli tracker boards delete 7 --dry-run
```

## Branch on the exit code

Each kind of failure has its own exit code, listed in the [configuration reference](../reference/configuration.md#exit-codes).

```bash
ycli tracker issues get TRACKER-1 > issue.json
case $? in
  0) echo found ;;
  3) echo "no such issue" ;;
  6) echo "try again later" ;;
esac
```

## Complete commands with Tab

ycli has several hundred commands; let the shell complete them. Install ycli as a tool first (`uv tool install yandex-cli`), so the command stays on your `PATH`, then:

```bash
ycli --install-completion    # for the shell you are in: bash, zsh, fish or PowerShell
```

Restart the terminal. Completion is installed for the name you ran: run it again as `yandex-cli --install-completion` if you use the long name. `ycli --show-completion` prints the script instead of installing it.

To use ycli in a pipeline, see [Use in CI](use-in-ci.md).
