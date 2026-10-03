---
description: "Get a Yandex OAuth token and your Yandex 360 organization id for ycli: one command, or by hand."
type: how-to
---

# Authenticate

ycli needs two values, read from the environment or from a `.env` file in the working directory:

```bash
YANDEX_ID_OAUTH_TOKEN=...        # a Yandex OAuth token with Tracker, Wiki and Forms access
YANDEX_ID_ORGANIZATION_ID=...    # your Yandex 360 organization id
```

ycli sends the organization id as the `X-Org-Id` header to every service.

## Get a token with `ycli auth login`

Yandex issues OAuth tokens only through a registered application.

1. Register an app at [oauth.yandex.ru](https://oauth.yandex.ru/client/new) and grant it the
   **Tracker**, **Wiki** and **Forms** permissions, read and write. The read permissions alone are
   enough only for `ycli mcp start --read-only`.
2. Put its ClientID, and the Client secret if you want the headless flow, into `.env`:

    ```bash
    YANDEX_OAUTH_CLIENT_ID=...
    YANDEX_OAUTH_CLIENT_SECRET=...    # optional: enables the device flow
    ```

3. Run `ycli auth login`. It gets a token, detects your organization and writes both into `.env`:
    - with a client id and a secret it uses the **device flow**: it prints a code and a
      `https://ya.ru/device` link, you approve there, and it captures the token. This works over SSH;
    - with only a client id, or with `--implicit`, it uses the **browser flow**: it opens the Yandex
      authorization page, you approve and paste the token it shows back.

## Check the credentials

```bash
ycli auth status            # whose token, which organization, which services accept it
ycli tracker auth status    # one service only (also wiki, forms)
ycli doctor                 # every check in order, with what to fix for each one that fails
```

`ycli doctor` also says where each credential is set (the environment or the `.env` file, never its value) and which extras are installed; add `-o json` for an agent. All three exit non-zero when a service rejects the token. The organization's name needs the optional
`directory:read_organization` scope; without it you get the id and a note.

## Do it by hand

Device flow:

```bash
# 1. start the flow: returns a user_code and a verification_url
curl -s -X POST https://oauth.yandex.ru/device/code -d "client_id=$YANDEX_OAUTH_CLIENT_ID"
# 2. open https://ya.ru/device, enter the user_code, approve
# 3. exchange the device_code for the token
curl -s -X POST https://oauth.yandex.ru/token \
  -d grant_type=device_code -d "code=<device_code>" \
  -d "client_id=$YANDEX_OAUTH_CLIENT_ID" -d "client_secret=$YANDEX_OAUTH_CLIENT_SECRET"
```

Browser flow: open `https://oauth.yandex.ru/authorize?response_type=token&client_id=<ClientID>`
in a signed-in browser, approve, and copy the token from the page.

Organization id: [tracker.yandex.ru/admin/orgs](https://tracker.yandex.ru/admin/orgs), your
organization, the identifier field.

## Yandex documentation

| Step | Yandex docs |
|---|---|
| Register the OAuth app | [Registering an app](https://yandex.ru/dev/id/doc/en/register-client) |
| Device flow | [Entering the code on the authorization page](https://yandex.ru/dev/id/doc/en/codes/screen-code-oauth) |
| Browser flow | [Obtain a token manually](https://yandex.ru/dev/id/doc/en/tokens/debug-token) |
| Token and organization header per service | [Tracker](https://yandex.ru/support/tracker/en/api/access) · [Wiki](https://yandex.ru/support/wiki/en/api-ref/access) · [Forms](https://yandex.ru/support/forms/en/api-ref/access) API access |
