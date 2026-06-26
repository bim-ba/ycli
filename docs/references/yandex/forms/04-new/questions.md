---
source: https://yandex.ru/support/forms/en/add-questions
title: "Add questions to a form |"
word_count: 1531
token_estimate: 3309
extracted: "2026-05-22T17:57:41Z"
mode: quality
---

Forms consist of questions (fields or lists) where users provide answers or enter data. You can set validation rules and answer options for questions, and configure when questions appear based on how the user answered other questions.

1.  To add a question block to your form, select a question from the popular question types on the **Form builder** tab.

    To see all available questions, click **Show all questions**. [Which questions to use](https://yandex.ru/support/forms/en/add-questions#questions-list)

2.  You can add a new question anywhere in the form. To add a question, hover over the top or bottom of a question block and click .

3.  You can change the type for some questions without losing the field values. To change the question type, click the type name in the top-left corner of the block and select a new value from the drop-down list.

4.  [Configure the question parameters](https://yandex.ru/support/forms/en/add-questions#params).

5.  You can reorder questions in two ways:

    -   Select a question in the question area and drag it by the icon.

    -   Select a question in the **Contents** section and drag it by the icon.

6.  To show or hide questions based on how the user answered other questions, configure [question display conditions](https://yandex.ru/support/forms/en/add-questions#conditions).

7.  To copy a question, click → in the top-right corner of the block.

8.  To delete a question, click → in the top-right corner of the block.

9.  To split a form into multiple pages, click **Add page** to the right of the **Contents** section or at the bottom of the page.

    Users can't go to the next page until they fill in the required fields.

10.  To see what your form will look like, click in the top right corner of the page.

# Set up question parameters

### Show settings

To reveal additional question settings, click **Show settings** at the top of the question block. To hide the settings, click the icon again.

Question blocks show different parameters based on the question type. Parameters fall into three groups:

-   **Question** — the main block content, which includes the question and any clarifying information.

-   **Answers** — parameters for questions with multiple answer options. You can define answer options and specify how many options the user can choose.

-   **Settings** — additional question parameters. For example, sorting of answer options or field pre-population.

For detailed parameter descriptions, see [Question reference](https://yandex.ru/support/forms/en/blocks-ref/blocks-reference).

# Split a form into pages

If your form has a lot of questions or you want to group them by topic, you can split the form into multiple pages.

Users will be required to complete all fields on the current page before moving to the next. You can also configure when pages appear in the form.

1.  To add a page, click **Add page** below the question list or in the **Contents** panel to the right.

2.  Add new questions to the page or move questions from previous pages.

3.  To show or hide pages based on how the user answered the previous questions, configure display conditions. For more information, see [Configure display conditions for questions or pages](https://yandex.ru/support/forms/en/add-questions#conditions).

### Manage pages

To copy a page with all question parameters, click → **Duplicate** in the top-right corner of the page.

To delete a page, click → **Delete** in the top-right corner of the page.

# Configure display conditions for questions or pages

Configure when a question or an entire page appears based on a user's answers to previous questions:

1.  Click **Display if…** in the top-right corner of the block.

2.  Set the block display condition:

    1.  Select the question that determines whether the block or page appears.

        For the condition, you can select any question located above it in the form, with the exception of the following question types: [Text with no questions](https://yandex.ru/support/forms/en/blocks-ref/no-question), [Rating on a scale](https://yandex.ru/support/forms/en/blocks-ref/rating), [File](https://yandex.ru/support/forms/en/blocks-ref/file), [Questions series](https://yandex.ru/support/forms/en/blocks-ref/series).

    2.  Select the comparison operator: **equal** or **not equal**.

    3.  Select or enter the answer that the user's answer has to match.

3.  If you need to display the block when multiple conditions are met, click under the first condition. Set up the condition: select a question, a comparison operation, and an answer option.

    The new condition will be grouped with the existing ones. By default, all conditions within the group are combined using the **AND** operator, so the block appears in the form only if all conditions are met simultaneously. If you want to display the block when at least one condition is met, click the operator icon to the left of the group to select the logical **OR** instead.

4.  To set a more complex logic for displaying the block, add multiple groups of conditions. To do this, click **Add condition** under the list of conditions, then configure the conditions within the group and select a logical operator to apply to them: **AND** or **OR**.

    By default, all groups are combined using the logical **AND** operator, so the block appears in the form only if all conditions across all groups are met simultaneously. If you want to display the block when conditions within at least one group are met, click the operator icon to the left of each group to select the logical **OR** instead.

5.  To delete a condition, hover over it and click to the right.

6.  Click **Save**.

> **Example.** In the screenshot, the conditions are set up in such a way that the question "Specify your email" is displayed when the conditions are met in any of the groups (the groups are combined using the logical **OR**):
>
> -   For the question "Have you used our service?", the person selected "I want to try it" and also answered "Yes" to "Do you want to receive our newsletter?" (the conditions within the group are combined using the logical **AND**).
>
> -   For the question "Have you used our service?", the person selected "I'm already a user".
>
>
> ![](https://yandex.ru/support/forms/docs-assets/support-forms/rev/r19697197/en/_assets/condition-example.png)

### Setting up conditions

-   If you put the logical **AND** operator between the conditions, the final result is TRUE if all conditions are met simultaneously. If you use the logical **OR**, the result is TRUE if at least one condition is met.
-   For complex conditions, the TRUE or FALSE result is first determined for each of the groups, then the final result is obtained by applying a common logical operator to the results of individual groups.
-   You can't set up a display condition for the first block in the form.
-   We don't recommend adding conditions whose display depends on questions that are shown based on other conditions. If a question is omitted, all conditions associated with that question return FALSE.

# How to add a field for an arbitrary answer

To allow a user to give an arbitrary answer in a form with a fixed set of answers, use a condition for showing a question:

1.  Add these questions to the form:

    -   **Multiple answers** or **One answer** with multiple answer options. In addition to fixed answers, specify an arbitrary one, for example, `Other`.

    -   **Short text**. The user can enter any text here.

2.  In the form builder, select the **Short text** question and click **Display if…**.

3.  Set the condition for showing the question:

    -   Select a question with fixed answer options that determine whether to show or hide the block.

    -   Select the **equals** operator.

    -   Select **Other**.

This way, if the user selects **Other** in a multiple-choice question, they will see a field for entering any text.

# Which questions to use

If you aren't sure which question block is right for your form, use the table:

| What answer format you expect | Which block to choose |
| --- | --- |
| Any word or short phrase. For example, a name. | [Short text](https://yandex.ru/support/forms/en/blocks-ref/short-text) |
| Any long text. For example, a review. | [Long text](https://yandex.ru/support/forms/en/blocks-ref/long-text) |
| Information that doesn't require an answer. For example, a header for a group of questions. | [Text with no questions](https://yandex.ru/support/forms/en/blocks-ref/no-question) |
| Test or quiz. | [Tests and quizzes](https://yandex.ru/support/forms/en/blocks-ref/tests) |
| **Numbers** |  |
| An integer. For example, the number of people. | [Integer](https://yandex.ru/support/forms/en/blocks-ref/integer) |
| A number. For example, the amount of money. | [Number](https://yandex.ru/support/forms/en/blocks-ref/number) |
| Date or date range. For example, the date of an event. | [Date](https://yandex.ru/support/forms/en/blocks-ref/date) |
| **User info** |  |
| An email address. | [Email](https://yandex.ru/support/forms/en/blocks-ref/email) |
| Phone number. | [Phone number](https://yandex.ru/support/forms/en/blocks-ref/phone) |
| A link. For example, a social media profile. | [Link](https://yandex.ru/support/forms/en/blocks-ref/link) |
| A file uploaded by the user. For example, a photo. | [File](https://yandex.ru/support/forms/en/blocks-ref/file) |
| The name of a city or country. For example, the user's place of residence. | [Cities and countries](https://yandex.ru/support/forms/en/blocks-ref/cities) |
| The TIN of an individual or legal entity. | [TIN](https://yandex.ru/support/forms/en/blocks-ref/inn) |
| **User's opinion** |  |
| An answer selected from the dropdown list. For example, shoe size. | [Drop-down list](https://yandex.ru/support/forms/en/blocks-ref/dropdown) |
| An answer selected from the given options. For example, the color of the product. | [One answer](https://yandex.ru/support/forms/en/blocks-ref/radiobutton) |
| Multiple answers selected from the given options. For example, the user wants to order several services. | [Multiple answers](https://yandex.ru/support/forms/en/blocks-ref/multiple) |
| Multiple ratings on a given scale. For example, rating an event using multiple criteria. | [Rating on a scale](https://yandex.ru/support/forms/en/blocks-ref/rating) |
| Agreement with a statement or consent to an action. For example, consent to receive emails. | [Yes/No](https://yandex.ru/support/forms/en/blocks-ref/yes-no) |
| Group of repeating questions. For example, to enter multiple participants' data to register them for an event. | [Questions series](https://yandex.ru/support/forms/en/blocks-ref/series) |
| **Organization's data** |  |
| Яндекс 360 для бизнеса employee's name. | [People](https://yandex.ru/support/forms/en/blocks-ref/people) |
| Яндекс 360 для бизнеса department name. | [Departments](https://yandex.ru/support/forms/en/blocks-ref/departments) |
| Яндекс 360 для бизнеса team name. | [Teams](https://yandex.ru/support/forms/en/blocks-ref/teams) |
| **Testing knowledge or running a quiz** |  |
| To create a test that scores responses based on the number of correct answers, use questions from the **Tests and quizzes** section. | [Tests and quizzes](https://yandex.ru/support/forms/en/blocks-ref/tests) |