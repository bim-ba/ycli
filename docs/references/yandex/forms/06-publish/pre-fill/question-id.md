---
source: https://yandex.ru/support/forms/en/question-id
title: "Getting question and response IDs |"
word_count: 492
token_estimate: 866
extracted: "2026-05-22T18:02:18Z"
mode: quality
---

Question and answer IDs are used to prefill a form. There are several ways to get IDs for different types of questions.

# Questions IDs

Question IDs are specified in the **Settings**, under the corresponding question block.

To reveal additional question settings, click **Show settings** at the top of the question block. To hide the settings, click the icon again.

# IDs for a series of questions

You can add a [series of questions](https://yandex.ru/support/forms/en/blocks-ref/series) to a form several times. This means that questions from a series may repeat. To distinguish between multiple instances of the same question, question IDs that belong in a series get a suffix, which is the instance number after a double underscore. The numbers start with zero: `__0`, `__1`, `__2`.

For example, the form has a series of questions:

-   **Name** with the `text_2643945` ID.

-   **Phone** with the `phone_2752014` ID.

To prefill the fields in a series of questions, configure [GET parameters](https://yandex.ru/support/forms/en/get-params):

-   For the first instance of the series, which is displayed in the form by default, use the `text_2643945__0` and `phone_2752014__0` question IDs.

-   For the second instance of the series, which can be added by clicking **One more**), use the question IDs: `text_2643945__1`, `phone_2752014__1`.

# Answer IDs

To find out the ID of an answer, click **Show settings** at the top of the block.

IDs can be edited. IDs of answers to a single question must be unique.

You can also find out the answer IDs in your browser using developer tools. This feature is available both to the author and user of the form.

# Answer IDs for questions with suggestions

For some types of questions, such as Cities and countries and Wiki, users select their answers from suggested options that appear as they start entering text in the field. To find out the answer ID for these questions:

1.  Open the developer tools using the keyboard shortcut **Ctrl+Shift+I** (for Windows and Linux) or **⌘ + Option + I** (for macOS).

2.  Enter the desired answer in the question field.

3.  In the developer tools, go to the `Network` tab.

4.  Select the last `getSuggest` query from the list on the left.

5.  Go to the `Response` tab and find the desired answer option along with its `id`.

# Answer ID for **Rate on a scale**questions

Let's see how to get IDs using Yandex Browser:

1.  [Open the form by following the link](https://yandex.ru/support/forms/en/publish#link).

2.  Open the developer tools using the keyboard shortcut **Ctrl+Shift+I** (for Windows and Linux) or **⌘ + Option + I** (for macOS).

3.  Select the ![](https://yandex.ru/support/forms/docs-assets/support-forms/rev/r19697197/en/_assets/select-element.png) tool and click the necessary answer field, list, or marker.

    You will see a fragment of the page code with the question or answer parameters highlighted in the **Elements** tab.

4.  Find the ID values in the code:

    -   Question ID: The `name` parameter value.

    -   Answer ID: The last two digits of the `data-qa` parameter value. In the example below, this is `6815528_6815524`.