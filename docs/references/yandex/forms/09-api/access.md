---
source: https://yandex.ru/support/forms/en/api-ref/access
title: "Accessing the Yandex Forms API |"
word_count: 638
token_estimate: 1303
extracted: "2026-05-22T18:06:45Z"
mode: quality
---

API requests are made on behalf of a user. To perform actions through the API, the user on whose behalf the request is made must have the appropriate permissions in Forms. For example, if the user does not have permission to retrieve form responses, the corresponding API requests will be unavailable.

The Yandex Forms API is available to Yandex Forms for Business users. For more information, see [About Yandex Forms for Business](https://yandex.ru/support/forms/en/go-to-forms#business-features).

To access the Yandex Forms API, you can use one of these authorization methods:

-   OAuth 2.0 protocol — can be used in both Yandex 360 for Business and Yandex Cloud Organization organizations. For more information, see [Accessing the API via OAuth 2.0](https://yandex.ru/support/forms/en/api-ref/access#about_OAuth).

-   IAM token — can only be used in Yandex Cloud organizations. For more information, see [Accessing the API with an IAM token](https://yandex.ru/support/forms/en/api-ref/access#iam-token).

You cannot use a Yandex Cloud [service account](https://yandex.cloud/en/docs/iam/concepts/users/service-accounts) for authorization in the Yandex Forms API. Send requests only from a user account.

In requests, specify these headers:

-   `Host: api.forms.yandex.net`

-   Authorization header:

    -   `Authorization: OAuth <OAuth-token>` — when using the OAuth 2.0 protocol.

    -   `Authorization: Bearer <IAM-token>` — when using an IAM token.

-   Organization ID:

    -   `X-Org-Id` — for a Yandex 360 for Business organization.
    -   `X-Cloud-Org-Id` — for a Yandex Cloud Organization organization.

> Example:
>
> ```
> Host: api.forms.yandex.net
> Authorization: OAuth y0__xAbc*********
> X-Org-Id: 1234******
> ```

# Accessing the API via OAuth 2.0

If you are using a federated account, authorize using an [IAM token](https://yandex.ru/support/forms/en/api-ref/access#iam-token).

To get a token:

1.  Click the link [https://oauth.yandex.com](https://oauth.yandex.com/).

2.  On the **Your apps** page, click **Create**.

3.  In the window that opens, select **For API access or debugging** and click **Go to creation**.

4.  Enter the app name and your contact email.

5.  Add permissions for accessing user data. To select a permission, start typing its name in the **Permission name** field:

    -   **Editing form settings (forms:write)** — all operations with data: creation, deletion, and editing.
    -   **Viewing form settings (forms:read)** — reading only.
6.  Click **Create app**.

7.  In your [Yandex OAuth](https://oauth.yandex.com/) account, select the previously created application and copy its ID from the **ClientID** field.

8.  Generate a link to request a token:

    ```
    https://oauth.yandex.ru/authorize?response_type=token&client_id=<application_ID>
    ```

9.  Log in to the account you will use to work with the API, then follow the generated link.

    A sequence of characters will appear on the page — this is your OAuth token. Copy and save it.

See how to set up your app in Yandex ID Help:

-   [How to create an OAuth app for accessing the API](https://yandex.com/dev/id/doc/en/access).
-   [How to obtain a token](https://yandex.com/dev/id/doc/en/tokens/debug-token).

To check if you have access to the API, send any request. If access has not been granted, the request will return a response with code `401 Unauthorized`.

For example, to retrieve information about the current user with curl:

Unix

Windows

```
curl -X GET 'https://api.forms.yandex.net/v1/users/me/' \
     -H 'Authorization: OAuth y0__xAbc******' \
     -H 'X-Org-Id: 1234******'
```

```
curl -X GET "https://api.forms.yandex.net/v1/users/me/" ^
     -H "Authorization: OAuth y0__xAbc******" ^
     -H "X-Org-Id: 1234******"
```

# Accessing the API with an IAM token

If you are using Forms as part of a Yandex Cloud organization, you can authorize with the API using an IAM token.

An IAM token is a unique sequence of characters issued to a user after authentication. The user uses this token to authorize with the Yandex Forms API and perform operations on resources. For more information about this authentication method, see the [documentation of the identity and access management service](https://yandex.cloud/en/docs/iam/concepts/authorization/iam-token).

-   [How to get an IAM token for a Yandex account](https://yandex.cloud/en/docs/iam/operations/iam-token/create)

-   [How to get an IAM token for a federated account](https://yandex.cloud/en/docs/iam/operations/iam-token/create-for-federation)

The IAM token is valid for no more than 12 hours and is limited by the cookie lifetime for the [federation](https://yandex.cloud/en/docs/organization/concepts/add-federation). When the token expires, the `401 Unauthorized` error is returned.