---
description: "Use the Yandex Tracker, Wiki and Forms CLI in shell scripts: JSON output, jq filters, dry runs, exit codes, shell completion."
type: how-to
---

# Script the CLI

## Get JSON

At a terminal ycli prints tables; piped, it prints JSON. Force a format with the global `--format` / `-o` (`auto`, `json`, `yaml`, `pretty`, `csv`, `markdown`, `ndjson`, `name`), before or after the command:

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
ycli tracker issues search 'Queue: TEST' -o json | jq -r '.items[].key'
```

`-o json` makes the format explicit; without it a pipe gets JSON anyway.

## Get a table or one item on a line

`-o csv` and `-o markdown` print a table, `-o ndjson` prints one item on a line:

```bash
ycli tracker issues search 'Queue: TEST' -o csv > issues.csv
ycli tracker queues list -o markdown >> report.md
ycli tracker issues search 'Queue: TEST' -o ndjson | jq -r .key
```

- The columns are the fields ycli knows for that kind of object, the same whatever the reply holds. A field the service added since has no column; `-o json` prints it.
- A nested object becomes columns named through a dot (`status.key`); a list stays one cell, as JSON text.
- A command that answers with one object prints a table of one row, or one line.
- `csv` is UTF-8 with no byte order mark, its lines end with a line feed alone, and a cell is the service's text as it came. A spreadsheet reads a cell that starts with `=` as a formula, so open a file of someone else's text with that in mind.
- Where a listing stopped is said on stderr, as with `-o pretty`: stdout holds the rows alone.

## Feed one command to another

`-o name` prints the identifier of each object on a line: what the command that reads it takes.

```bash
ycli tracker issues search 'Queue: TEST' -o name | xargs -n1 ycli tracker issues get
new=$(ycli tracker issues create --queue TEST --summary 'From a script' -o name)
```

- An object that lies inside another one prints its own identifier: `ycli tracker comments list TEST-1 -o name` prints comment ids, and the issue key is yours to add.
- A command whose result has no identifier (a grant of access, a count) is refused before it sends anything, with exit code 2.
- A reply that leaves the identifier of an item out is an error: nothing is printed, so a script never acts on fewer objects than were listed.
- With `--dry-run` the plan comes back in place of the object, and it is printed as JSON.
- DataLens commands do not print names yet.

## Take a long listing in pieces

A listing stops at 500 items unless told otherwise. `--limit N` takes the first N, `--all` takes everything, and `--next` goes on from where a run stopped. `-o json` and `-o yaml` print what the MCP tool and the SDK give: `{items, truncated, next, total}`, so a script takes the token with `jq -r .next`. A table (`-o pretty`) prints the rows, and where it stopped goes to stderr, ready to paste. The line says that the run stopped at its limit, not that more is left: only the next run can tell, and it may give nothing.

```console
$ ycli tracker issues search 'Queue: DE' --limit 100 > first.json
stopped at 100 of 752; go on with: ycli tracker issues search 'Queue: DE' --next eyJ2IjoxLCJvZiI6…  (or --all)
$ ycli tracker issues search 'Queue: DE' --limit 100 --next eyJ2IjoxLCJvZiI6… > second.json
```

A token carries its listing: with `--next`, give nothing but the limit and what the command cannot be called without, and that as it was: an argument that differs from the token's is refused by its name, never passed over. A token of a Tracker issue search by a scroll (`--scroll-type`) works once; any other token works again. A listing that can no longer go on exits with `9`: start it again without the token. A run that asks more pages than `YCLI__HTTP__MAX_PAGES` stops there and says so the same way, with a token to go on from. A small first `--limit` sets the size of the pages for every piece after it, so take the first piece as large as the ones you mean to go on with.

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
