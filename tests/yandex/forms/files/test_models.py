"""TDD for Forms files models (FileOut / ItemList[FileOut] / FileIn)."""

from ycli.yandex.forms.files.models import FileIn
from ycli.yandex.forms.models import FileOut


def test_file_out_parses_all_fields():
    out = FileOut.model_validate(
        {"name": "cv.pdf", "path": "p", "size": 12, "url": "u", "check_status": "ready"}
    )
    assert out.name == "cv.pdf" and out.size == 12 and out.check_status == "ready"


def test_file_in_drops_unset_on_dump():
    assert FileIn(path="p").model_dump(exclude_none=True) == {"path": "p"}
