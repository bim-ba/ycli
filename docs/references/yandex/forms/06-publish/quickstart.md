---
source: https://yandex.ru/support/forms/en/publish
title: "Publishing a form |"
word_count: 858
token_estimate: 1398
extracted: "2026-05-22T18:01:16Z"
mode: quality
---

Users will be able to fill out the form once you publish it. For example, you can do this by posting a link on your website or socials. If you're using Forms for business, you can publish the form on a Wiki page or in Yandex Tracker.

You can limit the number of form respondents, set a timeframe for submitting responses, and block users who are not part of your organization from filling out the form.

You can make changes to the form and its settings even after publication.

# Publishing a form using a link

To get a link to a form:

1.  Open the form and click **Publish** above the list of questions.

2.  In the **Share this form** pop-up window, copy the form link.

    You can reopen this window later by clicking next to **Publish**.

3.  Send the link to users or post it on public resources.

If you need Yandex Forms service messages — like warnings about invalid inputs — to appear in English, change the domain from `.ru` to `.com` in the link.

# Generating a private link

To distribute private links to your form, for example, among your promo participants, generate keys with unique links. A user can fill out the form using a link from the key only once.

You can use the keys to share the form before it's published. If you click **Publish** in the form builder, the keys will stop working as unique links: if a user follows them, they can fill out the form multiple times.

To generate keys:

1.  Select a form and go to **Settings** → **Personal links**.
2.  Click **Generate keys**.
3.  Enter the name for the keyset and the number of keys.
4.  Click **Generate**: the new keyset will show up in the list.

You can generate up to 10 keysets in total. Each set can hold up to 100 keys.

Links to the form are stored in the keyset's XLS file. To get links to your form, export this file and copy links from it.

To deactivate unused keys, click → **Disable**. The link will change its status to **Inactive**.

# Publishing on a website

To publish a form on your website:

1.  Select the form and click **Publish** above the list of questions.

2.  In the **Share this form** pop-up window, select the link or iframe code, then click to the right.

    You can reopen this window later by clicking next to **Publish**.

3.  Copy the form code from the **Iframe embed code** field.

4.  Paste it into the HTML code of the page where you want to put the form.

5.  Include additional form display parameters in your code if needed.

6.  To only publish your form in an iframe, set up a restriction:

    1.  Go to **Settings** → **Additional**.

    2.  Select **Allow publishing in iframe only**. In this case, you won't be able to share the form via a direct link.

If your site or service uses a [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) with restrictions on embedding sites in iframes, add the `forms.yandex.ru` and `cloud.yandex.ru` domains to the [`frame-src`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/frame-src) directive to ensure your forms function correctly within iframes.

In your site or service settings, add the following string:

```
Content-Security-Policy: frame-src https://forms.yandex.com https://cloud.yandex.ru;
```

## Additional parameters

You can configure the rules for displaying the form on the website:

-   To set the size, change the `width` parameter value. You can specify the size in percentage or pixels.
    For example, if you want the form to fit the page width, specify `width="100%"`.

-   To adjust the form height, add the `height` parameter to the form code. You can specify the value in percentages or pixels.

-   To add a border around the form, change the value of the `frameborder` parameter to `frameborder=1`.

-   \`\`To set a theme for the form, add an ampersand (`&`) and either a theme or `_theme` query parameter with one of the following values after the `iframe=1` URL parameter:

    -   `theme=light`: Light theme.
    -   `theme=dark`: Dark theme.
    -   `theme=dark-hc`: Dark theme with high contrast.
    -   `theme=light-hc`: Light theme with high contrast.

Sample form code:

```
<iframe src="https://forms.yandex.com/1234/?iframe=1&theme=dark" frameborder="1" width="650" height="800"></iframe>
```

# Publishing the form on Wiki

Only users of Yandex Forms for Business can work with Wiki.

To publish a form on a Wiki page:

1.  Click **Publish** above the question list.

2.  In the **Share this form** pop-up window, copy the form link.

    You can reopen this window later by clicking next to **Publish**.

3.  Paste the link into Wiki page text as follows:

    ```
    {% forms src="<link_to_form>" %}
    ```

# Adding the form to  Tracker

You can set up a form for creating issues and integrate it into the Yandex Tracker interface. This form will be displayed on the issue creation page next to the standard one. It will help users create issues based on a certain template without being distracted by unnecessary fields and parameters. For more information, see [Set up issue creation in Yandex Tracker](https://yandex.ru/support/forms/en/create-task#setup).

# Unpublishing the form

To stop accepting responses and unpublish the form:

1.  Select the form and click **Published** above the list of questions.

2.  Click **Unpublish**.