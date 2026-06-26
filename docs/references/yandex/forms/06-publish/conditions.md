---
source: https://yandex.ru/support/forms/en/send-condition
title: "Configuring conditions for submitting a response |"
word_count: 382
token_estimate: 651
extracted: "2026-05-22T18:01:32Z"
mode: quality
---

You can configure requirements in a form for allowing users to submit a a response, or add a CAPTCHA to prevent automated responses.

# Set conditions for submitting a response

The submit button can be shown or hidden depending on how the user responded to the questions. For example, you can allow submits only by users from a specific city.

1.  Select a form and go to **Settings** → **Text and submit logic**.

2.  Under **Form submission button**, select **Activate button** → **On condition**.

3.  Set the condition under which the user can submit a response:

    1.  Select the question that determines whether to show or hide the submit button.

        The submit button will be disabled if the selected question is hidden in the form based on a [condition](https://yandex.ru/support/forms/en/add-questions#conditions).

    2.  Select the comparison operator: **equal** or **not equal**.

    3.  Select or enter the answer that the user's input has to match.

4.  If you need to allow submitting a response only when multiple conditions are met, click under the first condition. Set up the condition: select a question, a comparison operation, and an answer option.

    The new condition will be grouped with the existing ones. By default, all conditions within the group are combined using the **AND** operator, so the user can submit their response only if all conditions are met simultaneously. If you want users to be able to submit responses when at least one condition is met, click the operator icon to the left of the group to select the logical **OR** instead.

5.  To set a more complex logic, add multiple groups of conditions. To do this, click **Add condition** under the list of conditions, then configure the conditions within the group and select a logical operator to apply to them: **AND** or **OR**.

6.  To delete a condition, hover over it and click to the right.

7.  At the bottom of the page, click **Save**.

For more information about setting up conditions, see [Add questions to a form](https://yandex.ru/support/forms/en/add-questions#conditions).

# Add a CAPTCHA to the form

To prevent automated responses to your form, you can ask the user to enter a [CAPTCHA](https://en.wikipedia.org/wiki/CAPTCHA) before submitting their response.

1.  Select a form and go to **Settings** → **Additional**.

2.  Enable the ![](https://yandex.ru/support/forms/docs-assets/support-forms/rev/r19697197/en/_assets/enabled-switch-blue.png) **Add captcha before submitting form** option.

3.  Click **Save**.