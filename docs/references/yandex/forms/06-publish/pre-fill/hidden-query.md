---
source: https://yandex.ru/support/forms/en/hidden-query
title: "Configure pre-filling of a hidden field |"
word_count: 294
token_estimate: 596
extracted: "2026-05-22T18:02:28Z"
mode: quality
---

You can use hidden fields to automatically send technical or auxiliary parameters, such as [UTM tags](https://en.wikipedia.org/wiki/UTM_parameters), to the form. This way, you can add additional info to user responses for analytics and statistics.

> Let's say you created a form and posted it on different websites. Now you want to know which website the user filled out the form on. To find this out, use the `utm_source` UTM tag.
>
> Add a hidden Source of responses field to the form. Add a GET parameter to the link, and its value will automatically be sent to the hidden field. Then you can see where responses came from.

To set up a hidden parameter for this example:

1.  Add a [Short text](https://yandex.ru/support/forms/en/blocks-ref/short-text) question titled Source of responses to the form.

2.  Enable **Hidden question** for this question.

3.  In the **Question ID** field, specify `utm_source`: that's the [GET parameter](https://yandex.ru/support/forms/en/get-params) name.

4.  [Get a link to the form](https://yandex.ru/support/forms/en/publish#link) and add the `?utm_source=site_name_1` GET parameter at the end.

    -   Sample link to the form without the GET parameter:
        `https://forms.yandex.comu/6191b18d99e21b1********/`

    -   Sample link to the form with the GET parameter:
        `https://forms.yandex.comu/6191b18d99e21b1********?utm_source=site_name_1`

5.  Post the form link with the GET parameter on the website.

6.  In the same way, create another link to be placed on another website. To do this, add the GET parameter `?utm_source=site_name_2` at the end of the URL.

7.  When a user follows the link, the `site_name_1` or `site_name_2` value is automatically entered in the hidden Source of responses field. Based on this value, you can determine on which website the user filled out your form.

To enable pre-filling of a hidden field when [embedding a form in a website with an iframe](https://yandex.ru/support/forms/en/publish#publlish-site), specify the URL with the GET parameters in the iframe embed code.