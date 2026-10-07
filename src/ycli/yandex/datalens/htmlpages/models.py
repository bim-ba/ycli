"""DataLens HTML page models: the public names of the generated classes this resource uses."""

from typing import Literal

from ycli.yandex.datalens.models import Language as PreviewLanguage
from ycli.yandex.datalens.schemas.html_pages import (
    CreateHtmlPageArgsAnnotation as HTMLPageAnnotation,
)
from ycli.yandex.datalens.schemas.html_pages import CreateHtmlPageResult as HTMLPageCreated
from ycli.yandex.datalens.schemas.html_pages import GetHtmlPagePreviewUrlResult as HTMLPagePreview
from ycli.yandex.datalens.schemas.html_pages import GetHtmlPageResult as HTMLPage
from ycli.yandex.datalens.schemas.html_pages import UpdateHtmlPageArgs as HTMLPageUpdate
from ycli.yandex.datalens.schemas.html_pages import UpdateHtmlPageArgsVariant1 as HTMLPageContent
from ycli.yandex.datalens.schemas.html_pages import UpdateHtmlPageArgsVariant2 as HTMLPageRevision
from ycli.yandex.datalens.schemas.html_pages import UpdateHtmlPageResult as HTMLPageSaved

#: The theme of a preview.
PreviewTheme = Literal["light", "dark", "light-hc", "dark-hc", "system"] | str

__all__ = [
    "HTMLPage",
    "HTMLPageAnnotation",
    "HTMLPageContent",
    "HTMLPageCreated",
    "HTMLPagePreview",
    "HTMLPageRevision",
    "HTMLPageSaved",
    "HTMLPageUpdate",
    "PreviewLanguage",
    "PreviewTheme",
]
