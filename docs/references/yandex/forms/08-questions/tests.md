---
source: https://yandex.ru/support/forms/en/blocks-ref/tests
title: "Tests and quizzes |"
word_count: 561
token_estimate: 1130
extracted: "2026-05-22T18:06:26Z"
mode: quality
---

In Yandex Forms, certain question types can be used in a [test](https://yandex.ru/support/forms/en/tests). These include:

-   [One answer](https://yandex.ru/support/forms/en/blocks-ref/radiobutton)​
-   [Multiple answers](https://yandex.ru/support/forms/en/blocks-ref/multiple)​
-   [Drop-down list](https://yandex.ru/support/forms/en/blocks-ref/dropdown)​

In addition, you can use any **Short answer** questions:

-   [Short text](https://yandex.ru/support/forms/en/blocks-ref/short-text)​
-   [Number](https://yandex.ru/support/forms/en/blocks-ref/number)​
-   [Phone number](https://yandex.ru/support/forms/en/blocks-ref/phone)​
-   [TIN](https://yandex.ru/support/forms/en/blocks-ref/inn)​
-   [Email](https://yandex.ru/support/forms/en/blocks-ref/email)​
-   [Link](https://yandex.ru/support/forms/en/blocks-ref/link)​

Avoid merging questions from the **Tests and quizzes** category into a [series](https://yandex.ru/support/forms/en/blocks-ref/series), as this prevents scoring from working.

# Enable **Score**.

To convert the desired question into a test question:

1.  In the form builder, add the question to the workspace.

2.  Under **Answer**, click **Score**.

3.  Specify the correct answer to the question and the number of points to award for that answer:

    -   If the answer is a number or text, the user will only receive points if their answer exactly matches the punctuation and letter case of the correct answer.

    -   If the question has multiple correct answers, the user must select all of them.

        -   If the user answers everything correctly, they receive the specified points.

        -   If the user misses at least one correct answer or selects at least one incorrect one, they receive no points for the question.

# Examples

Below are examples with questions most frequently used in tests.

-   **Short text**

    The answer must be a word or text up to 255 characters. The user's input must exactly match the correct answer.

    > Question: Fill in the missing letters to complete the sentence: *He's better now th\_n th\_n.*
    >
    > User's answer: He is better now than then
    >
    > The answer is incorrect because the user omitted the period and entered "He is" instead of "He's". No points are awarded.
    >
    > Correct answer: He's better now than then.

-   **Number**

    The answer must be an integer or a fraction with no more than two decimal places. The format of the entered number is checked when the user completes the test.

    > Question: Solve the equation: x+2 = 5x + 2 = 5
    >
    > User's answer: 3
    >
    > The answer is correct, so the user is awarded the specified number of points.

-   **One answer**

    Users can choose an answer from the suggested options. There may be multiple correct answers. Users receive points for any correct answer.

    > Question: How many times did you travel abroad last year?
    >
    > Possible answers:
    >
    > -   I didn't go abroad: 0 points.
    > -   Once: 1 point.
    > -   Two or three times: 3 points.
    > -   More than three times: 5 points.
    >
    > All the suggested options are correct. The more often the user travels abroad, the more points they get for this question.

-   **Multiple answers**

    Users can choose multiple answers from the suggested options. The user receives points only if they select all the correct answers and don't pick any incorrect ones.

    > Question: Which of these cities are in Italy?
    >
    > Possible answers:
    >
    > -   Nice: 0 point.
    > -   Naples: 1 point.
    > -   Valencia: 0 points.
    > -   Milan: 1 point.
    >
    > There are two correct responses among those suggested: Naples and Milan. If the user selects these two cities and doesn't select Nice or Valencia, they'll get 2 points.

### Learn more

-   [How to conduct a test](https://yandex.ru/support/forms/en/tests)
-   [How to score tests](https://yandex.ru/support/forms/en/tests#test-result)
-   [How to show test results](https://yandex.ru/support/forms/en/success-page#test)
-   [How to view answers](https://yandex.ru/support/forms/en/answers)