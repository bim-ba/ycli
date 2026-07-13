"""TDD for Forms files models (FileOut / FileList / FileIn)."""

from ycli.yandex.forms.files.models import FileIn, FileList, FileOut


def test_file_out_parses_all_fields():
    out = FileOut.model_validate(
        {"name": "cv.pdf", "path": "p", "size": 12, "url": "u", "check_status": "ready"}
    )
    assert out.name == "cv.pdf" and out.size == 12 and out.check_status == "ready"


def test_file_list_is_flat_root():
    fl = FileList.model_validate([{"name": "a"}, {"name": "b"}])
    assert [f.name for f in fl.root] == ["a", "b"]


def test_file_in_drops_unset_on_dump():
    assert FileIn(path="p").model_dump(exclude_none=True) == {"path": "p"}
