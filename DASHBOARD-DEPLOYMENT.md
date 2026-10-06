# INXS dashboard deployment

`web/index.html` is the Daily briefing homepage. The automation overview is
at `/dashboard` (`web/dashboard.html`); `/briefing` remains a compatible alias. `web/tools/index.html` preserves the
former INXS homepage and its tool links. Invoice, mortgage, LeaseScan and
LeaseCreate remain at their existing URLs; media tool subdomains remain linked.
All paths on this Vercel project go through `api/site.js` before serving a file.

The existing `/home/damato/Projects/Dashboard` user service still supplies live
Linux schedules, saved reports and health checks. It is not suitable for running
inside Vercel because it reads local services, databases and report files.
`deploy/dashboard_bridge.py` binds only to loopback port 8089, allows only known
read-only Dashboard data/report endpoints, and requires a random bearer token.
Tailscale Funnel forwards HTTPS traffic to that authenticated bridge. It does
not expose the unauthenticated LAN Dashboard on port 8088.

Vercel production and preview environment variables:

- `DASHBOARD_PASSWORD_HASH`: 16-byte hexadecimal salt, colon, and the hex result
  of PBKDF2-HMAC-SHA256 with 210000 iterations and 32 output bytes.
- `DASHBOARD_SESSION_SECRET`: random secret with at least 32 characters.
- `DASHBOARD_ORIGIN`: HTTPS origin of the authenticated Linux bridge.
- `DASHBOARD_ORIGIN_TOKEN`: the bridge's independent random bearer token.

No password or secret is checked into this repository. Authentication fails
closed if its environment is absent. Password changes require a new hash and
session secret followed by redeployment; this invalidates existing sessions.
Cookies are signed, expire after 12 hours, and are HttpOnly, Secure and SameSite.
Authenticated responses disable browser and CDN caching. Sign out is available
on every Dashboard page. Login has instance-local attempt throttling; stronger
global abuse controls can be added through the hosting provider if needed.

Run `npm test` for authentication, routing, file isolation, origin forwarding,
query preservation and existing tool-page checks. The Linux machine must remain
awake and online for live data and reports; the Vercel pages and tools page are
still served if the origin is unavailable, with API requests reporting an error.

The tools' own external subdomains are separate deployments. This project's
password does not change authentication on those subdomains.

Browser assets are packaged by `scripts/package-web.cjs` during npm installation.
The gzip JSON bundle is included in the function so Vercel does not transpile
browser ES modules. The original editable frontend remains under `web/`.


## Cameras

The authenticated `/cameras` page has a six-camera grid and a single-camera selector.
The bridge imports `deploy/cameras.py` and serves only `/api/cameras` and fixed
`/camera-stream/[1-6]/index.m3u8` / `segment_<number>.ts` paths. Credentials never
appear in API responses or browser assets. All reads require the existing INXS
session and bridge bearer token; CDN caching remains disabled.

Store recorder credentials in `~/.config/inxs-dashboard/cameras.json` with mode
0600, containing `host`, `username`, `password`, and a six-element `channels`
array. The host is restricted to `10.0.0.105`. Never commit this file.

FFmpeg converts the recorder substreams to muted H.264 HLS at 640 pixels wide,
10 fps, approximately 350 kbit/s per camera. Safari uses native HLS; other
supported browsers use the vendored hls.js 1.7.3 library (BSD license alongside
its asset). Opening one camera uses that same feed at a larger display size.
The relay retains a short rolling buffer rather than recordings. Workers stop
90 seconds after the last view and restart on demand. Rejected logins stop
retrying until the credential file changes. FFmpeg diagnostics are discarded
after classifying authentication failures, so credentials are not logged.

The existing bridge service has write access only to its private state folder.
Restart `dashboard-bridge` after changing relay code. Confirm actual video on
all six channels before reporting the feature connected. Tests:
`python3 -m unittest discover -s deploy -p test_cameras.py` and `npm test`.
