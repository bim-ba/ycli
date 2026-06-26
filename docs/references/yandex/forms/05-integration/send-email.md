---
source: https://yandex.ru/support/forms/en/send-mail
title: "Sending an email |"
word_count: 958
token_estimate: 1571
extracted: "2026-05-22T17:58:51Z"
mode: quality
---

You can integrate your form with Yandex Mail so that a notification is sent automatically when the user fills out the form.

# Configuring notifications

1.  Select the desired form and open the **Integration** tab.

2.  Select a [group of actions](https://yandex.ru/support/forms/en/notifications#add-integration) for which you want to set up sending emails and click ![](https://yandex.ru/support/forms/docs-assets/support-forms/rev/r19697197/en/_assets/mail-notification-new.png) **Email** at the bottom of the group.

3.  Under action settings, fill in the following fields:

    -   **To**: Email address to send the notification to. You can list multiple addresses separated by commas, or set a variable.

        -   To send a notification to the form creator's email, select the **Form creator's email** variable.

        -   To send a notification to the Yandex email account the user was logged in to when filling out the form, select the **Email** variable. This option is only available to Yandex Forms for business users.

        -   To send a notification to the address the user entered when answering a question, add the **Question answer** variable and select the Email question type.

    -   **Sender**: Sender name you want the recipient to see.

    -   **Send response to**: Email address the recipient can send responses to. If not specified, your respondents will not be able to reach you by email.

    -   **Subject**: Email subject.

    -   **Text**: Email text.

    -   If necessary, add service headers to the message. To add a header:

        -   Click **Add header**.
        -   Specify a name and value for each header.
            The header name must begin with the prefix `X-` and must not contain Cyrillic characters. Otherwise, the header will be ignored. Header name example: `X-Form`.
        -   You can use [variables](https://yandex.ru/support/forms/en/vars) as parameter values. To do this, click on the right of the field. If you're using a variable, enable **Send if value is set**.

    You can insert an answer to a question or other form data in any field:

    -   Select the field and click on the right.

    -   Select a [variable](https://yandex.ru/support/forms/en/vars) from the list to add to the field. For example, you can add a variable to address the user by their name or to include their [test results](https://yandex.ru/support/forms/en/tests) in the email.

4.  To attach a file from your computer to the email, click **Attach file**.

    To attach the files that the user sent in response to the form to your email, select questions of the File type from the **Attach files from question answers** list.

    The maximum total size of the email is 9 MB. This includes technical information, the message body, and the attached files.

5.  To display a message informing the user that an email was sent after they filled out the form, enable the **Show messages about the results of actions** option under the action name.

6.  Click **Save**.

To send multiple email notifications at once, add new actions using the ![](https://yandex.ru/support/forms/docs-assets/support-forms/rev/r19697197/en/_assets/mail-notification-new.png) **Email** button at the bottom of the action group.

If you want notifications to only be sent to users who gave certain answers, [set your conditions](https://yandex.ru/support/forms/en/notifications#conditions).

> Sample notification for a form with a questionnaire for job applicants Once the form is filled out, the survey answers are sent to the HR department's email address.
>
> ![](https://yandex.ru/support/forms/docs-assets/support-forms/rev/r19697197/en/_assets/email-example-new.png)

# Troubleshooting

If you set up email notifications but are not getting emails after filling out the form, check your **Spam** folder and see if there are errors when sending emails.

## Check your **Spam**folder

If you are not receiving email notifications, check your Spam folder. If emails from Yandex Forms were sent to the **Spam** folder, mark them as Not spam.

If you use your own mail server, whitelist the sender addresses: `<form_ID>@forms.yandex.com` and `sndr.bnc@yandex.ru`.

## Check the email text

The mail server can block an email if its text is missing or looks like spam. Fill out or edit the email text.

## Check the size of attachments

If a file attached to an email is too big, the mail server will not be able to send it. When this happens, the following error message will appear:

```
Error class: EmailMaxSizeExceededError
Error message: Total file size must be less than 9 MB.
```

The maximum total size of the email is 9 MB. This includes technical information, the message body, and the attached files.

To avoid this error, limit the maximum size of files that users can attach to forms. To do this, in the **File** question settings, set the [maximum total file size](https://yandex.ru/support/forms/en/blocks-ref/file#max-size) to no more than 8 MB.

If you need users to be able to attach large files to their answers, use **Share link** or **Short text** questions. This way, users will be able to link files uploaded to an external hosting.

## Check for integration errors

To check for errors that occur during the form integration:

1.  Open the form where the integration is incomplete or doesn't work as expected.

2.  Go to the **Integrations** tab and click **Completed integrations**.

3.  Check the list for error messages related to your integration.

4.  After resolving the problem, try [creating an issue again](https://yandex.ru/support/forms/en/notifications-history#status).

5.  If the problem persists, [contact support](https://yandex.ru/support/forms/en/feedback).

## If there are no spam notifications or error messages

If you have no notifications in the Spam folder or errors in the **Integration** tab, the email may be blocked by the recipient's mail server. To find out why the email is blocked:

1.  Open the form with notification issues and click **Integration** at the top of the page.

2.  In the email notification settings, go to the **Send response to** field and enter your personal or corporate email.

3.  The next time the mail server blocks a notification from the form, an error message will be sent to the email that you specified. Copy the message text.

4.  [Contact Yandex Forms support](https://yandex.ru/support/forms/en/feedback) and include the error message that you received.