---
description: "Find, create and change Yandex Tracker issues, comment, log time, create a Wiki page: each task as a CLI command, an MCP tool call and Python."
type: how-to
---

# Common tasks

The everyday operations, each shown three ways. Pick a tab once and every example on the site follows it.

- **CLI**: the command to type.
- **MCP**: the tool call an agent makes when you ask it in words.
- **SDK**: the call on a client, `tracker = TrackerClient(oauth_token="…", organization_id="…")` (and `wiki`, `forms` likewise).

Every example here is generated from the test that runs it on all three surfaces.

## Find issues

--8<-- "docs/examples/operations/tracker.issues.search.md"

The CLI and the tool take the common filters as options; for anything else pass a query in Tracker's own language: `ycli tracker issues search 'Queue: DE AND Status: open'`.

## Read an issue

--8<-- "docs/examples/operations/tracker.issues.get.md"

## Create an issue

--8<-- "docs/examples/operations/tracker.issues.create.md"

## Change an issue

--8<-- "docs/examples/operations/tracker.issues.update.md"

## Comment on an issue

--8<-- "docs/examples/operations/tracker.comments.create.md"

## Move an issue along its workflow

An issue moves by a transition, and each status offers its own. List them first:

--8<-- "docs/examples/operations/tracker.transitions.list.md"

Then run one by its id:

--8<-- "docs/examples/operations/tracker.transitions.execute.md"

## Log time

--8<-- "docs/examples/operations/tracker.worklog.create.md"

## Create a Wiki page

--8<-- "docs/examples/operations/wiki.pages.create.md"

## Read a form

--8<-- "docs/examples/operations/forms.surveys.get.md"

Every other operation is in the reference: [CLI](../reference/cli/index.md), [MCP tools](../reference/mcp/tracker.md), [SDK](../reference/sdk/tracker.md).
