# Resource conventions

These rules fill the gap between the structural invariants in
[`ARCHITECTURE.md`](../../ARCHITECTURE.md) (ARCH-1..10) and the per-file conventions
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

## 3. MCP `RO` / `TAGS` / `<domain>_client` come from the domain `_deps`

Every `mcp.py` imports `RO`, `TAGS`, and the domain client provider from the domain's
`_deps` module — not from the shared `ycli.yandex._mcp`:

```python
# src/ycli/yandex/tracker/issues/mcp.py
from ycli.yandex.tracker._deps import RO, TAGS, tracker_client
```

The `_deps` module re-exports `RO` (from `ycli.yandex._mcp`) in its `__all__`, so
import-linter and IDEs resolve the canonical source correctly.  The scaffold
(`scripts/new_endpoint.py`) generates this single-line import automatically.

---

## 4. MCP tool-metadata standard

Every MCP tool MUST satisfy the following metadata contract.  fastmcp auto-derives
`description` from the docstring and `outputSchema` from the return type annotation —
**never set either by hand**.

### Required fields

| Field | Where it lives | Requirement |
|---|---|---|
| `name` | `@mcp.tool(name=…)` | `snake_case`, pattern `<resource>_<verb>`, verb in `READ_VERBS` |
| description | function docstring (first line) | One sentence; the LLM's primary selector — **required** |
| output schema | return type annotation | A concrete type (`ModelClass`, `list[X]`, `dict[str, Any]`) — **required** |
| `annotations` | `@mcp.tool(annotations={**RO, "title": "…"})` | Must include all RO hints + an imperative title |
| `tags` | `@mcp.tool(tags=TAGS)` | Always the domain `TAGS` constant |

### Prohibited

- `description=` kwarg in `@mcp.tool(…)` — set the docstring instead
- `output_schema=` kwarg in `@mcp.tool(…)` — set the return annotation instead
- `meta`, `icons`, `version`, top-level `title=` — omit by default

### Example

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

### Enforcement

`tests/test_architecture.py::test_every_mcp_tool_has_description_and_output_schema`
asserts that every registered tool has a non-empty `description` and a non-`None`
`outputSchema`.  The test uses `fastmcp.Client` to list tools from the mounted root
server and checks the `tool.description` and `tool.outputSchema` attributes (MCP spec
field `outputSchema`, exposed as camelCase by fastmcp 3.4.x).

---

## 5. Where these rules are enforced

| Rule | Enforced by |
|---|---|
| `APIModel` base | code review only — no automated check (ARCH-1 verifies the files exist, not what they subclass) |
| `XList` / `XResponse` naming | code review only — model class names are not snapshotted (snapshots track command/tool names) |
| `_deps` import path | `scripts/new_endpoint.py` scaffold + code review |
| Read-only MCP | `tests/test_architecture.py` ARCH-3 |
| Serialization confinement | `tests/test_architecture.py` ARCH-4 |
| MCP tool description + output schema | `tests/test_architecture.py::test_every_mcp_tool_has_description_and_output_schema` |
