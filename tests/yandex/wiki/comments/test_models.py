"""Property accessor on the wiki Comment model — populated and None branches."""
from ycli.yandex.wiki.comments.models import Comment


def test_author_display_populated_and_none():
    assert Comment.model_validate({"author": {"display": "Сава"}}).author_display == "Сава"
    assert Comment.model_validate({"content": "ok"}).author_display is None
