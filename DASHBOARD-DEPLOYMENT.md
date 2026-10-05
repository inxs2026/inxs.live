# INXS dashboard deployment

`web/index.html` is the Dashboard homepage. `web/tools/index.html` preserves the
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
