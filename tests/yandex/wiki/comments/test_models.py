"""Wiki Comment author flattens to a bare scalar — populated and None branches."""

from ycli.yandex.wiki.comments.models import Comment


def test_author_flattens_to_scalar():
    assert Comment.model_validate({"author": {"display": "Сава"}}).author == "Сава"
    assert Comment.model_validate({"content": "ok"}).author is None
