# Resource conventions

These rules fill the gap between the structural invariants in
[`ARCHITECTURE.md`](../../ARCHITECTURE.md) (ARCH-1..11) and the per-file conventions
documented in [`skills-and-commands.md`](skills-and-commands.md).  They apply to every
`yandex/<domain>/<resource>/` package, including the singleton `me` resources.

---

## 1. Every model inherits `APIModel`

All pydantic models — including sub-models and singleton `me` models — inherit from
`ycli.yandex.models.APIModel`:

```python
from ycli.yandex.models import APIModel

class MyModel(APIModel):
    ...
```

`APIModel` sets `extra="ignore"` (unknown API fields are silently dropped) and
`populate_by_name=True` (a field may be set by its Python name *or* its serialization
alias).  Never use bare `pydantic.BaseModel` inside `ycli.yandex`.

---

## 2. List-model naming: `XList` is flat, `XResponse` is the envelope

| Convention | Class signature | Used as |
|---|---|---|
| Flat list | `class XList(RootModel[list[X]]): root: list[X] = []` | Public return type of `client.list()` and MCP `list_` tool |
| Envelope | `class XResponse(APIModel): links: ...; result: list[X]` | Internal parse type of `client._list_page()` |

```python
# models.py
class SurveyList(RootModel[list[Survey]]):          # flat — public
    root: list[Survey] = []

class SurveysResponse(APIModel):                    # envelope — internal
    links: dict[str, Any] = Field(default_factory=dict)
    result: list[Survey] = Field(default_factory=list)
```

The envelope type (`XResponse`) is an implementation detail of the client and must not
appear in the public `client.list()` signature or in MCP tool return types.

---

## 3. MCP annotation sets / tags / `<domain>_client` come from the domain `dependencies`

Every `mcp.py` imports the annotation sets (`RO`, `WRITE`, `WRITE_IDEMPOTENT`,
`DESTRUCTIVE`), the tag constants (`TAGS`, `WRITE_TAGS`), and the domain client provider
from the domain's `dependencies` module — not from the shared `ycli.yandex.mcp`:

```python
# src/ycli/yandex/tracker/issues/mcp.py
from ycli.yandex.tracker.dependencies import DESTRUCTIVE, RO, TAGS, WRITE, WRITE_TAGS, tracker_client
```

The `dependencies` module re-exports the annotation sets (from `ycli.yandex.mcp`) in its
`__all__` and defines the domain tags (`TAGS = {"<domain>"}`,
`WRITE_TAGS = TAGS | {WRITE_TAG}`), so import-linter and IDEs resolve the canonical source
correctly.  The scaffold (`scripts/new_endpoint.py`) generates this single-line import
automatically.

### Why `<domain>_client` is a cached provider

fastmcp's `mount()` does not propagate lifespan context across server boundaries, so a
mounted domain server cannot receive a shared client through startup state.  Each `dependencies`
module therefore builds its provider with `make_cached_client` (in `ycli.yandex.mcp`), which
wraps a `functools.cache`d zero-arg factory:

```python
# src/ycli/yandex/tracker/dependencies.py
tracker_client = make_cached_client(TrackerClient)
```

The provider reads credentials from the env once and returns the same client for every tool
in the domain; `app_config()` is the matching `@cache`d config provider.  MCP tools consume
them via `Depends(tracker_client)`.  This is the only approved sharing pattern — fastmcp's
deprecated `import_server` must not be used.

---

## 4. MCP tool-metadata standard

Every MCP tool MUST satisfy the following metadata contract.  fastmcp auto-derives
`description` from the docstring and `outputSchema` from the return type annotation —
**never set either by hand**.

### Required fields

| Field | Where it lives | Requirement |
|---|---|---|
| `name` | `@mcp.tool(name=…)` | `snake_case`, pattern `<resource>_<verb>`; the verb (longest `_`-suffix) **must classify** in the fail-closed READ / WRITE / WRITE_IDEMPOTENT / DESTRUCTIVE maps in `tests/test_architecture.py` — an unknown verb fails the build and is added deliberately |
| description | function docstring (first line) | One sentence; the LLM's primary selector — **required** |
| output schema | return type annotation | A concrete type (`ModelClass`, `list[X]`, `dict[str, Any]`) — **required**; bodyless writes return `Ack` (see below) |
| `annotations` | `@mcp.tool(annotations={**<SET>, "title": "…"})` | `<SET>` matches the verb class exactly: `RO` for reads, `WRITE` for additive creates, `WRITE_IDEMPOTENT` for PATCH-style edits, `DESTRUCTIVE` for delete/clear/abort — plus an imperative title. Explicit because the MCP-spec default for an unannotated tool is `destructiveHint=true` |
| `tags` | `@mcp.tool(tags=…)` | `TAGS` for reads, `WRITE_TAGS` for writes — the `write` tag is what `ycli mcp start --read-only` disables wholesale |

### Prohibited

- `description=` kwarg in `@mcp.tool(…)` — set the docstring instead
- `output_schema=` kwarg in `@mcp.tool(…)` — set the return annotation instead
- `meta`, `icons`, `version`, top-level `title=` — omit by default

### Read example

```python
@mcp.tool(
    name="issues_get",
    annotations={**RO, "title": "Get Tracker issue"},
    tags=TAGS,
)
def get(key: str, client: TrackerClient = Depends(tracker_client)) -> Issue:
    """A single Tracker issue by key."""          # ← this IS the description
    return client.issues.get(key)                 # return type IS the outputSchema
```

### Write example

```python
@mcp.tool(
    name="comments_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker issue comment"},
    tags=WRITE_TAGS,
)
def delete(key: str, comment_id: str, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Permanently delete one comment from a Tracker issue (irreversible)."""
    client.comments.delete(key, comment_id)
    return Ack(detail=f"deleted comment {comment_id} on {key}")
```

### `Ack` for bodyless write responses

MCP tools must expose an output schema and CLI output goes through the Serializer — a bare
`None` return satisfies neither.  Writes whose API response carries no body (deletes,
clears, aborts) therefore surface a typed `ycli.yandex.models.Ack`
(`{ok: bool, detail: str}`): the MCP tool (and CLI command) constructs the `Ack` around the
bodyless client call, as in the example above.

### Binary payloads stay CLI/SDK-only

Raw-bytes **downloads** (attachments, exports, keyset files) never become MCP tools —
the matching *list* read does.  Upload endpoints may ship as MCP tools only in base64
form (pydantic `Base64Bytes` input — see `wiki_attachments_upload` and the
`wiki_uploadsessions_*` pipeline); raw file-path or multipart inputs stay on the CLI/SDK.

### Enforcement

`tests/test_architecture.py::test_every_mcp_tool_has_description_and_output_schema`
asserts that every registered tool has a non-empty `description` and a non-`None`
`outputSchema`.  The test uses `fastmcp.Client` to list tools from the mounted root
server and checks the `tool.description` and `tool.outputSchema` attributes (MCP spec
field `outputSchema`, exposed as camelCase by fastmcp 3.4.x).

---

## 5. Heterogeneous MCP output unions must be discriminated

fastmcp rebuilds `result.data` from the tool's output JSON schema and, for an undiscriminated
`anyOf`, picks the *first* branch that validates — silently reshaping one member into another
and dropping fields.  Any union a tool returns must carry a `Literal` discriminator tag via
`Field(discriminator=…)`:

```python
class TrackerAuthStatus(_ServiceAuthStatus):
    service: Literal["tracker"] = "tracker"
    me: TrackerMe | None = None
# … WikiAuthStatus, FormsAuthStatus …
ServiceAuthStatus = Annotated[
    TrackerAuthStatus | WikiAuthStatus | FormsAuthStatus, Field(discriminator="service")
]
```

The CLI/SDK path carries the native model instance and is unaffected; only the MCP
`result.data` reconstruction depends on the schema being self-describing.

---

## 6. Where these rules are enforced

| Rule | Enforced by |
|---|---|
| `APIModel` base | code review only — no automated check (ARCH-1 verifies the files exist, not what they subclass) |
| `XList` / `XResponse` naming | code review only — model class names are not snapshotted (snapshots track command/tool names) |
| `dependencies` import path | `scripts/new_endpoint.py` scaffold + code review |
| MCP annotation honesty (fail-closed verb classification, exact hints, `write` tag) | `tests/test_architecture.py` ARCH-3 (`test_arch3_mcp_annotation_honesty`) |
| Serialization confinement | `tests/test_architecture.py` ARCH-4 |
| Discriminated MCP output unions | code review + regression test (`status_get` me round-trip) |
| MCP tool description + output schema | `tests/test_architecture.py::test_every_mcp_tool_has_description_and_output_schema` |
