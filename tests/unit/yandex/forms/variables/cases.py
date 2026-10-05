"""Contract cases for Forms ``/surveys/{id}/variables`` (see tests/contract/)."""

from tests.contract import Case, Reply, Sent

SID = "686d0a1b2c3d4e5f000000c0"
VARIABLES = [
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
        "renderers": [{"type": "txt", "name": "Текст"}],
    },
]

CASES = [
    Case(
        "forms.variables.list",
        args=(SID,),
        cli=["forms", "variables", "list", SID],
        mcp=("forms_variables_list", {"survey_id": SID}),
        exchanges=[(Sent("GET", f"surveys/{SID}/variables"), Reply(json=VARIABLES))],
    ),
]
