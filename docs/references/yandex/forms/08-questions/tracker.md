---
source: https://yandex.ru/support/forms/en/blocks-ref/tracker
title: "Tracker |"
word_count: 449
token_estimate: 863
extracted: "2026-05-22T18:05:33Z"
mode: quality
---

To answer this question, you can select an entity from Yandex Tracker. The list of available answer options depends on the user's access rights.

# Question

Enter the question title or text.

-   To add a comment or hint to a question, click **Add explanation**. The text of a comment is displayed using a smaller font size.

    To format the text of a question or comment, use [Markdown markup](https://yandex.ru/support/forms/en/appearance#text-formatting).

-   To add an image to the question, click **Add image**.

-   To make a question required, turn on the ![](https://yandex.ru/support/forms/docs-assets/support-forms/rev/r19697197/en/_assets/enabled-switch-blue.png) **Required** option in the top right corner of the block.

    Required questions are marked with an asterisk (\*) in the form. If a user skips a required question, they won't be able to submit the form.

-   To show or hide a question based on previous answers, click **Display conditions** in the top right corner of the block. For more information, see [Configure display conditions for questions or pages](https://yandex.ru/support/forms/en/add-questions#conditions).

# Answers

### Multiple answers

Enable this option to allow users to select multiple answer options for a question.

### Data type

To ensure relevant input prompts, specify the type of data the user needs to enter:

-   **Queue**: [Queue](https://yandex.com/support/tracker/queue-intro.html) name or key.
-   **Task**: [Issue](https://yandex.com/support/tracker/user/create-ticket.html) name or key.
-   **Component**: [Component](https://yandex.com/support/tracker/manager/components.html) name.
-   **Board**: [Board](https://yandex.com/support/tracker/manager/agile-new.html) name.
-   **Sprint**: [Sprint](https://yandex.com/support/tracker/manager/create-agile-sprint.html) name.
-   **Project**: [Project](https://yandex.com/support/tracker/manager/project-new.html) name.

# Filter answers

This option allows users to select issues or components from the queue they selected in a previous (parent) Tracker<\\q> block. To filter answer options:

1.  Add a parent **Tracker** block with the **Queue** type to the form.

2.  Add a second **Tracker** block with the **Issue** or **Component** type. Filtering only applies to blocks with that data type.

3.  In the **Filter answers** list, select the parent **Tracker** block.

It's handy to use filtering along with the **Multiple answers** option, because it helps extend the list of answer options. For instance, if the user selected two queues in the parent block, they will be able to select issues from both queues in the filtered block.

# Settings

To reveal additional question settings, click **Show settings** at the top of the question block. To hide the settings, click the icon again.

### Questions IDs

Use the question ID to [prefill the form](https://yandex.ru/support/forms/en/pre-fill).

Question IDs may contain capital and lowercase Latin letters, numbers, `-` and `_` characters. Make sure all questions in the same form have unique IDs.

### Hide question

Enable this option to hide a question in the form. You can use hidden questions to [pass service or auxiliary parameters](https://yandex.ru/support/forms/en/pre-fill#hidden-query).

Don't select both the **Hide question** and **Required** options at the same time. Otherwise, users won't be able to submit the form.