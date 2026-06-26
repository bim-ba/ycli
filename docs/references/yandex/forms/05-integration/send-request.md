---
source: https://yandex.ru/support/forms/en/send-request
title: "Sending an HTTP request |"
word_count: 937
token_estimate: 1624
extracted: "2026-05-22T17:59:24Z"
mode: quality
---

For HTTP requests to work correctly, allow your service to accept packets from the Yandex Forms `2a02:6b8:c00::/40` network. Otherwise, the firewall of your service may block form submissions.

The integration works only with IPv6. Yandex Forms doesn't support HTTP requests that originate from IPv4 addresses.

To send data from your form to a web service via the API, use HTTP requests:

1.  Select the desired form and open the **Integration** tab.

2.  Select the [group of actions](https://yandex.ru/support/forms/en/notifications#add-integration) to which you want to add an HTTP request, then click the button with the desired **API** request type:

    -   [JSON-RPC POST request](https://yandex.ru/support/forms/en/send-request#json-request): Send a request using the JSON-RPC protocol.

    -   [Request with a set method](https://yandex.ru/support/forms/en/send-request#any-request): Send any available form data with the option to set the request format and select the HTTP method.

    All requests are executed asynchronously.

3.  Enter the URL of the service: Address of the node that provides the API.

4.  Set parameters that depend on your selected request type:

    -   Request JSON-RPC POST

        -   Specify the service method that the request is sent to.

        -   Specify the request parameters. Specify a name and value for each parameter.

        -   You can use [variables](https://yandex.ru/support/forms/en/vars) as parameter values. If you choose to do so, enable **Send if value is set**.

    -   Request with a set method

        -   Select the HTTP method.

        -   Set the request body: specify the parameters to be sent in JSON format. To add the data from the form to the request body, use [variables](https://yandex.ru/support/forms/en/vars).

        -   Add headers to the request. Specify a name and value for each header.

        -   You can use [variables](https://yandex.ru/support/forms/en/vars) as header values. If you choose to do so, enable **Send if value is set**.

5.  Click **Save**.

> Example: Create a project in Yandex Tracker with a specified name.
>
> Create a request to the [Yandex Tracker API](https://yandex.com/support/tracker/about-api.html) by filling out the form as follows:
>
> -   **URL** — `https://api.tracker.yandex.net/v3/entities/project`.
>
> -   **Request method** — `POST`.
>
> -   **Request body**: Project parameters in JSON format:
>
>     ```
>
>         {
>             "fields":{
>                 "summary": "New Project"
>             }
>         }
>     ```
>
> -   **Headers**:
>
>     -   `Authorization` — `OAuth <OAuth_token>`\>
>     -   `X-Org-ID: <organization_ID>`
>
> For more information about creating projects using Yandex Tracker API requests, see [Yandex Tracker Help](https://yandex.com/support/tracker/concepts/entities/create-entity.html).
>
> ![](https://yandex.ru/support/forms/docs-assets/support-forms/rev/r19697197/en/_assets/request-example-new.png)

# Processing responses to HTTP requests with a set method

**Successful request**

A request is considered successful if you get a response with code `200`, `201` or `202`.

**Handling errors**

If the following errors occur, the request is sent again (up to seven attempts in 30 minutes):

-   Request expires in 5 seconds.

-   Network error.

-   Response with `5XX` code.

-   Response with `404` code.

Any other errors cause the integration to fail.

**Redirect**

If the received response has the `307` code, the request is redirected to the URL that's specified in the `Location` header.

# Processing responses to a JSON-RPC POST request

**Successful request**

The request is considered successful if there are no errors from the list below.

**Redirect**

If the received response has the `307` code, the request is redirected to the URL that's specified in the `Location` header.

**Handling errors**

Errors are processed as follows:

1.  If there's no response due to a network error or because the request expired, the request is sent again.

2.  The response body is checked. If there's an error in the response body, the request is sent again after any error code, except:

    -   `-32700` Parse error

    -   `-32600` Invalid Request

    -   `-32602` Invalid params

3.  If the response body has no errors, the HTTP status code is checked. The request is sent again after responses with `5XX` and `404` status codes.

Any other errors cause the integration to fail.

# Troubleshooting

To check for errors that occur during the form integration:

1.  Open the form where the integration is incomplete or doesn't work as expected.

2.  Go to the **Integrations** tab and click **Completed integrations**.

3.  Check the list for error messages related to your integration.

4.  After resolving the problem, try [creating an issue again](https://yandex.ru/support/forms/en/notifications-history#status).

5.  If the problem persists, [contact support](https://yandex.ru/support/forms/en/feedback).

## Two HTTP requests are sent per response in the form

In some cases, the HTTP request module doesn't wait for the external service to respond that the request is accepted. If so, the request is sent again and the service receives a duplicate request with the same data. If you want to track the uniqueness of HTTP requests, use the `x-delivery-id` header value.

## Variable data is inserted in an incorrect format

If you use [variables](https://yandex.ru/support/forms/en/vars) to add data from your form to a request, invalid characters may get into the request body and cause an integration error. To remove invalid characters from an answer or convert it into a different format, set up [filters for variables](https://yandex.ru/support/forms/en/vars#var-filters).

Let's say a variable with an answer to a question of the Long text type needs to be added to the request body. If the answer text contains linebreaks, integration will fail. To avoid this, convert the value of a variable to JSON format.

To do so, select the **JSON** filter when adding a variable.

## 400 Client Error: Bad request

If the integration failed with 400 Client Error: Bad request, check the URL and the request body for typos, such as odd line breaks, non-breaking spaces, and escaped characters. The request body must be in JSON format.

## An error occurred while establishing a proxy connection

This error may occur if the request is sent to an address belonging to a service banned in Russia.