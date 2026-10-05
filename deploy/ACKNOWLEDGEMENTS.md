# Notice acknowledgements and history

Shared state: ~/.local/state/inxs-dashboard/acknowledgements.sqlite3 on Linux. Both the LAN dashboard and authenticated Vercel bridge use this database. The bridge service needs ReadWritePaths for that directory; create it owned by damato, mode 0700, before starting the service. Keep the database in machine backups.

POST /api/acknowledgements observes notices or acknowledges a specific occurrence. Vercel requires a valid password session and same-origin POST, then forwards using the private origin bearer token. The LAN dashboard also requires same-origin POST. Scheduler records are never altered.

A job identity includes job ID, last-run timestamp, result and sanitized failure cause. A new failed run cannot inherit an old acknowledgement. Complete successful source checks mark absent notices no longer reported, retaining their history; recurrence creates a fresh occurrence. Partial data checks never clear unseen notices. Technical verification is a separate record keyed to that failed run. All stored notices are retained; the UI shows the latest 100 in a collapsed history.

Checks: npm test; cd deploy && python3 -m unittest test_acknowledgements.
