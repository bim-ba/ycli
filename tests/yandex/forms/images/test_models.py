"""TDD for Forms images model (Image)."""

from ycli.yandex.forms.images.models import Image


def test_image_parses_all_fields():
    img = Image.model_validate(
        {"id": 7, "links": {"orig": "u"}, "name": "logo.png", "check_status": "ready"}
    )
    assert img.id == 7 and img.name == "logo.png" and img.check_status == "ready"


def test_image_links_default_empty():
    assert Image.model_validate({"id": 1}).links == {}
