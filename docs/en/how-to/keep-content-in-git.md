---
description: "Keep Yandex Wiki pages and Tracker triggers as files in git: ycli sync pull, diff and push, with a review of the plan in a pull request."
type: how-to
---

# Keep content in git

`ycli sync` keeps objects of Yandex 360 as files of a git repository: you pull them, edit them like any text, review the change in a pull request and push it back. Two kinds of object are kept today, and `ycli sync kinds` lists them:

| Kind | A file | Its path |
|---|---|---|
| `wiki/page` | Markdown under a short header | `wiki/team/onboarding.md` for the page `team/onboarding` |
| `tracker/trigger` | YAML | `tracker/queues/DE/triggers/16.yaml` for trigger 16 of the queue `DE` |

Run every command from the root of the repository. Credentials are the usual ones (see [Authenticate](authenticate.md)).

There are no MCP tools for this: `sync` works in your working tree, which an MCP server does not have. An agent runs the same commands.

## Pull

```console
$ ycli sync pull wiki/team
3 written, 0 unchanged, 1 skipped
$ ycli sync pull tracker/queues/DE
```

`pull wiki/team` writes the page `team` as `wiki/team.md` and every page under it into `wiki/team/`. An object the kind does not keep, such as a grid among the pages, is listed as skipped. A file looks like this:

```markdown
---
ycli: wiki/page
hash: 3954dedc1b058bc73e60e88d4436078e9689cc2e811ffb88e1e6cd48563c3a8d
id: 4821
revision: 9
title: Team
---
# Team
```

The first four keys are the link of the file to its object, written by ycli: do not edit them. `hash` is the fingerprint of the content as it was read, and it is how every later command tells what changed.

`pull` writes over whatever is there. Commit your edits before you pull: git is what protects them. `ycli --dry-run sync pull wiki/team` writes nothing and names the files with uncommitted work it would overwrite.

## See what changed

```console
$ ycli sync status
$ ycli sync diff
```

`status` reads only the files, so it works offline and fits a pre-commit hook. `diff` reads the server and shows, for each file, the difference from the object as it is now to the file. Both say what `push` would do with a file:

| State | What it means |
|---|---|
| `unchanged` | nothing to push |
| `update` | you edited the file |
| `create` | the file names no object yet: `push` creates one |
| `untracked` | the file names an object and was never pulled from it: pull first |
| `changed-on-server` | somebody changed the object since you pulled (`diff` only) |
| `gone` | the object no longer exists (`diff` only) |
| `no-file` | the container holds an object with no file: `pull` writes it (`diff` on a directory) |
| `unsupported` | the API cannot do what the file asks |
| `unreadable` | the file is not a file of a known kind; the line and the reason are given |

Unchanged files are hidden; `--show-unchanged` lists them. `--kind wiki/page` limits a run to one kind, and a path limits it to a file or a directory.

Where the object changed on the server, `diff` shows your file against the server as it is now. A file keeps only the fingerprint of what was pulled, so `diff` cannot say which lines are yours and which are theirs: pull into a clean tree and let git show you.

## Push

```console
$ ycli --dry-run sync push
$ ycli sync push
0 created, 1 updated, 0 deleted, 14 unchanged, 0 stopped, 0 failed
$ git commit -am "Update the onboarding page"
```

`push` sends a file only when its object is still as you pulled it. After each write it reads the object again and writes the new link into the file, which is why a commit follows a push.

| Result | What happened |
|---|---|
| `created`, `updated`, `deleted` | done, and read back |
| `stopped` | the file and its object went apart (`changed-on-server`, `untracked`, `gone`): nothing was sent; pull, then push |
| `failed` | the API refused, or the service did not keep a value that was sent: the value is named |

A new file needs no link: write `ycli: wiki/page`, a `title` and the text, put the file where the page should live, and `push` creates the page and fills in the rest. A new trigger file is renamed to the id of its trigger.

`--on-error abort` ends the run at the first failed file; by default the run goes on to the next.

### Delete what you deleted

`push` never deletes on its own. To delete the objects whose files you removed, name the commit to compare with:

```console
$ ycli --dry-run sync push --prune main
$ ycli sync push --prune main
```

ycli takes the deleted files from git and asks before each delete; `--yes` answers for all. An object that never had a file is never deleted.

## Check files before a commit

`ycli sync validate` exits non-zero when a file does not read as a file of its kind or lies where files of its kind do not, and says the line. As a [pre-commit](https://pre-commit.com/) hook:

```yaml
repos:
  - repo: local
    hooks:
      - id: ycli-sync-validate
        name: ycli sync validate
        entry: ycli sync validate
        language: system
        pass_filenames: false
```

## Review the plan in a pull request

With `--exit-code`, `status` and `diff` exit with `7` when there is something to push and with `8` when a file and its object went apart; without the flag they exit with `0`. This job comments the plan on a pull request and fails when a pull is needed first:

```yaml
name: sync-plan
on: pull_request

jobs:
  plan:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    env:
      YANDEX_ID_OAUTH_TOKEN: ${{ secrets.YANDEX_ID_OAUTH_TOKEN }}
      YANDEX_ID_ORGANIZATION_ID: ${{ secrets.YANDEX_ID_ORGANIZATION_ID }}
      GH_TOKEN: ${{ github.token }}
    steps:
      - uses: actions/checkout@v5
      - uses: astral-sh/setup-uv@v10.2.0
      - name: Plan
        run: |
          uvx yandex-cli==0.132.0 sync diff --exit-code -o json > plan.json || code=$?
          jq -r '.[] | "### `\(.path)`: \(.state)\n\n```diff\n\(.diff // .detail // "")\n```\n"' plan.json > plan.md
          test -s plan.md || echo "Nothing to push." > plan.md
          gh pr comment "${{ github.event.pull_request.number }}" --body-file plan.md
          case "${code:-0}" in 0|7) ;; *) exit "$code" ;; esac
```

Secrets in a difference are masked. Push from the default branch after the merge, with the same two secrets and `ycli sync push`, then commit the links `push` wrote.

*Checked on 2026-10-08 against a real organization: pull, status, diff and push, with `--prune`, on Wiki pages; pull, diff and push of an edit on a trigger of a Tracker queue. Creating a trigger from a file, the pre-commit hook and the GitHub Actions job were not run.*
