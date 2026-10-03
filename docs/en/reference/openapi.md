---
description: "OpenAPI 3.1 documents for Yandex Tracker, Wiki and Forms, describing each API as ycli wraps it."
type: reference
---

# OpenAPI documents

One OpenAPI 3.1 document per service, describing the API **as ycli wraps it**:

| Service | Document |
|---|---|
| Tracker | <https://bim-ba.github.io/ycli/openapi/tracker.yaml> |
| Wiki | <https://bim-ba.github.io/ycli/openapi/wiki.yaml> |
| Forms | <https://bim-ba.github.io/ycli/openapi/forms.yaml> |

They are generated from ycli's own code and are not published by Yandex. Yandex publishes a
specification for Wiki and Forms and none for Tracker; these three share one format.

## What a document holds

| Part | Where it comes from |
|---|---|
| paths, methods, query parameters | the requests ycli's contract tests make the SDK send |
| path parameter names | the arguments of the SDK operation that sends the request |
| response schemas | the pydantic models ycli parses the replies into |
| request body schemas | the body model of the operation's MCP tool, where it has one |

## Extensions

| Key | Meaning |
|---|---|
| `x-ycli-operations` | the SDK operations that send the request, as `resource.method` |
| `x-ycli-effect` | `read`, `write`, `idempotent_write` or `destructive` |
| `x-ycli-pagination` | how the listing pages, for a paginated operation |
| `x-ycli-body` | `typed`: the schema is the MCP tool's body model; `untyped`: the SDK takes a free-form mapping, so no schema is given |

## Limits

- A document is only as complete as ycli. README's
  [Against the published API](https://github.com/bim-ba/ycli#against-the-published-api) lists
  the query parameters ycli cannot send and the response fields its models drop.
- A parameter's type is the type of the SDK argument it carries, or of the value ycli sends;
  one ycli cannot tie to either has none. An `enum` lists the values ycli accepts, which may
  be fewer than the API does.
- Responses describe what ycli reads. Its models ignore unknown fields, so a schema never
  forbids extra properties.
- Component schema names are ycli's class names, prefixed with the resource where two
  resources share one (`CommentsComment`, `EntitiesComment`). They change when a model is
  renamed.
