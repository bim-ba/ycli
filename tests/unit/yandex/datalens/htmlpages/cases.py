"""Contract cases for DataLens HTML pages (see tests/contract/)."""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.htmlpages.models import HTMLPageAnnotation, HTMLPageUpdate

HP = "hp000000000001"
WB = "wb000000000001"
HTML = "<p>Hello</p>"
NOTE = {"description": "A greeting"}
# A page as `getHtmlPage` answers it: flat, with no HTML of the page in it (measured,
# 2026-10-06).
PAGE = {
    "entryId": HP,
    "scope": "artifact",
    "type": "html-page",
    "key": "Pages/Hello",
    "workbookId": WB,
    "collectionId": None,
    "revId": "rev1",
    "savedId": "rev1",
    "publishedId": "rev1",
    "annotation": None,
    "version": 1,
}
ENTRY = {key: value for key, value in PAGE.items() if key != "type"}
NEW = {"entryId": HP, "content": "<p>Bye</p>", "mode": "save"}
REVISION = {"entryId": HP, "revId": "rev1", "mode": "publish"}
PREVIEW = {"url": f"https://preview.example/{HP}?sig=1"}

CASES = [
    Case(
        "datalens.htmlpages.get",
        args=(HP,),
        kwargs={"branch": "published"},
        cli=["datalens", "htmlpages", "get", HP, "--branch", "published"],
        mcp=("datalens_htmlpages_get", {"entry_id": HP, "branch": "published"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getHtmlPage", json={"entryId": HP, "branch": "published"}),
                Reply(json=PAGE),
            )
        ],
    ),
    Case(
        "datalens.htmlpages.get",
        args=(HP,),
        kwargs={
            "rev_id": "rev1",
            "include_permissions": True,
            "include_favorite": False,
        },
        cli=[
            *("datalens", "htmlpages", "get", HP, "--rev-id", "rev1"),
            *("--include-permissions", "--no-include-favorite"),
        ],
        mcp=(
            "datalens_htmlpages_get",
            {
                "entry_id": HP,
                "rev_id": "rev1",
                "include_permissions": True,
                "include_favorite": False,
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getHtmlPage",
                    json={
                        "entryId": HP,
                        "revId": "rev1",
                        "includePermissions": True,
                        "includeFavorite": False,
                    },
                ),
                Reply(json={**PAGE, "isFavorite": False}),
            )
        ],
    ),
    Case(
        "datalens.htmlpages.create",
        kwargs={"content": HTML, "workbook_id": WB, "name": "Hello"},
        cli=[
            *("datalens", "htmlpages", "create", "--content", HTML),
            *("--workbook-id", WB, "--name", "Hello"),
        ],
        mcp=("datalens_htmlpages_create", {"content": HTML, "workbook_id": WB, "name": "Hello"}),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createHtmlPage",
                    json={"content": HTML, "workbookId": WB, "name": "Hello"},
                ),
                Reply(json={"entry": ENTRY, "warnings": []}),
            )
        ],
    ),
    Case(
        "datalens.htmlpages.create",
        kwargs={
            "content": HTML,
            "annotation": HTMLPageAnnotation.model_validate(NOTE),
            "key": "Pages/Hello",
        },
        cli=[
            *("datalens", "htmlpages", "create", "--content", HTML),
            *("--annotation", json.dumps(NOTE), "--key", "Pages/Hello"),
        ],
        mcp=(
            "datalens_htmlpages_create",
            {"content": HTML, "annotation": NOTE, "key": "Pages/Hello"},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createHtmlPage",
                    json={"content": HTML, "annotation": NOTE, "key": "Pages/Hello"},
                ),
                Reply(json={"entry": ENTRY, "warnings": []}),
            )
        ],
    ),
    Case(
        "datalens.htmlpages.update",
        args=(HTMLPageUpdate.model_validate(NEW),),
        cli=[
            *("datalens", "htmlpages", "update", HP, "--mode", "save"),
            *("--content", NEW["content"]),
        ],
        mcp=("datalens_htmlpages_update", {"body": NEW}),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent("POST", "rpc/updateHtmlPage", json=NEW),
                Reply(json={"entry": {**ENTRY, "revId": "rev2", "savedId": "rev2"}}),
            )
        ],
    ),
    Case(
        "datalens.htmlpages.update",
        args=(HTMLPageUpdate.model_validate({**NEW, "annotation": NOTE}),),
        cli=[
            *("datalens", "htmlpages", "update", HP, "--mode", "save"),
            *("--content", NEW["content"], "--annotation", json.dumps(NOTE)),
        ],
        mcp=("datalens_htmlpages_update", {"body": {**NEW, "annotation": NOTE}}),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent("POST", "rpc/updateHtmlPage", json={**NEW, "annotation": NOTE}),
                Reply(json={"entry": {**ENTRY, "revId": "rev2", "savedId": "rev2"}}),
            )
        ],
    ),
    Case(
        "datalens.htmlpages.update",
        args=(HTMLPageUpdate.model_validate(REVISION),),
        cli=["datalens", "htmlpages", "update", HP, "--mode", "publish", "--rev-id", "rev1"],
        mcp=("datalens_htmlpages_update", {"body": REVISION}),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (Sent("POST", "rpc/updateHtmlPage", json=REVISION), Reply(json={"entry": ENTRY}))
        ],
    ),
    Case(
        "datalens.htmlpages.delete",
        args=(HP,),
        cli=["datalens", "htmlpages", "delete", HP],
        mcp=("datalens_htmlpages_delete", {"entry_id": HP}),
        effect=Effect.DESTRUCTIVE,
        exchanges=[(Sent("POST", "rpc/deleteHtmlPage", json={"entryId": HP}), Reply(json={}))],
    ),
    Case(
        "datalens.htmlpages.preview_url_get",
        args=(HP,),
        kwargs={"branch": "saved"},
        cli=["datalens", "htmlpages", "preview-url-get", HP, "--branch", "saved"],
        mcp=("datalens_htmlpages_preview_url_get", {"entry_id": HP, "branch": "saved"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getHtmlPagePreviewUrl", json={"entryId": HP, "branch": "saved"}),
                Reply(json=PREVIEW),
            )
        ],
    ),
    Case(
        "datalens.htmlpages.preview_url_get",
        args=(HP,),
        kwargs={"rev_id": "rev1", "lang": "ru", "theme": "dark"},
        cli=[
            *("datalens", "htmlpages", "preview-url-get", HP),
            *("--rev-id", "rev1", "--lang", "ru", "--theme", "dark"),
        ],
        mcp=(
            "datalens_htmlpages_preview_url_get",
            {"entry_id": HP, "rev_id": "rev1", "lang": "ru", "theme": "dark"},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getHtmlPagePreviewUrl",
                    json={
                        "entryId": HP,
                        "revId": "rev1",
                        "lang": "ru",
                        "theme": "dark",
                    },
                ),
                Reply(json=PREVIEW),
            )
        ],
    ),
]
