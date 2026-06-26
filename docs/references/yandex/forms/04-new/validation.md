---
source: https://yandex.ru/support/forms/en/option-validation
title: "Validating an answer |"
word_count: 295
token_estimate: 635
extracted: "2026-05-22T17:58:14Z"
mode: quality
---

For [Short text](https://yandex.ru/support/forms/en/blocks-ref/short-text), [Long text](https://yandex.ru/support/forms/en/blocks-ref/long-text), [Number](https://yandex.ru/support/forms/en/blocks-ref/number), [Mail](https://yandex.ru/support/forms/en/blocks-ref/email), [Phone](https://yandex.ru/support/forms/en/blocks-ref/phone), [TIN](https://yandex.ru/support/forms/en/blocks-ref/inn), and [Share link](https://yandex.ru/support/forms/en/blocks-ref/link) questions, including those with the [**Score**](https://yandex.ru/support/forms/en/blocks-ref/tests#turn-on) option enabled, you can set the **Validation** option in the block settings.

Use validation if you need to check that an answer meets the specified format. For example, you can check that an answer contains text in Russian or doesn't contain unsupported characters. If an answer doesn't meet the specified format, a warning appears saying that the field is filled in incorrectly.

Select a validation method:

-   **No validation**: The answer may contain any characters. Select this method if you don't need input validation.

-   **Email validation**: The answer may only contain Latin letters, numbers, and the characters `@ . _ -` in the following format: `user@domain.ru`.

-   **Link validation**: The answer may only contain Latin or Russian letters, numbers, and the characters `- _ . ~ ! * ' ( ) ; / ? : @ & = + $ ,`.

-   **Phone number validation**: The answer may only contain numbers and the characters `+ -`. Phone numbers can't be shorter than 10 digits.

-   **Validation of fractional numbers**: The answer may only contain an integer or a decimal number.

-   **TIN validation**: The answer may only contain a valid 10–12-digit taxpayer ID and must pass the checksum check.

-   **Validation of letters from the Cyrillic alphabet**: The answer may only contain Russian letters, numbers, spaces, and the characters `. , ; ( )`.

-   **Validation using regular expressions**: You can create a custom [regular expression](https://en.wikipedia.org/wiki/Regular_expression) to validate the response. For example:

    -   A regular expression that only allows entering Latin letters, numbers, and spaces:

        ```
        ^[A-Za-z0-9\s]+$
        ```

    -   A regular expression that allows entering any characters, except numbers and some special characters:

        ```
        ^[^0-9@#$%^&*]+$
        ```