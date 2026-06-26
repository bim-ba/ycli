---
source: https://yandex.ru/support/forms/en/create-task
title: "Creating an issue in Yandex Tracker |"
author: "Error in the Author, Assignee, and Follower fields"
word_count: 983
token_estimate: 1768
extracted: "2026-05-22T17:59:01Z"
mode: quality
---

Only Yandex Forms for Business users can set up integration with Yandex Tracker.

You can integrate your form with [Yandex Tracker](https://tracker.yandex.com/) to automatically create issues from user responses. The user's answers are sent from the form to Yandex Tracker, and a new issue is created based on the submitted information. This flow can be useful for accepting service requests, collecting error logs, and similar scenarios. For more information about issues, see [Yandex Tracker Help](https://yandex.com/support/tracker/user/create-ticket.html).

# Set up issue creation in Yandex Tracker

1.  Select the desired form and open the **Integration** tab.

2.  Select an [action group](https://yandex.ru/support/forms/en/notifications#add-integration) for which you want to set up issue creation and click ![](https://yandex.ru/support/forms/docs-assets/support-forms/rev/r19697197/en/_assets/tracker-notification-new.png) **Tracker** at the bottom of the group.

3.  Enter the [queue](https://yandex.com/support/tracker/queue-intro.html) key to create your issue in.

4.  To create a [sub-issue](https://yandex.com/support/tracker/user/create-ticket.html#subtask), enable **Convert to sub-issue** and enter the parent issue key.

5.  Set up the type, issue priority, and other parameters:

    -   In the **Author**, **Assignee**, and **Followers** fields, specify a username in `user` format.

        To specify multiple users in the **Followers** field, enter their usernames separated by commas (for example, `smith,johnson`).

    -   If the integration settings don't specify the **Author** and a user from your organization completes the form, that user will be specified as the issue's author.

        If an unauthorized user completes the form, Tracker Robot (`yndx-tracker-cnt-robot@`) is specified in the **Author** field.

    -   The remaining fields should be completed exactly as they appear in Yandex Tracker.

    -   To add multiple values to the **Components** or **Tags** field, separate them with commas.

    -   You can use YFM markup in the issue description. To learn more, see [Yandex Tracker Help](https://yandex.com/support/tracker/user/syntax-yfm.html).

    No suggestions appear when entering values in the fields such as **Author**, **Assignee**, **Tags**, or **Components**.

6.  You can also create a new field if the one you need isn't available in the issue parameters. To do this, click **Add issue parameter** and start typing its name, then select the desired parameter from the suggested options.

    For more information about issue parameters, [Yandex Tracker Help](https://yandex.com/support/tracker/user/create-param.html).

7.  To populate the issue fields with answers to questions or other data from the form:

    1.  Select a field and click on the right.

    2.  Select a [variable](https://yandex.ru/support/forms/en/vars) from the list to add to the field.

    For example, if your form collects error messages, you can add the user's message and technical details to the issue description.

    Fields can also contain an **Answer to question** variable. If an answer contains [YFM markup](https://yandex.com/support/tracker/user/syntax-yfm.html) elements, they are automatically converted to text formatting elements when you add the answer to the issue description in Yandex Tracker.

    To add an employee specified in an answer to a People, to the **Author**, **Assignee**, **Followers** fields in Tracker, add a **Question answer option ID** variable to the field. If you use an **Answer to question** variable, integration won't work.

8.  To get a link to the new issue after filling out the form, enable the **Show messages about the results of actions** option under the action name.

9.  Click **Save**.

To create multiple issues at once, add new actions by clicking ![](https://yandex.ru/support/forms/docs-assets/support-forms/rev/r19697197/en/_assets/tracker-notification-new.png) **Tracker** at the bottom of the page.

# Example

If you want an issue to only be created for users who give certain answers, [set your conditions](https://yandex.ru/support/forms/en/notifications#conditions).

> Example of integration with Yandex Tracker for a request form for equipment procurement. Employees can use this form to submit equipment requests, and these requests will be transformed into issues for the procurement department.
>
> ![](https://yandex.ru/support/forms/docs-assets/support-forms/rev/r19697197/en/_assets/tracker-example-new.png)

# Embed a form in the Yandex Tracker interface

You can set up a form for creating issues and integrate it into the Yandex Tracker interface. This form will be displayed on the issue creation page next to the standard one. It will help users create issues based on a certain template without being distracted by unnecessary fields and parameters. For more information, see [Set up issue creation in Yandex Tracker](https://yandex.ru/support/forms/en/create-task#setup).

# Troubleshooting

To check for errors that occur during the form integration:

1.  Open the form where the integration is incomplete or doesn't work as expected.

2.  Go to the **Integrations** tab and click **Completed integrations**.

3.  Check the list for error messages related to your integration.

4.  After resolving the problem, try [creating an issue again](https://yandex.ru/support/forms/en/notifications-history#status).

5.  If the problem persists, [contact support](https://yandex.ru/support/forms/en/feedback).

The error may be caused by invalid data being sent from the form to the **Author**, **Assignee**, or **Followers** issue field. Fill in these fields in the following way:

-   To add an employee manually, enter a username like `smith`.

-   To add an employee specified in an answer to a People,, insert a **Question answer option ID** [variable](https://yandex.ru/support/forms/en/vars) in the field. If you use an **Answer to question** variable, integration won't work.

-   To add an employee specified in an answer to a Drop-down list or Multiple answers question, set usernames (e.g., `smith`) as answer options and use the **Answer to question** [variable](https://yandex.ru/support/forms/en/vars).

If there is an error in the **Author** field even though the field is populated correctly, make sure the user filling out the form is [authorized to create issues in the specified Yandex Tracker queue](https://yandex.ru/support/forms/en/create-task#access).

## Error: No rights to add issues to queue

This error occurs because the user who filled out the form doesn't have the rights to create issues in the specified Yandex Tracker queue. Ask the queue owner to [check access rights](https://yandex.com/support/tracker/manager/queue-access.html).

## The issue description displays incorrectly

Check your YFM markup for errors if you used it to format the text in the **Description** field. To see how your marked-up text will appear, paste it into an issue description in Yandex Tracker or onto a Wiki page.

For example, the text may display incorrectly if there is no empty line before a block element (such as `{% note %}`) or if extra spaces are added after closing an HTML block (`:::` ). For more information about markup, see [Yandex Tracker Help](https://yandex.com/support/tracker/user/syntax-yfm.html).