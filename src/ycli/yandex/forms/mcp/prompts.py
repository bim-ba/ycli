"""Forms MCP prompts: ready requests over the Forms tools, offered by the client's UI.

A prompt's text names the tools to call; ``NEEDS_TOOLS`` lists them, so a server that does not
serve one of them does not offer the prompt.
"""

from ycli.yandex.forms.dependencies import TAGS
from ycli.yandex.mcp import NEEDS_TOOLS, new_server

mcp = new_server("forms-prompts")


@mcp.prompt(
    name="answers_table",
    title="Answers of a form as a table",
    tags=TAGS,
    meta={NEEDS_TOOLS: ["forms_answers_list", "forms_questions_list", "forms_surveys_get"]},
)
def answers_table(survey_id: str) -> str:
    """Show the answers of a form as a table, one row per answer, with a short summary.

    Args:
        survey_id: The form's id.

    Returns:
        The request for the model.
    """
    return (
        f"Show me the answers of the Yandex Forms survey {survey_id} as a table.\n\n"
        f"1. Call forms_surveys_get and forms_questions_list for {survey_id}: the form's name "
        "and its questions in order.\n"
        f"2. Call forms_answers_list for {survey_id}.\n"
        "3. Answer with the form's name and the number of answers, then a Markdown table: one "
        "row per answer, the submission time first, then one column per question, headed by "
        "the question's text.\n"
        "4. Under the table, for each choice question give the count per option, and for each "
        "free-text question two or three recurring themes.\n\n"
        "Show the answers as they were given; do not correct or translate them."
    )
