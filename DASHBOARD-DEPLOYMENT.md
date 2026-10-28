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


## Sports

`/sports` follows Daily briefing in the shared navigation. The briefing contains
weather and Canadian/U.S. news; Sports has scoreboards for NHL, MLB, and NFL,
Today/Yesterday/Tomorrow shortcuts, and a date picker spanning 2000-2099. Future
empty feeds are labeled as having no games listed yet, and failed league feeds
are distinguished from empty schedules. Standings show the current season
independently of the chosen game date. Season years are explicit to avoid
upstream defaults selecting a future MLB season.

The authenticated bridge forwards `/api/sports-scores?date=YYYY-MM-DD` and
`/api/sports-standings?league=NHL|MLB|NFL` to Dashboard. The `sports_page.py`
module caches today's scores for a minute, other dates and standings for ten
minutes, and labels retained data stale after a failed refresh. Existing ESPN
team branding is reused. The LAN Sports navigation redirects to the protected
INXS.live page. Verify with `npm test` and
`python3 -m unittest discover -s deploy/dashboard -p test_sports_page.py`.

## Combined Dashboard (October 27, 2026)

Dashboard now contains Today's workflows, All schedules, and Health & backups
views under a single page header. The health view includes services, Codex usage,
Linux storage/uptime/maintenance, and all backup checks. The former Health rail
entry is removed from all pages. /health and /health.html redirect authenticated
requests to /dashboard#health-backups; direct links from Briefing go there too.
Sidebar typography, artwork, spacing, and width are reduced proportionally.
The nine phone navigation links use a balanced five/four layout in two rows.

## Woodbine Claims (October 28, 2026)

`/woodbine-claims` is a protected workspace page, linked after Woodbine Stats on
all ten shared navigation rails. Phone navigation uses two balanced rows of five.
The compact latest-card report appears first; all current-year claims follow in
descending date and ascending race/program order. Horse/race names are blue,
previous connections red, and new connections green. There is no horizontal table.

`/api/woodbine-claims` is served directly by the authenticated bridge using
`deploy/claims_api.py`. It accepts only the current year's complete and balanced
snapshot, and marks failed or overdue scheduled refreshes stale. Snapshot state
is under `~/.local/state/inxs-dashboard/claims/`; no claim records or credentials
are packaged in public browser assets. Requests without a session receive 401.

`deploy/claims/` retains the chart parsers, year-specific calendar, update wrapper
and systemd unit definitions. The installed user timer runs at 15:00, 16:00, ...
23:00 on Thursday-Sunday, plus 00:00 Friday-Monday as the final check of the
preceding race day. All calendar expressions use America/Toronto explicitly.
Catch-up outside these windows is disabled. A one-time initial refresh verified
209 claims, C$3,993,000, across 98 completed cards and four cancelled cards through
October 25, 2026. The last complete snapshot is retained on any failed update.

The annual parser caches official Equibase charts, rechecks the latest three
charts and the published results calendar, and checks race/count coverage.
New connections are extracted from their PDF columns individually so wrapped
trainer surnames and voided-claim annotations do not contaminate owner names.
For a new year, install a validated year-specific racing calendar.

Checks: `npm test`,
`python3 -m unittest discover -s deploy -p test_claims_api.py`, and the standalone
parser regression suite supplied with the report package. The LAN route redirects
to the protected INXS page. No Mac Mini or Pi changes were made.

### Grouped Woodbine navigation

Woodbine Racing, Woodbine Stats and Woodbine Claims now live under a single
Woodbine disclosure button on every INXS workspace page. The active child and
parent retain their selected style. The dropdown supports click, outside-click
closing, Escape and arrow-key entry. Eight top-level navigation items use a
balanced four/four phone layout; the three child links open above the phone rail.
