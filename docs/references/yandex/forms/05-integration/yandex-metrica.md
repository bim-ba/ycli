---
source: https://yandex.ru/support/forms/en/metrica
title: "Enabling Yandex Metrica |"
word_count: 304
token_estimate: 656
extracted: "2026-05-22T18:00:58Z"
mode: quality
---

To analyze statistics on form visits and user actions, you can embed a [Yandex Metrica](https://metrika.yandex.com/) tag in the page of your form. For more information about tags, see [Yandex Metrica Help](https://yandex.ru/support/metrica/general/creating-counter.html#counter-html).

# Adding a tag

To add a tag to the form page:

1.  Select a Yandex Metrica tag to use for collecting statistics or [create a new one](https://yandex.com/support/metrica/general/creating-counter.html).

2.  [Copy the form link](https://yandex.ru/support/forms/en/publish#link) and paste it in the tag settings as the website URL.

    To make sure the tag can receive data from different forms or other websites, turn off **Accept data only from the specified addresses** in the tag settings. In this case, you can specify any URL in the **Site address** field.

3.  Go to the **Settings** tab and select **Additional** in the left panel.

4.  Enable the ![](https://yandex.ru/support/forms/docs-assets/support-forms/rev/r19697197/en/_assets/enabled-switch-blue.png) **Connect Yandex Metrica** option and enter the tag number.

5.  Click **Save**.

# Analyze user actions

You can use a Yandex Metrica tag to track the actions of users who opened the form page. For example, you can track the number of users who submitted a completed form and calculate the conversion rate (the percentage of all users who opened the form).

To track user actions:

1.  Add a [Yandex Metrica](https://yandex.ru/support/forms/en/metrica#add-counter) tag to your form.

2.  In Yandex Metrica, go to the tag's settings and [add a goal](https://yandex.com/support/metrica/general/goal-js-event.html).

3.  For the goal, select the **JavaScript event** condition type and specify the ID of the goal with the **contains** condition. Events with the following goal IDs are tracked on the form page:

    -   The user filled in at least one field in the form: `ya-forms_start-change`.

    -   The user clicked **Submit** in the form: `ya-forms_submit`.

    -   The user clicked **Next** in a multi-page form: `ya-forms_next`.

    -   The user clicked **Back** in a multi-page form: `ya-forms_prev`.

For more information about goals, see [Yandex Metrica Help](https://yandex.com/support/metrica/general/goals.html).