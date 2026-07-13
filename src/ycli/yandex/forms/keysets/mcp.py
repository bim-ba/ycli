"""Forms /surveys/{id}/keysets FastMCP tools (reads + writes, honest hints).

List/get/create/modify/delete are all exposed; ``download`` (the actual keys) is a binary
payload and stays CLI/SDK-only.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    forms_client,
)
from ycli.yandex.forms.keysets.models import Keyset, KeysetCreate, KeysetList, KeysetUpdate
from ycli.yandex.models import Ack

mcp = FastMCP("forms-keysets")


@mcp.tool(name="keysets_list", annotations={**RO, "title": "List Forms key sets"}, tags=TAGS)
def list_(
    survey_id: Annotated[
        str, Field(description="Form id (24-char hex), e.g. 6818ceffe010db4f59d11329.")
    ],
    client: FormsClient = Depends(forms_client),
) -> KeysetList:
    """Every personal-link key set on a form, as a flat array.

    A key set is a batch of single-use keys that become personal form-filling links; each item's
    integer ``id`` is what you pass to ``keysets_get``. Use ``surveys_list`` to find the
    ``survey_id`` first. Downloading the actual keys is a binary payload — CLI/SDK-only.

    Example:
        >>> keysets_list(survey_id="6818ceffe010db4f59d11329")  # doctest: +SKIP
    """
    return client.keysets.list(survey_id)


@mcp.tool(name="keysets_get", annotations={**RO, "title": "Get Forms key set"}, tags=TAGS)
def get(
    survey_id: Annotated[str, Field(description="Form id (24-char hex) the key set belongs to.")],
    keyset_id: Annotated[int, Field(description="Key set id (integer) from ``keysets_list``.")],
    client: FormsClient = Depends(forms_client),
) -> Keyset:
    """One key set's settings and usage (``total`` keys, ``used`` count, ``is_enabled``).

    Look up ``keyset_id`` via ``keysets_list``. To download the actual keys use the
    ``forms keysets download`` CLI command (binary payload — not exposed over MCP).

    Example:
        >>> keysets_get(survey_id="6818ceffe010db4f59d11329", keyset_id=7)  # doctest: +SKIP
    """
    return client.keysets.get(survey_id, keyset_id)


@mcp.tool(
    name="keysets_create", annotations={**WRITE, "title": "Create Forms key set"}, tags=WRITE_TAGS
)
def create(
    survey_id: Annotated[str, Field(description="Form id (24-char hex) to add the key set to.")],
    body: Annotated[
        KeysetCreate,
        Field(description="Key set settings; the API requires ``is_enabled`` on create."),
    ],
    client: FormsClient = Depends(forms_client),
) -> Keyset:
    """Create a batch of single-use personal-link keys on a form; returns the created ``Keyset``.

    The API rejects a body without ``is_enabled``, so set it explicitly alongside ``name`` and
    ``total``. Download the generated keys via the ``forms keysets download`` CLI command
    (binary payload — not exposed over MCP).
    """
    return client.keysets.create(survey_id, body.model_dump(exclude_none=True))


@mcp.tool(
    name="keysets_modify",
    annotations={**WRITE_IDEMPOTENT, "title": "Modify Forms key set"},
    tags=WRITE_TAGS,
)
def modify(
    survey_id: Annotated[str, Field(description="Form id (24-char hex) the key set belongs to.")],
    keyset_id: Annotated[int, Field(description="Key set id (integer) from ``keysets_list``.")],
    body: Annotated[
        KeysetUpdate,
        Field(description="Full key set record — name, total and is_enabled are all required."),
    ],
    client: FormsClient = Depends(forms_client),
) -> Keyset:
    """Replace a key set's settings; returns the updated ``Keyset``.

    Despite the PATCH verb, the API validates the body as a full record: ``name``, ``total``
    and ``is_enabled`` must all be set or the request is rejected with ``400``.
    """
    return client.keysets.modify(survey_id, keyset_id, body.model_dump(exclude_none=True))


@mcp.tool(
    name="keysets_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Forms key set"},
    tags=WRITE_TAGS,
)
def delete(
    survey_id: Annotated[str, Field(description="Form id (24-char hex) the key set belongs to.")],
    keyset_id: Annotated[int, Field(description="Key set id (integer) to delete.")],
    client: FormsClient = Depends(forms_client),
) -> Ack:
    """Delete a key set — its unused keys (personal fill links) stop working.

    The API answers ``200 OK`` with no body, so a typed acknowledgement is returned.
    """
    client.keysets.delete(survey_id, keyset_id)
    return Ack.deleted("keyset", keyset_id, from_=f"survey {survey_id}")
