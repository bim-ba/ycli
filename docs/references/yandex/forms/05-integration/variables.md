---
source: https://yandex.ru/support/forms/en/vars
title: "Variables in action settings |"
word_count: 857
token_estimate: 2589
extracted: "2026-05-22T18:00:39Z"
mode: quality
---

When you set up integration of your form with other services, you can send answers or other data from the form to the service. For example, you can insert the user's answers into the body of an email or insert data into issue fields in Yandex Tracker.

To do this, use variables:

1.  In the **Integration** tab of your form, [add an action](https://yandex.ru/support/forms/en/notifications#add-integration).

2.  Select the field and click on the right.

3.  In the list, select a variable to add to the field.

4.  If using variables like **Answer to question**, **Question answer option ID** or similar, you can choose a [filter](https://yandex.ru/support/forms/en/vars#var-filters) for the variable values if needed.

5.  Click **Save**.

When data is sent to the service, the variable is automatically converted to a value: an answer to a question, test result, or technical data.

When [integrating your form with Yandex Tracker](https://yandex.ru/support/forms/en/create-task), you can add the employee specified in an answer to a People question to the **Author**, **Assignee**, and **Followers** fields in Yandex Tracker. To do so, add a **Question answer option ID** variable to the field. If you use an **Answer to question** variable, integration won't work.

> For example, here's the text of an email containing all the user's answers to the form's questions.
>
> ![](https://yandex.ru/support/forms/docs-assets/support-forms/rev/r19697197/en/_assets/variables-example-new.png)

# Filters

If integration settings contain answers to questions added using variables, errors may occur if the answers do not match the format required for integration. For example, if you add an answer to a Long text question to the HTTP request body, and this answer contains line breaks, integration will not work.

To avoid data format errors, use the following filters for variables:

-   **Sanitize string**: Remove special characters from the answer.

-   **JSON**: Convert the answer to a JSON-compatible format.

-   **base64**: Convert the answer to ASCII encoding.

# Formatting answers

If you're using an **Answers to questions** variable in the integration settings, you can select the format of the answer list.

-   **Plain text** shows the data as Question - Answer pairs.

-   **Old format** shows answers as `%% Answer %%`.

-   **New format** embeds answers within a code block.

-   **JSON** shows answers as `"key": "value"` pairs.

To send answers to Tracker or Wiki, we recommend using the **New format** option. For more information about YFM markup, see [Wiki Help](https://yandex.com/support/wiki/wysiwyg/text-format.html).

# Variable reference

You can use the following variables in action settings:

| Variable | Description |
| --- | --- |
| **User info** | Personal data of the user who completed the form.<br>Variables from this group are only converted into the user's personal data if the form was created in [Forms for Business](https://yandex.ru/support/forms/en/go-to-forms#business-features) mode and completed by an employee of the organization. You can only get data from external users if they provide it in answers to the form's question. |
| Name | User's name. |
| Username | User's username. |
| Email | User's email. |
| Gender | User's gender. |
| Department | Employee's department (for [Yandex Forms for Business](https://yandex.ru/support/forms/en/go-to-forms#business-features) users). |
| Phone | Employee's work phone number (for [Yandex Forms for Business](https://yandex.ru/support/forms/en/go-to-forms#business-features) users). |
| Manager | Employee's direct supervisor (for [Yandex Forms for Business](https://yandex.ru/support/forms/en/go-to-forms#business-features) users). |
| Team | Employee's teams (for [Yandex Forms for Business](https://yandex.ru/support/forms/en/go-to-forms#business-features) users). |
| **Company details** | Information from the organization's address book in Яндекс 360 для бизнеса. |
| Information from the answer to the question | For questions of the **People**, **Departments**, and **Teams** type, this variable is one of the fields from the employee's or department's card specified in the answer. |
| User information | One of the fields of the card of the employee who filled out the form. |
| **Test results** | [Test or quiz](https://yandex.ru/support/forms/en/tests) results. |
| Maximum test points | Maximum number of points one can score in the test. |
| Total questions with points | Number of question one can score points for. |
| Points scored | Number of points scored by the user. |
| Test results heading | [Header of the segments](https://yandex.ru/support/forms/en/tests#test-result) the user's result fits into. |
| Description of test results | [Description of the segment](https://yandex.ru/support/forms/en/tests#test-result) the user's result fits into. |
| Points scored for a question | Number of points scored for a selected question. |
| **Form** | Form parameters and answers to the form's questions. |
| Form ID | Unique form ID. |
| Name. | Form name. |
| Answer to question | User answers to a specific question in the form: select the question and set up [filters](https://yandex.ru/support/forms/en/vars#var-filters). Only the answers to the question you selected are passed to this variable. |
| Answers to questions | User answers to multiple questions: select the questions and set up [filters](https://yandex.ru/support/forms/en/vars#var-filters) and [question formatting](https://yandex.ru/support/forms/en/vars#formatting-responses). The selected questions and the answers to them are passed to this variable as Question : Answer pairs. |
| Answers to questions in JSON | User answers to multiple questions: select the questions and set up [filters](https://yandex.ru/support/forms/en/vars#var-filters). The selected questions, the answers to them, and the information about the form (ID, creation date, and other parameters) are passed to this variable in [JSON](https://en.wikipedia.org/wiki/JSON) format. This format can be useful when working with [HTTP requests](https://yandex.ru/support/forms/en/send-request). |
| Response ID | Unique ID of the completed form. |
| Question answer option ID | Unique ID of an answer option for multiple-choice questions (such as "People" or "Drop-down" list). |
| Response date | Date when the form was submitted. |
| Form author's email | Email of the user who created the form. |
| **Browser** | User's browser and operating system info. |
| OS family | Operating system type. |
| OS name | Operating system name. |
| OS version | Operating system version. |
| Browser name | Name. |
| Browser version | Version. |
| **Request** | Technical parameters of the HTTP session. |
| Host | Domain name of the server the request came from. |
| URL | Form's address. |
| All GET parameters | Values of all request parameters.<br>[How to use GET parameters to pre-fill a form](https://yandex.ru/support/forms/en/get-params) |
| GET parameter | Value of a specific request parameter (specify the parameter name).<br>[How to use GET parameters to pre-fill a form](https://yandex.ru/support/forms/en/get-params) |