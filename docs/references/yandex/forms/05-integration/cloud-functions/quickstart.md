---
source: https://yandex.ru/support/forms/en/call-function
title: "Invoking a Cloud Functions function |"
word_count: 615
token_estimate: 1222
extracted: "2026-05-22T17:59:35Z"
mode: quality
---

You can integrate a form with a [Cloud Functions function](https://yandex.cloud/en/docs/functions). For example, you can collect user data and transfer it to a website or database to register customers using the form.

# Step 1. Create a service account

1.  Go to the [Yandex Cloud management console](https://console.cloud.yandex.com/).
2.  In the left-hand panel, select the folder to create a function in.
3.  In the top-right corner, click → **Create service account**.
4.  In the service account creation window, fill in the following fields:
    1.  **Name**; it may only contain lowercase Latin letters, numbers, and hyphens.
    2.  **Description**; it may contain any characters.
    3.  In the **Roles in folder** field, add the `functions.functionInvoker` role.
5.  Tap **Create**.

If no billing account is linked to your Yandex Cloud account, a window for creating a billing account will open. Fill in its fields to create an account. For more information, see [{#T}](https://yandex.cloud/en/docs/getting-started/individuals/registration#new-account)

# Step 2. Create a service account key

1.  In the left-hand panel of the [management console](https://console.cloud.yandex.com/), select the folder where the appropriate service account is located.
2.  Go to the **Service accounts** tab.
3.  Select the account you need.
4.  In the top panel on the account page, click **Create new key** → **Create API key**.
5.  Provide a brief description for the key.
6.  Tap **Create**.
7.  This will open a window with the key ID and the secret key. Store them in a secure place. You will not be able to access them after you close the window.

# Step 3. Enable cloud function invocation

1.  In Yandex Forms, open the form for which you need to set up integration with a cloud function.
2.  Go to the **Settings** tab and select **Additional** in the left panel.
3.  Under **Cloud function key**, fill in the **Key ID** and **Secret key** fields. Paste the values you copied when creating the service account key there.
4.  Click **Save**.

# Step 4. Create a cloud function

1.  Go back to the [Yandex Cloud management console](https://console.cloud.yandex.com/).
2.  In the left-hand panel, click and select Cloud Functions.
3.  In the top-right corner, click **Create function**.
4.  On the function creation page, fill in the following fields:
    1.  **Name**; it may only contain lowercase Latin letters, numbers, and hyphens.
    2.  **Description**; it may contain any characters.
5.  Select the programming language that your function will be written in.
6.  Select a tab with the function source:
    -   **Code editor** to write the function code directly in it.
    -   **Object Storage** to select a bucket and object with the appropriate function.
    -   **ZIP archive** to attach a `.zip` file with the appropriate function.
7.  You can optionally set up the function parameters and logging. All parameters required for creating a function are preset.
8.  Click **Save changes**.
9.  On the function page, copy the value from the **ID** field.

To learn more about creating cloud functions, see the [documentation for cloud functions](https://yandex.cloud/en/docs/functions/quickstart/create-function/index).

# Step 5. Set up integration

1.  Go back to the form and click the **Integrations** tab.
2.  Select a group of actions to set up issue creation in and click Cloud Functions at the bottom of the group.
3.  In the **Function code** field, paste the function ID that you copied in the previous step.
4.  Under **Parameters**, you can optionally select additional parameters to be transferred to the function.
5.  Click **Save**.

Responses to the form will be delivered in JSON format. See its structure below:

```
{
	"id":<form_response_ID>,
	"uid":"<user_ID>",
	"data":{
		"<question_ID_with_its_type_specified>":{
			"value":<answer_to_question>,
			"question":{
				"id":<question_ID>,
				"slug":"<question_ID_with_its_type_specified>",
				"options":{
					<question_parameters>
				},
				"answer_type":{
					"id":<question_type_ID>,"slug":"<question_type>"
				}
			}
		}
	}
,"survey":{
	"id":"<form_ID>"
	},
"created":"<response_date>",
"cloud_uid":"<user_ID>"
}
```

You can view the sent request and the function execution results on the [completed integrations](https://yandex.ru/support/forms/en/notifications-history) page.