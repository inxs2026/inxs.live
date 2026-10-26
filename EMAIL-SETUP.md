# INXS Mail

`https://inxs.live/email` is protected by the existing workspace login. Every
signed-in workspace user can access the connected mailboxes. Gmail accounts are
connected individually; there is no application account-count cap. This first
implementation supports personal Gmail accounts. Other providers need their own
adapters and authorization before they can be added.

The Daily Briefing top bar links to Mail and checks total unread inbox messages
every two minutes while the page is visible. Unknown, disconnected, and failed
counts are explicit; they are never displayed as zero unread.

## One-time Google setup

1. In Google Cloud Console, create/select a project for INXS Mail. Enable the
   Gmail API. A Gmail API OAuth client does not require buying a Cloudflare plan.
2. Configure Google Auth Platform branding and external audience for personal
   use. Use a support/contact email you control. Restrict initial test access to
   `lexiinxs@gmail.com`. Add `https://www.googleapis.com/auth/gmail.modify` under
   Data Access. This scope permits reading, organizing, and sending messages.
3. Create an OAuth client of type **Web application**. Add this exact authorized
   redirect URI: `https://inxs.live/email/oauth/callback`.
4. Download the client JSON. Transfer it privately to the Linux PC at
   `/home/damato/.config/inxs-dashboard/gmail-oauth.json`. Keep its owner as
   `damato`, permissions `0600`, and its parent directory `0700`. The standard
   downloaded `{"web": {...}}` format is supported. Do not commit it or paste its
   client secret into chat. The server reloads this file per connection request;
   no restart is needed after adding it.
5. Open Mail and choose **Connect with Google**. Sign in as `lexiinxs@gmail.com`
   and approve the Gmail permission. The redirect must return to INXS in the
   same browser and existing workspace session within ten minutes.
6. Confirm actual inbox reads. A human should send one intended test message to
   an address they control and confirm its delivery before declaring send/receive
   fully connected. Fixture tests do not establish real email delivery.

Google external apps in Testing can receive refresh tokens that expire after
seven days when Gmail scopes are requested. Choose the Google publishing and
verification status appropriate for personal use before relying on this daily;
follow Google’s console requirements rather than promising indefinite testing
tokens or bypassing account warnings. No billing or paid plan is enabled by this
repository. Adding the app to a different provider is separate from configuring
Gmail; adding a custom sender address also requires its own valid sending setup.

## Security and storage

The Vercel function authenticates every Mail page/API request and rejects mail
writes without a matching Origin and JSON body. Only named endpoints are
forwarded to the existing bearer-authenticated Linux bridge. OAuth uses a
single-use, ten-minute state, bound to the dashboard session, plus PKCE and an
exact callback. Tokens are validated against the intended Gmail account and
requested scope before saving. Tokens/client secrets are never included in
browser assets or status results.

State is in `~/.local/state/inxs-dashboard/mail/mail.sqlite3` (0600, directory
0700). It contains mailbox connection tokens and send idempotency results; it
does not store message bodies. Protect this directory like a password store.
The existing systemd bridge can write to this location under its current
sandbox. Do not include it in public backups.

Messages render as escaped plain text, including HTML-only messages converted to
text. Remote images/scripts are never loaded. Attachment upload/download limits
are 2 MB per message due to the hosting proxy; larger attachments can be opened
in Gmail. Drafts are view-only. Compose is not autosaved; closing it loses the
unsent text. No mail is sent by setup or automated tests.

Sending uses a per-compose idempotency key. An uncertain failure is not retried
automatically: check Gmail Sent before composing a replacement. Disconnect
removes local saved tokens, not the Gmail account/messages. Google-side access
can also be revoked at https://myaccount.google.com/connections.

## Checks

`npm test`

`python3 -m unittest discover -s deploy -p test_mail.py`

The bridge should be restarted after changing `deploy/inxs_mail.py` or
`deploy/dashboard_bridge.py`. Existing camera workers are on-demand and can
restart after a bridge restart.

Primary references:

- https://developers.google.com/identity/protocols/oauth2/web-server
- https://developers.google.com/workspace/gmail/api/auth/scopes
- https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/send

## Public OAuth branding links

Homepage: https://inxs.live/mail-info

Privacy policy: https://inxs.live/privacy

Terms of use: https://inxs.live/terms

Authorized domain: inxs.live

These static information pages and their exact stylesheet path are accessible
without login. The root Daily Briefing, /email, all Mail APIs, and all other
workspace routes still require authentication. Domain ownership verification,
Google publishing, and any requested Google verification remain console tasks.
Publishing does not update an already-issued Testing grant: reconnect the same
Gmail account from Add Gmail after changing to In production.

## Moving messages to Trash

The message reader's Delete button calls Google's recoverable message-trash
endpoint through the existing session- and origin-protected modify route.
It uses the already authorized gmail.modify scope. No permanent-delete API
is exposed. Successful moves refresh the current message list and show a
status message. Errors leave the message in the reader and show the failure.
Restore a deleted message using Gmail's Trash. Drafts remain view-only here.
