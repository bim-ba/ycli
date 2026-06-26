---
source: https://yandex.ru/support/forms/en/send-wiki
title: "Adding a response to Wiki |"
word_count: 922
token_estimate: 1686
extracted: "2026-05-22T17:59:15Z"
mode: quality
---

Yandex Forms for Business users can set up integration with Wiki.

You can integrate your form with [Wiki](https://wiki.yandex.com/) to save user responses on a Wiki page. For example, if you are using a form to register participants for an event, you can automatically create a list of participants in Wiki. For more information about Wiki pages, see the [Wiki documentation](https://yandex.com/support/wiki/pages-types.html).

Integration will not work if user access to a Wiki page is restricted. In this case, [grant access](https://yandex.com/support/wiki/page-management/access-setup.html) to your page for the service account `@yndx-wiki-cnt-robot`.

Settings for sending responses to Wiki differ depending on the response destination: a [Wiki page](https://yandex.ru/support/forms/en/send-wiki#editor) or a [dynamic table](https://yandex.ru/support/forms/en/send-wiki#grid).

# Adding responses to a page

To set up adding form responses to a Wiki page:

1.  Select the desired form and open the **Integration** tab.

2.  Select a [group of actions](https://yandex.ru/support/forms/en/notifications#add-integration) for which you want to set up sending responses to Wiki and click ![](https://yandex.ru/support/forms/docs-assets/support-forms/rev/r19697197/en/_assets/wiki-notification-new.png) **Wiki** at the bottom of the group.

3.  Specify the address of the Wiki page where you want to send data from the form. Specify the address without a domain. For example: `users/login/my-page`.

4.  In the **Select action** field, choose **Add to page**.

5.  In the **Text to be saved** field, specify what data should be added to the page. You can use YFM markup to format your text. To learn more, see [Wiki Help](https://yandex.com/support/wiki/wysiwyg/text-format.html).

    To add to the text an answer to a question or other data from the form:

    1.  Click in the top right corner of the field.

    2.  Select a [variable](https://yandex.ru/support/forms/en/vars) from the list to add to the field. For instance, you can add a user's name and email to the text.

    Fields can also contain an **Answer to question** variable. If an answer contains YFM markup elements, they are automatically converted to text formatting elements when you add it to a Wiki page.

6.  By default, responses are added to the bottom of the page. To embed the responses at the top of the page, select **Add answer to page** → **To the beginning**.

    To add responses to a specific place on the page:

    1.  On the page, place an anchor where you want the form responses to be added. For example: `#[Anchor](https://yandex.ru/support/forms/anchor)`.

    2.  In the Wiki integration settings, append the `#` character and the name of the anchor to the page address like this: `users/login/my-page#anchor`. The form responses will be embedded on the page after the anchor.

    For more information about anchors, see [Wiki Help](https://yandex.com/support/wiki/wysiwyg/text-format.html#anchor).

7.  To get a link to the Wiki page after filling out the form, enable the **Show messages about the results of actions** option under the action name.

8.  Select the integration language. If the translation is available, the integration will be performed in the chosen language. By default, Russian is used for CIS countries, and English is used for all other regions.

9.  Click **Save**.

# Adding form responses to a dynamic table

To import form responses to a Wiki dynamic table:

1.  Select the desired form and open the **Integration** tab.

2.  Select a [group of actions](https://yandex.ru/support/forms/en/notifications#add-integration) for which you want to set up sending responses to Wiki and click ![](https://yandex.ru/support/forms/docs-assets/support-forms/rev/r19697197/en/_assets/wiki-notification-new.png) **Wiki** at the bottom of the group.

3.  Specify the address of the dynamic table to send the data from the form to. In the **Page address** field, add an absolute or [relative](https://yandex.com/support/wiki/structure.html#relative) link to the dynamic table. For example:

    `https://wiki.yandex.com/users/<username>/<page_name>?gridId=<table_ID>`

    `/users/<username>/<page_name>?gridId=<table_ID>`

    You can copy the link to the dynamic table from the table settings. To learn more, see [Wiki Help](https://yandex.com/support/wiki/wysiwyg/grid.html#share).

4.  In the **Select action** field, specify where you want to embed the form data.

    -   To embed data on the page that hosts the dynamic table, select **Add to page**.
    -   To embed data in the dynamic table, select **Add to grid**.
5.  Under **Data to write**, select the column where you want to embed the data. You can select multiple columns. Specify the data individually for each column.

6.  Below, indicate what data you want to add to the table. You can use [YFM markup](https://yandex.com/support/wiki/wysiwyg/text-format.html) to format the text. To add to the text an answer to a question or other data from the form:

    1.  In the column text box, click .

    2.  Select a [variable](https://yandex.ru/support/forms/en/vars) from the list to add to the field. For example, you can add a user's name and email address to the text.

7.  In the **Add answer to page** field, select where to add the new rows: the beginning or the end of the table.

8.  To get a link to the Wiki page after filling out the form, enable the **Show messages about the results of actions** option under the action name.

9.  Select the integration language. If the translation is available, the integration will be performed in the chosen language. By default, Russian is used for CIS countries, and English is used for all other regions.

10.  Click **Save**.

To send responses to multiple Wiki pages at once, add multiple actions using the ![](https://yandex.ru/support/forms/docs-assets/support-forms/rev/r19697197/en/_assets/wiki-notification-new.png) **Wiki** button at the bottom of the page.

If you want data to be sent to Wiki only if the user gave certain responses, [set the conditions](https://yandex.ru/support/forms/en/notifications#conditions).

# Troubleshooting

To check for errors that occur during the form integration:

1.  Open the form where the integration is incomplete or doesn't work as expected.

2.  Go to the **Integrations** tab and click **Completed integrations**.

3.  Check the list for error messages related to your integration.

4.  After resolving the problem, try [creating an issue again](https://yandex.ru/support/forms/en/notifications-history#status).

5.  If the problem persists, [contact support](https://yandex.ru/support/forms/en/feedback).