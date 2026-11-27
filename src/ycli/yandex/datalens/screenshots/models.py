"""DataLens screenshot models: the public names of the generated classes this resource uses."""

from typing import Literal

from ycli.yandex.datalens.schemas.screenshots import GetScreenshotResult as Screenshot

#: The format of the picture; DataLens makes a PNG when none is asked.
ImageType = Literal["png", "jpeg", "jpg"] | str

__all__ = ["ImageType", "Screenshot"]
