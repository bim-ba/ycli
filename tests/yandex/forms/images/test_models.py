"""TDD for Forms images model (Image)."""

from ycli.yandex.forms.images.models import Image, ImageClone


def test_image_parses_all_fields():
    img = Image.model_validate(
        {"id": 7, "links": {"orig": "u"}, "name": "logo.png", "check_status": "ready"}
    )
    assert img.id == 7 and img.name == "logo.png" and img.check_status == "ready"


def test_image_links_default_empty():
    assert Image.model_validate({"id": 1}).links == {}


def test_clone_answer_carries_the_scan_mode():
    # As POST /surveys/{id}/images/clone answered on the test organization (2026-10-02).
    clone = Image.model_validate(
        {
            "id": 9053282,
            "links": {"360x": "https://avatars.mds.yandex.net/get-forms/6197807/7056bcf1/360x"},
            "name": "copy.png",
            "check_status": "ready",
            "check_mode": "strict",
        }
    )
    assert clone.check_mode == "strict" and clone.check_status == "ready"


def test_clone_body_drops_what_is_not_set():
    assert ImageClone(id=7).model_dump(exclude_none=True) == {"id": 7}
    body = ImageClone(links={"orig": "https://img.test/a.png"}, name="b.png")
    assert body.model_dump(exclude_none=True) == {
        "links": {"orig": "https://img.test/a.png"},
        "name": "b.png",
    }
