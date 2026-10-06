# Resource conventions

These rules fill the gap between the structural invariants in
[`ARCHITECTURE.md`](../../ARCHITECTURE.md) (ARCH-1..9) and the per-file conventions
documented in [`skills-and-commands.md`](skills-and-commands.md).  They apply to every
`yandex/<domain>/<resource>/` package, including the singleton `me` resources.

---

## 1. Every model inherits `APIModel`

All pydantic models — including sub-models and singleton `me` models — inherit from
`ycli.yandex.models.APIModel`:

```python
from ycli.yandex.models import APIModel


class MyModel(APIModel): ...
```

`APIModel` sets `extra="allow"` (a reply keeps a field the model does not declare, so what
Yandex adds shows up in the output at once, untyped), `validate_by_name=True` (a field may be
set by its Python name *or* its alias) and `serialize_by_alias=True` (every dump, CLI and MCP
alike, keeps the API's field names). A model that only request bodies are built from inherits
`RequestBody` (`extra="forbid"`): a key it does not declare is an error where the body is
built, not something sent to the API. Never use bare `pydantic.BaseModel` inside
`ycli.yandex`; a bare mapping with no fields of its own is a `RootModel[dict[...]]`.

Two lists hold what is open on purpose, each entry with its reason: `OPEN_BODIES` in
`scripts/api_drift.py` (an issue takes custom fields; the drift comparison skips only these
bodies) and `BODY_AND_REPLY` in `tests/architecture/test_conventions.py` (a model that both builds a body
and reads a reply stays open, so a key it does not declare, nested in a body, reaches the API;
its declared fields are still compared with the published ones).

### One class per shape

A shape that two or more resources of a service read (a reference with `self`, `id` and
`display`; a localized name) is one class in the service's `models.py`
(`ycli.yandex.tracker.models.Reference`), not a class per resource. Models of one kind that
differ by a few fields share a base class and add their own (`KeyedReference(Reference)`
adds `key`); models of different kinds that only happen to match stay separate. A model
used by one resource stays in that resource. `tests/architecture/test_model_shapes.py` fails when two models of a
service have the same schema, unless the group is listed in `SAME_SHAPE` with its reason.

A public model that is renamed or merged stops importing under its old name in the same
release: no alias is kept. The commit that does it carries a `BREAKING CHANGE` footer listing
"was → is", which becomes the changelog entry.

### Generated models

DataLens publishes one OpenAPI document with about 600 schemas, and its objects are too large to
write by hand, so `scripts/gen_datalens_models.py` generates them into
`src/ycli/yandex/datalens/schemas/`, one module per section of the API. The rules of this page
are met by the script, not by an editor: before the generator runs it rewrites the document so
that a reply is read openly, a union of objects in a reply that nothing tells apart is one object (where every field its members share is of one type), every other union of kinds has one spare open member and no discriminator (#391, #444: a kind the document does not list, or a known kind with a field of another type, is read and is sent as `OtherKind`, an empty open class that keeps every key as it came; only a request's union whose members nothing tells apart is left as it is, having no kind to be unknown), no object requires a field but the one that tells its kind (DataLens leaves out fields its document calls required, and most objects are read and sent back; only the top level of a request keeps what it requires, the arguments of its operation), a set of values is open, only the envelope of a request is closed
(and takes `RequestBody`), no field has a default of the document's (what is not given is `None`
and is not sent), a `number` is read as an integer or a fraction, whichever it is (`300000` is not sent as `300000.0`), no field has a limit on its value (its length, range or pattern is the API's to enforce), and every class is named from the place of its schema, so a schema added
elsewhere renames nothing.

A field the document both requires and lets be `null` is `Annotated[..., NoDropNull()]`
(`ycli.yandex.models`) and goes out as `null` when it has no value: a dashboard is saved only
with `autoupdateInterval: null`. A field that is only optional is left out, DataLens refusing
`null` there.

A generated file is never edited by hand and carries no `# violation` marker; the checks of this
page skip the directory (`GENERATED` in `tests/architecture/scanners.py`), and
`tests/tooling/test_gen_datalens_models.py` holds what stands in for them:

- every file is the one the script wrote: its checksum is in `scripts/datalens_schemas.sha256`,
  which the script writes, and a file changed, added or removed without the script fails;
- every file is nothing but models: it imports only from `pydantic`, `typing`, `datetime` and
  `ycli.yandex.models`, its classes inherit only from `APIModel`, `RequestBody`, `RootModel`
  and each other, and it runs no code. The document is downloaded, and its extensions that
  would tell the generator to import or inherit something else are removed before it is read;
- every module imports.

The specification itself is not committed; the weekly `api-drift` run regenerates from the
published one and reports a difference.

A resource does not hand a generated class to its callers under the generator's name: its
`models.py` imports the classes it uses and gives them their public names, and those names
follow this page.

### A field with a set of values

A set of values is the known values plus any string, and the definition itself says so:

```python
SortDirection = Literal["asc", "desc"] | str
```

It is the same on the way in and on the way out, in every service: a CLI option, an MCP tool
parameter, a request-body field, a reply field. ycli does not refuse a value outside the set:
it goes to the API, which answers for it, and in a reply it does not fail the parse. An IDE
suggests the known values, and a tool's schema shows them (`anyOf` of the `enum` and a string).

- **CLI.** Typer has no "one of these or any string" type, so the option is a string built by
  `ycli.cli.typedefs.values_option(SortDirection, "--order", help="Sort direction.")`, which
  takes the values for the help text and the completion from the definition. Do not list the
  values by hand: `test_an_option_takes_the_values_it_names_from_the_definition_of_the_set`; an
  option that must is marked `# violation(value-set): <reason>` above the parameter.
- **One definition per set**, used by name: a set of one resource in its `models.py`, of
  several in the service's `models.py`, of several services in `ycli.yandex.models`
  (`SortDirection`, `GroupSource`). `test_a_closed_value_set_is_defined_once` fails on a second
  `Literal` or `StrEnum` with the same values.
- **Strict on purpose** (not sets of Yandex values): a discriminator field, by which pydantic
  picks the class (`type` of a question or a subscription); `forms questions --type`, the five
  types the flags can build.
- **A set of ycli's own is a `StrEnum`.** The rule in one line: a closed set that ycli owns is a
  `StrEnum`, a set of values of the API is `Literal[...] | str`. ycli's own sets are the ones
  only a release of ycli changes: `OutputFormat`, `Transport`, `Kind`, `LogLevel`, `LogFormat`,
  `CredentialKind`, `Effect`; the HTTP method is the standard library's `http.HTTPMethod`. A member equals its
  string, so a setting, an option and a reply field carry the same text as before.

### A field the API ignores

A request field or parameter that the API accepts and does nothing with stays in ycli. Its
description begins with `IGNORED_BY_API` (`ycli.yandex.models`), so the CLI help, the MCP
input schema and the reference say so; its body model inherits `WarnsOnIgnored`, so setting
it logs a warning (a reply carrying the same name is read silently). The comparison with the
published API (`scripts/api_drift.py`) takes its reason from the same mark, so nothing else
lists the field; `tests/tooling/test_api_drift.py` fails on a mark that explains no difference. A
query parameter has no model to carry the mark: it is listed in `EXPLAINED` with the `IGNORED`
reason.

---

## 2. Lists: `ItemList[X]` is flat, `XResponse` is the envelope

| What | Type | Used as |
|---|---|---|
| Flat list | `ItemList[X]` from `ycli.yandex.models` | Public return type of `client.list()` and of the MCP `list` tool |
| Envelope | `class XResponse(APIModel): links: ...; result: list[X]` | The page the endpoint parses, read by the pager |

```python
# client.py
def list(self, *, limit: int | None = None) -> ItemList[Survey]: ...


# models.py
class SurveysResponse(APIModel):  # envelope — internal
    links: dict[str, Any] = Field(default_factory=dict)
    result: list[Survey] = Field(default_factory=list)
```

A resource does not define a list class of its own. An envelope that holds only the items and
their paging (`XResponse`, or `CursorPage[X]` for a Wiki cursor listing) is read by the pager and
flattened. An envelope that carries data of its own is the public type: Forms conditions return
`ConditionsResponse` because its `operator` joins the groups.

---

## 3. MCP annotation sets / `<domain>_client` come from the domain `dependencies`

Every `mcp.py` imports the annotation sets (`RO`, `WRITE`, `WRITE_IDEMPOTENT`,
`DESTRUCTIVE`) and the domain client provider from the domain's `dependencies` module — not
from the shared `ycli.yandex.mcp`:

```python
# src/ycli/yandex/tracker/issues/mcp.py
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    tracker_client,
)
```

The `dependencies` module re-exports the annotation sets (from `ycli.yandex.mcp`) in its
`__all__`, so import-linter and IDEs resolve the canonical source correctly. It also defines
the domain tags (`TAGS`, `WRITE_TAGS`) for the prompts and resources of the service, which
have no annotations to derive them from.  The scaffold (`scripts/new_endpoint.py`) generates this single-line import, and
an import-linter contract forbids a resource `mcp.py` from importing `ycli.yandex.mcp`.

### Why `<domain>_client` is a per-request provider

fastmcp's `mount()` does not propagate lifespan context across server boundaries, so a
mounted domain server cannot receive a shared client through startup state.  Each `dependencies`
module therefore builds its provider with `client_provider` (in `ycli.yandex.mcp`):

```python
# src/ycli/yandex/tracker/dependencies.py
tracker_client = client_provider(TrackerClient)
```

The provider resolves credentials (`caller_credentials`: the environment over stdio, the signed-in
caller's Yandex token over HTTP) and builds the client
on every tool call, so a rotated token applies without a restart and nothing is cached per
process; `app_config()` is the matching per-call config provider.  MCP tools consume them via
`Depends(tracker_client)`.

---

## 4. MCP tool-metadata standard

Every MCP tool MUST satisfy the following metadata contract.  fastmcp auto-derives
`description` from the docstring and `outputSchema` from the return type annotation —
**never set either by hand**.

### Required fields

| Field | Where it lives | Requirement |
|---|---|---|
| `name` | `@mcp.tool(name=…)` | the operation's name with its resource in front (`boards_update`), see [Naming an operation](#7-naming-an-operation). Prefixed with the service it is the CLI path of the same operation (`tracker_boards_update` = `ycli tracker boards update`) |
| description | function docstring (first line) | One sentence; the LLM's primary selector — **required** |
| output schema | return type annotation | A concrete type (`ModelClass`, `list[X]`, `dict[str, Any]`) — **required**; bodyless writes return `Ack` (see below) |
| parameters | `Annotated[T, Field(description=…)]` | **Every** input property carries a non-empty description (`tests/unit/mcp/test_mcp_metadata.py`). Reuse the shared aliases in `<domain>/dependencies.py` (`IssueKey`, `QueueID`, `Version`, `SurveyID`, `Slug`, …) instead of repeating a description per tool; a request `body` model describes itself through its fields |
| `annotations` | `@mcp.tool(annotations={**<SET>, "title": "…"})` | `<SET>` matches the verb class exactly: `RO` for reads, `WRITE` for additive creates, `WRITE_IDEMPOTENT` for PATCH-style edits, `DESTRUCTIVE` for delete/clear/abort — plus an imperative title. Explicit because the MCP-spec default for an unannotated tool is `destructiveHint=true` |
| `tags` | never passed | The root server derives them (`ycli.mcp.listing.DerivedTags`): the service from the tool's name, `write` when `readOnlyHint` is not true — the tag `ycli mcp start --read-only` disables wholesale. A tool that passes `tags=` fails `test_arch3_no_tool_states_its_tags_itself` |

### Prohibited

- `description=` kwarg in `@mcp.tool(…)` — set the docstring instead
- `output_schema=` kwarg in `@mcp.tool(…)` — set the return annotation instead
- `meta`, `icons`, `version`, top-level `title=` — omit by default
- examples in a tool docstring: it is the tool's description, so it carries none
  (`test_no_tool_docstring_carries_an_example`); the SDK method it calls has the example. A request
  model's examples reach the input schema, and the listing strips them (`ycli.mcp.listing`)

### Read example

```python
@mcp.tool(
    name="issues_get",
    annotations={**RO, "title": "Get Tracker issue"},
)
def get(key: IssueKey, client: TrackerClient = Depends(tracker_client)) -> Issue:
    """A single Tracker issue by key."""  # ← this IS the description
    return client.issues.get(key)  # return type IS the outputSchema
```

### Write example

```python
@mcp.tool(
    name="comments_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker issue comment"},
)
def delete(key: str, comment_id: str, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Permanently delete one comment from a Tracker issue (irreversible)."""
    client.comments.delete(key, comment_id)
    return Ack(detail=f"deleted comment {comment_id} on {key}")
```

### Typed request body — never `dict`

A request body is the resource's pydantic request model in every layer: the MCP tool takes
it as its `body` parameter, the CLI command builds it from its options, the client method and
the endpoint builder take it as it is, and `Endpoint` dumps it once (`Endpoint.body`: API field
names, unset fields left out). The dump is pydantic's own: `APIModel` carries one wrap
serializer that, for a request body (`model_dump(context=WIRE)`), leaves out an optional field
that is `None`, keeps a required field that is `None`, and keeps a key the model does not
declare as it was given. The serializer has no return annotation on purpose: with one, pydantic
replaces the model's schema with that type and every MCP output schema loses its fields
(`tests/snapshots/mcp_output_schemas.txt` would change). A model may carry pydantic
serializers of its own. Nothing in between dumps it, so the three surfaces
send the same JSON. In an MCP tool the model is the input schema: an agent sees the field
names, types and aliases instead of an opaque `object`, and a malformed payload fails before
the HTTP call:

```python
@mcp.tool(
    name="issues_update_bulk",
    annotations={**WRITE, "title": "Bulk-update issues"},
)
def update_bulk(body: BulkUpdate, client: TrackerClient = Depends(tracker_client)) -> BulkChange:
    """Start an async bulk field update over many Tracker issues; returns the operation."""
    return client.issues.update_bulk(body)
```

A `None` is an absence and is not sent, except where the caller could only have meant it: in a
field with no default, and in a field the model does not declare (an open body: Tracker clears
a field given as `null`). A command that merges `--field` values into its body dumps the named
options, merges, and validates the result into the model.

The only exception is a binary upload, which takes `Base64Bytes` (see below); another would carry
`# violation(arch-8): <reason>` above the function, and there is none.

### A body over the schema budget

A client reads every tool's input schema before its first call, and some cut a large one short (Codex compacts a schema over 5,000 bytes; #372). So a tool's input schema weighs at most `SCHEMA_BUDGET_BYTES` (32 KB, `ycli.yandex.mcp`), measured as `len(json.dumps(schema))` of what the server lists. A body that would take its tool over the budget is marked:

```python
SUBSCRIPTION = "ycli.yandex.forms.subscriptions.models:Subscription"

body: Annotated[Subscription, OverBudget(SUBSCRIPTION, "The integration; ``type`` selects its schema.")]
```

The listing then shows the parameter as a free-form object whose description names the definition to read, and the `schema_get(service, name)` tool serves that definition and each one it refers to, one per call. The value is still validated by the model: the tool receives a typed body, and a call with a wrong field is refused with the field's path. The address is `module:name` of the model or of the named union; `schema_get` keeps no map of its own and reads the addresses from the listing. Within a service a name means one definition: two bodies may share one, and two different definitions under one name stop the index (`test_one_name_is_one_definition_within_a_service`). The SDK and the CLI do not change. `test_every_tool_lists_a_schema_within_the_budget` names the tool and the parameter to mark; a mark that is no longer needed is not checked for.

### An RPC operation: the fields of its request are its arguments

Where an API has no addresses and every operation is `POST /rpc/<name>` with all its fields in one object (DataLens), the method takes the top-level fields of that object as its arguments, under one name in the SDK, the CLI and MCP (#371): `datalens.collections.update(collection_id, title=…)`, `--title`, `title`. There is no `body` parameter. A nested value stays a generated model (`deltas: list[AccessBindingDelta]`). The request layer builds the generated request from the arguments, so the body is typed all the way down. `test_an_rpc_method_takes_the_fields_of_its_request_as_arguments` holds the arguments equal to the fields; the pager's own fields are not arguments.

A parent that is not given is the root (#379): `parent_id: str | None = None` on every surface, for reads and for writes alike. The API requires the field and takes `null` for the root, and ycli sends that `null`.

### `Ack` for bodyless write responses

MCP tools must expose an output schema and a CLI command's return value is what gets printed —
a bare `None` return satisfies neither.  Writes whose API response carries no body (deletes,
clears, aborts) therefore surface a typed `ycli.yandex.models.Ack`
(`{ok: bool, detail: str}`): the MCP tool (and CLI command) constructs the `Ack` around the
bodyless client call, as in the example above.

### Binary payloads stay CLI/SDK-only

Raw-bytes **downloads** (attachments, exports, keyset files) never become MCP tools —
the matching *list* read does.  Upload endpoints may ship as MCP tools only in base64
form (pydantic `Base64Bytes` input — see `wiki_attachments_upload` and the
`wiki_uploadsessions_*` pipeline); raw file-path or multipart inputs stay on the CLI/SDK.

### Enforcement

`tests/architecture/test_arch8.py::test_arch8_mcp_write_tool_bodies_are_typed` AST-walks every
`mcp.py`, `client.py` and `endpoints.py` and fails the build on a bare `dict`/`dict[...]`
`body` parameter; `test_arch8_a_request_body_is_dumped_only_by_the_endpoint` fails on a
`.model_dump(` in any of the three. Both are fail-closed, with no exception today.

`tests/architecture/test_tool_metadata.py::test_every_mcp_tool_has_description_and_output_schema`
asserts that every registered tool has a non-empty `description` and a non-`None`
`outputSchema`.  The test uses `fastmcp.Client` to list tools from the mounted root
server and checks the `tool.description` and `tool.output_schema` attributes (MCP spec
field `outputSchema`; the MCP SDK v2 types under fastmcp 4 spell it in snake_case).

---

## 5. Heterogeneous MCP output unions must be discriminated

fastmcp rebuilds `result.data` from the tool's output JSON schema and, for an undiscriminated
`anyOf`, picks the *first* branch that validates — silently reshaping one member into another
and dropping fields.  Any union a tool returns must carry a `Literal` discriminator tag via
`Field(discriminator=…)`, the way the Forms question union (`forms/questions/models.py`) does:

```python
class StringQuestion(_QuestionBase):
    type: Literal["string"] = Field(default="string", description="Discriminator: string.")
# … BooleanQuestion, IntegerQuestion, … one member per question type …
QuestionCreate = Annotated[
    StringQuestion | BooleanQuestion | IntegerQuestion | ..., Field(discriminator="type")
]
```

The CLI/SDK path carries the native model instance and is unaffected; only the MCP
`result.data` reconstruction depends on the schema being self-describing.

A union whose members are all classes of the generated layer is outside this rule
(`_generated_classes` in `tests/architecture/test_conventions.py`): it is read softly, with a
spare open member in place of the discriminator ("Generated models", #391). Its members
still require their tag, so a value fits one of them at most, and `structuredContent` is
what DataLens sent; one hand-written member puts the union back under the rule.

---

## 6. Writing a client and its CLI commands

`/new-endpoint` (`scripts/new_endpoint.py`) generates a new resource on the httpx2 core;
`tracker/issues/` and the Forms resources are worked examples.

A module carries `from __future__ import annotations` only where it needs it: a type imported
under `if TYPE_CHECKING:` or a class named before it is defined (most `client.py`). Elsewhere
the line does nothing and is left out; from Python 3.14 it is needed nowhere.

**`endpoints.py`** — sans-IO declarations: one function per operation Yandex publishes, returning
an `Endpoint` (or a `Paged` listing with its core `Pagination`) and named like the client method
that sends it (`boards.update` sends `endpoints.update`; a builtin's name takes an underscore,
`list_`; a method that sends several names each after itself, `search` and `search_scroll`); every caller-supplied path part goes through
`segment()`; `effect=` only where the method misleads, with `# violation(arch-3): <reason>` above it.

**`client.py`** — HTTP only (ARCH-2):

- Subclass `ycli.yandex.core.resource.Resource`; each public method sends one declaration
  (`self._session.send(…)`, or `self._session.iterate(…, limit=…)` for a listing, returning the
  flat `ItemList[X]` of §2). A bodyless write returns `None` and the surfaces build the `Ack`; a binary
  download declares `response_type=bytes` and returns `bytes`.
- Every public method's docstring names its `METHOD /path`, has Google-style `Args:`,
  `Returns:` and `Raises:` sections that match the signature (ruff `D`, `pydoclint`), and an
  example that runs: `>>> tracker.boards.get(31).name` with the arguments of the operation's first
  contract case, whose reply answers it (the repository-root `conftest.py` puts the `tracker`,
  `wiki` and `forms` clients into every doctest). `+SKIP` only where an example needs a real file
  or the network.

**`models.py`** — inherit `APIModel` (§1); every field
carries `Field(description=…)`, which becomes the MCP schema text. Request bodies are typed
models (`XCreate` / `XUpdate`), discriminated where the API is polymorphic.

**What ycli checks.** Only what it needs to build the request: the names and types of a
body's fields, a required field, the syntax of its own options (JSON, `key=value`), the file
an option names, and limits of its own (`--limit`). Everything else is the API's to check: a
value's length or range, a value outside a known set, which arguments go together, a rule of
the service. ycli sends it as given and shows the API's answer; it does not fill in a value
the caller left out to make a request pass. ARCH-9 keeps a list of the refusals that remain,
each with its reason. A missing field of a request model is printed by one formatter
(`ycli.cli.errors.format_cli_error`, exit code 2: nothing was sent), so a command needs no
check of its own to say it. A reply that does not fit its model is another error,
`YandexUnexpectedReplyError`: the request went out, and the exit code is 1.

**`cli.py`**:

- `app = typer.Typer(name=…, help=…, no_args_is_help=True)`;
  `--help` works without credentials because a client is built only when a command runs.
- A command declares the clients it needs as keyword-only parameters
  (`*, tracker: TrackerClient`, or `config: AppConfig`); `ycli.cli.inject` fills them and hides
  them from Typer. It **returns** its result, annotated with the real type, and never prints
  (ARCH-4): a model renders through `--format`, a count returns `int`, raw text returns `str`, a
  binary download returns `BinaryResult(data, output)` behind `--output`.
- Every argument and option is `Annotated[…, typer.Argument(help=…)]` /
  `Annotated[…, typer.Option(help=…)]`. A write builds the typed request model from the options.
- A local file is a `Path` with `exists=True, dir_okay=False, readable=True`, so a missing file
  is a usage error, not a traceback; a JSON body file goes through `Model.model_validate_json`
  (`tests/unit/cli/test_cli_files.py` lists every such command).
- An option that is not given is `None` (`Annotated[str | None, typer.Option(…)] = None`), never
  `""` or `0`: an explicit empty string or zero is a value and is sent, so `--description ""`
  clears a field. A test asks `is not None`, not truthiness. An MCP tool parameter follows the
  same rule (`Annotated[str | None, Field(…)] = None`; `limit` is `int | None` with `ge=1`).
  `tests/unit/test_not_given.py` fails on a `""` or `0` default in a `cli.py` or an `mcp.py`.
- ycli sends what the caller gave and nothing of its own (#296). A boolean is three-valued on
  every surface: `Annotated[bool | None, typer.Option("--notify/--no-notify", …)] = None` in the
  CLI, `bool | None = None` in a tool and in the SDK; `True` and `False` are both sent, `None` is
  left out. No option, parameter or body field carries a default of ycli's own: where the API
  declares a default it applies by itself, and where the API requires a value the option is
  required. No `x or None` on a value the caller gave: an empty string or a `False` is a value.
  A place that departs from this on purpose is marked `# violation(as-given): <reason>`.
- A secret in a request body (a password, a token: sent, never read back) is a `SecretStr`,
  and a map of secrets is `dict[str, SecretStr]`. A caller gives the plain string and reads it
  back with `.get_secret_value()`. pydantic masks it wherever the model is printed (`repr`, a
  dump, a command's output, a tool's reply); it goes out as its own value in one place, the
  dump of a request body (`APIModel._as_sent` under `WIRE`). A value that fails validation is
  raw, so no model quotes its input in the text of an error (`hide_input_in_errors` on
  `APIModel` and on every generated `RootModel`); the error still names the field. `--dry-run`
  prints `***` under every key that the request's model types as a secret (`secret_keys`), at
  any depth and whoever gave it (a flag, `-F`, `--body-file`): `PlannedRequest.of` (#388). That
  mask goes by the key's name within one request, so a field of the same name elsewhere in the
  body is masked too. A generated model types as secrets what its specification marks
  `writeOnly`, with the names the generator adds and removes, each with its reason
  (`_SECRET_MAPS`, `_NOT_SECRETS`). The help of a command that takes a secret says to give it
  in `--body-file`. The type holds for a body that fits its kind: one that falls to the spare
  class (`OtherKind`, a connection of a kind the document lacks) keeps its secret as plain
  text in `repr` and in a dump; a dry run and the text of an error mask it all the same (#444).
- A secret in a reply is the result of the operation and is printed as it came: the private
  key that `datalens embeddingsecrets create` returns once is a plain string in the CLI, the
  MCP tool and the SDK alike (#448). `SecretStr` is for a secret in a request. The command,
  the tool and the method say that the value is given once, and the tool says that it enters
  the agent's context.
- A trait of a field or a parameter is a typed object in its `Annotated` metadata
  (`NoDropNull()`, `OverBudget(…)`), not a string key, a list of names or an edit of text.
- Every command that sends a JSON object takes `-F key=value` and `--body-file file` (JSON or YAML) for a
  field that has no flag of its own (#354). They are declared once, beside `--yes` and
  `--dry-run`, and a command writes no code for them: the CLI lays them under the body the
  command built, at the first request it sends, object by object. The later the stronger:
  file, then `-F`, then the command's flags. `-F 'fields[priority]=high'` names a nested field.
  `-F key=@file` (`@-` for stdin) gives the file's text as it is, always a string (#412); a
  string that starts with `@` goes in JSON quotes (`-F 'text="@ivan"'`).
  Only objects merge: a list replaces the one below it, so a file's `{"tags": ["a"]}` and
  `-F 'tags[]=x'` send `["x"]`. A `-F` given before the subcommand and one after it add up. A
  command with a `-F` of its own (`ycli api`, the bulk changes) refuses the common one.
  Such a field does not pass the body model; the API answers for it. A command whose first
  request carries no JSON object refuses them before sending. A command whose body is a union
  that picks its class by a field (a question, a subscription, a condition group) cannot wait
  for the request: it takes `CallerFields` as a parameter, merges in the same order and
  validates the result. Where that model is closed (`forms questions`, the eight
  `forms conditions` writes) a field it does not know is refused; where it is open
  (`forms subscriptions`, `forms filling submit`) the field is sent. A command that sends no
  body at all (`auth status`, `doctor`, `mcp start`) refuses both options before it does anything.
- An async trigger (export, clone, bulk change) takes `--wait/--no-wait`, default `--wait`, and
  polls through `ycli.cli.progress.wait_for`; the matching `operations get` read ships on every
  surface so an agent can poll it too.

---

## 7. Naming an operation

An operation has one name on every surface. The SDK method is `tracker.issues.update_bulk`, the
MCP tool `tracker_issues_update_bulk`, the CLI command `ycli tracker issues update-bulk` (hyphens
between the words of a command), and the function in `endpoints.py` is `update_bulk`. One
operation Yandex publishes gets one name: no method stands for several addresses.

The name is `[parts_]verb[_qualifier]`.

| | Rule | Example |
|---|---|---|
| Verb | One standard word for what the operation does: `get` one object, `list` many, `search` or `suggest` where the API calls it that, `count`, `create`, `update` some fields, `set` a whole value, `delete`; for files `upload`, `download`, `attach`, `import`, `export`; `clear` for all at once. | `POST /issues/{id}/comments` creates a comment: `comments.create`, though the API's page says "add" |
| | A synonym is never a verb: `add`, `remove`, `edit`, `modify`, `patch`, `query`. | `rows_create`, not `rows_add` |
| | Any other verb is the API's own, where its address or the operation's name states an action that none of the standard words covers. | `surveys.publish`, `transitions.execute`, `recovery.recover` |
| Parts | The nouns of the address between the resource and the action, in the order of the address. The one the operation acts on is plural; a noun that only says whose it is may stay singular. | `queues.versions_create`, `operations.clone_get`, `conditions.question_list` |
| Qualifier | Every other word follows the verb: `bulk`, a way to pick the object, a word the API does not say. | `issues.update_bulk`, `pages.get_by_id`, `components.list_for_queue`, `worklog.list_global` |

A Python keyword or builtin cannot name a function: the method is `issues.import_`, and the
functions in `endpoints.py`, `cli.py` and `mcp.py` are `import_` and `list_`.

One tool has no command of its own name, because one command serves two tools
(`tracker_entities_comments_list_relative` beside `tracker entities comments list --relative`,
marked `# violation(arch-1)` above the tool), and two tools share one operation: `tracker_issues_list` and `tracker_issues_search` both call
`issues.search`. The first is the short way to the most common request and is marked
`# violation(naming)` above the tool (#432).

**Who holds this.** The tests hold what a machine reads without judgment: one name on every
surface, no synonym in a name, and a method named exactly `get` that does not return a list.
Everything else in this section is a convention held by review: `/arch-review` compares the names
of new operations with it. That includes "a `get` returns one object" for a name with parts:
`autoactions.logs_get` and `comments.thread_get` return the records of one run and of one thread,
and are marked in the code. A renamed operation stops answering to its old name in the same
release, and the changelog lists both.

### A parameter has one name too

The name is the SDK argument's. The MCP parameter is that name, the CLI option is it with
hyphens (`is_silent` is `--is-silent`), and a positional argument shows it in capitals
(`ENTITY_TYPE`). Where a command has no SDK argument behind an option, it takes the name the
tool gives the parameter (`--issue-type`).

### A deliberate departure

Code that departs from a rule on purpose says so where it does, in one line:

```python
# violation(naming): the log of one run is one object, its entries are the list
def logs_get(...) -> ItemList[AutoactionRunEntry]:
```

The form is `# violation(<rule>): <reason>`; the rule is one of this page (`naming`, `as-given`, `value-set`), `api-drift` (a body field that
differs from the published API for a reason of ycli's own, read by `scripts/api_drift.py`) or
an invariant (`arch-9`). The marker is a comment line of its own, right above the line where the
departure starts: the `raise`, the `Endpoint(...)`, the `def` of the method. A reviewer who meets
the code sees that the departure was chosen, and a search for `violation(` lists every one.
`tests/architecture/test_markers.py` holds the form; the check of an invariant that has a scanner
(`arch-9`) also holds that each of its markers stands above what it scans for, and the reverse.

## 8. Names in code

- **An acronym keeps its capitals inside a CapWords name** (PEP 8): `QueueID`, `HTTPSubscription`,
  `JSONRPCSubscription`, `SurveyAPIKey`, `ACL`; a plural adds a lower-case `s` (`UserIDs`). The
  list is `ACRONYMS` in `tests/architecture/test_conventions.py`. A name that has a spelling of its own keeps
  it and is recorded with its reason in `OWN_SPELLINGS` (`OAuth`). A snake_case name is all
  lower case as before (`queue_id`, `api_key`).
- **An `Annotated` alias is defined once.** The same text in two modules is one alias: it moves
  to the nearest shared module (`<domain>/typedefs.py` for CLI options and arguments,
  `<domain>/dependencies.py` for MCP parameters, `ycli/cli/typedefs.py` across domains) and is
  imported by name.
- **An alias name means one thing.** Two aliases that differ in help, type or requiredness are
  different things and carry different names: the shared one keeps the plain name (`ExpandOpt`,
  `PageID`), the one of a single resource says whose it is (`ProjectExpandOpt`, `FormPageID`).

---

## 9. Where these rules are enforced

| Rule | Enforced by |
|---|---|
| `APIModel` base | `tests/architecture/test_conventions.py::test_every_model_inherits_apimodel` (exceptions in `MODEL_BASE_EXCEPTIONS`) |
| No list class of a resource's own | `tests/architecture/test_conventions.py::test_no_resource_defines_a_list_class_of_its_own` |
| `dependencies` import path | import-linter contract `conventions: a resource mcp.py imports from its domain dependencies` (`uv run lint-imports`) |
| MCP annotation honesty (each tool's hints against the strongest effect it sends, `write` tag) | `tests/contract/test_contract.py`, `tests/architecture/test_arch3.py` |
| Serialization confinement | `tests/architecture/test_arch4.py` |
| Discriminated MCP output unions | `tests/architecture/test_conventions.py::test_every_union_a_tool_returns_is_discriminated` |
| MCP tool description + output schema | `tests/architecture/test_tool_metadata.py::test_every_mcp_tool_has_description_and_output_schema` |
| Acronyms keep their capitals in a CapWords name | `tests/architecture/test_conventions.py::test_an_acronym_keeps_its_capitals_in_a_name` |
| One name on every surface, no synonym, `get` returns one object | `tests/architecture/test_arch1.py`: `test_arch1_cli_path_equals_mcp_name`, `test_arch1_sdk_method_equals_tool_name`, `test_arch1_a_get_returns_one_object` |
| The verb, the parts and their order | review: `/arch-review` against [Naming an operation](#7-naming-an-operation) |
| An `Annotated` alias is defined once | `tests/architecture/test_conventions.py::test_an_annotated_alias_is_defined_once` |
| Every model field carries a description | `tests/architecture/test_conventions.py::test_every_model_field_has_a_description` |
| An alias name means one thing | `tests/architecture/test_conventions.py::test_an_alias_name_means_one_thing` |
| A three-valued boolean option is a `--x/--no-x` pair ([section 6](#6-writing-a-client-and-its-cli-commands)) | `tests/architecture/test_conventions.py::test_a_three_valued_boolean_option_is_declared_as_a_pair` |
