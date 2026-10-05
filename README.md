# INXS.live

The password-protected Daily briefing is the main Vercel page. The automation
overview remains available at `/dashboard`. Its homepage and
assets are in `web/`; the former homepage is preserved at `/tools`. Invoice,
mortgage, LeaseScan and LeaseCreate keep their existing paths, and the media
services keep their subdomain links.

All website requests pass through `api/site.js`, including HTML, scripts, data
APIs and PDF reports. Live Dashboard data comes from the existing Linux service
through the authenticated loopback bridge in `deploy/dashboard_bridge.py`.

See [DASHBOARD-DEPLOYMENT.md](DASHBOARD-DEPLOYMENT.md) for deployment, environment
variables, password rotation and the Linux availability requirement.

## Structure

- `web/` — Dashboard frontend, tools directory and browser tools
- `api/site.js` — password login, signed sessions, file serving and data proxy
- `apps/` — existing media service applications
- `deploy/` — existing media stack and authenticated Dashboard bridge
- `tests/site.test.cjs` — authentication, protected routes and proxy checks

Run `npm test` to check the website routing and authentication.
