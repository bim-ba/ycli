"""Forms variable catalogue models parse what the live API returns."""

from ycli.yandex.forms.variables.models import VariableInfo
from ycli.yandex.models import ItemList

# Two items as GET /surveys/{id}/variables answered on the test organization (2026-10-02).
LIVE = [
    {
        "type": "form.answer_url",
        "name": "Ссылка на ответ",
        "category": {"type": "form", "name": "Форма"},
    },
    {
        "type": "form.question_answer_choice_slug",
        "name": "Идентификатор варианта ответа на вопрос",
        "category": {"type": "form", "name": "Форма"},
        "filters": {"question": {"answer_type": "answer_choices"}},
        "arguments": ["question"],
    },
]


def test_variables_parse_live_answer():
    first, second = ItemList[VariableInfo].model_validate(LIVE).root
    assert first.category is not None and first.category.type == "form"
    assert second.filters == {"question": {"answer_type": "answer_choices"}}
    assert second.arguments == ["question"] and second.renderers is None
