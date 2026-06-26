---
source: https://yandex.ru/support/forms/en/blocks-ref/wiki
title: "Wiki |"
word_count: 816
token_estimate: 1481
extracted: "2026-05-22T18:05:39Z"
mode: quality
---

To answer this question, you can select data pulled from a [Wiki dynamic table](https://yandex.com/support/wiki/ru/wysiwyg/grid). Answers not listed in the table are not accepted.

Data from the [dynamic Wiki table](https://yandex.com/support/wiki/ru/wysiwyg/grid) is updated every 30 minutes, which is why answer options may be loaded with a delay.

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

Use the **Wiki** value to upload answer options from a [dynamic table](https://yandex.com/support/wiki/wysiwyg/grid.html).

### Link to the table

Specify an absolute or [relative](https://yandex.com/support/wiki/structure.html#relative) link to the dynamic table in Wiki. For example:

`https://wiki.yandex.com/users/<username>/<page_name>?gridId=<table_ID>`

`/users/<username>/<page_name>?gridId=<table_ID>`

You can copy the link to the dynamic table from the [table settings](https://yandex.com/support/wiki/ru/wysiwyg/grid#share).

For instructions on how to create a table in Wiki, see [Table of answer options](https://yandex.ru/support/forms/en/blocks-ref/wiki#table).

# Filter answers

This option loads different answer options based on what the user selected in the previous (parent) Wiki block. To filter answer options:

1.  Add another **Wiki** parent block to the form and enter the link to the dynamic table.

2.  In Wiki, create another dynamic table with an additional column for filtering. For more information, see [Table with answer filtering](https://yandex.ru/support/forms/en/blocks-ref/wiki#filter).

3.  Add another **Wiki** block to the form and enter the link to the table you created.

4.  In the **Filter answers** list, select the **Wiki** parent block with the parent table.

Answer options in the second block will vary based on the answer that the user selected in the parent block.

# Settings

To reveal additional question settings, click **Show settings** at the top of the question block. To hide the settings, click the icon again.

### Questions IDs

Use the question ID to [prefill the form](https://yandex.ru/support/forms/en/pre-fill).

Question IDs may contain capital and lowercase Latin letters, numbers, `-` and `_` characters. Make sure all questions in the same form have unique IDs.

### Hide question

Enable this option to hide a question in the form. You can use hidden questions to [pass service or auxiliary parameters](https://yandex.ru/support/forms/en/pre-fill#hidden-query).

Don't select both the **Hide question** and **Required** options at the same time. Otherwise, users won't be able to submit the form.

# How to create a table in Wiki

### Table of answer options

The table of answer options for the Wiki block must use a special format. To create this table:

1.  In [Wiki](https://wiki.yandex.com/), create a [dynamic table](https://yandex.com/support/wiki/ru/wysiwyg/grid).

2.  Add a column named `name` to the table.
    If there are other columns in the table, they will not affect the answer options in the Wiki block.

3.  Add multiple rows to the table. In the `name` column cells, enter answer options that should be selectable in the Wiki block.

4.  Make sure the service account `yndx-wiki-cnt-robot@` has [access to the table](https://yandex.com/support/wiki/page-management/access-setup.html). This account also has access to the table if **Available to all employees** mode is on.

5.  Specify a link to the table in the [Wiki block settings](https://yandex.ru/support/forms/en/blocks-ref/wiki#link-answers).

### Table with answer filtering

To create a table with answer filtering:

1.  In [Wiki](https://wiki.yandex.com/), create a [dynamic table](https://yandex.com/support/wiki/ru/wysiwyg/grid).

2.  Add columns named `name` and `parent` to the table.
    If there are other columns in the table, they will not affect the answer options in the Wiki block and their filtering.

3.  Add multiple rows to the table. In the `name` column cells, enter answer options that should be selectable in the Wiki block.

4.  Link each answer option to a row in the parent table, which is the table specified in the parent Wiki block settings. To do so, go to the `parent` column and specify the row number in the parent table that should load the answer in the **Wiki** block with filtering.
    For example, if the user selects an answer from row number `1`, in the parent block, answer options that have `1` specified in the `parent` column are available in the block with filtering.

5.  Make sure the service account `yndx-wiki-cnt-robot@` has [access to the table](https://yandex.com/support/wiki/page-management/access-setup.html). This account also has access to the table if **Available to all employees** mode is on.

6.  Specify a link to the table in the Wiki block settings and [enable answer filtering](https://yandex.ru/support/forms/en/blocks-ref/wiki#filter).