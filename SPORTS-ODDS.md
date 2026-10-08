# Sports odds

Game cards read the public ScoresAndOdds NHL, MLB and NFL boards through the
Linux backend. Prices are the source's listed American odds, which may combine
sportsbooks; they are not OLG or theScore prices. The page checks once per minute
while visible, and again when returning to it. Provider publication delays can
still apply. Each card includes its source link and retrieval time.

The existing authenticated sports-scores endpoint carries odds; no new public
endpoint or credentials are required. Deploy sports_odds.py alongside server.py
and sports_page.py to /home/damato/Projects/Dashboard and restart the dashboard
user service. The Vercel frontend deploys from main.

Matching requires both home/away abbreviations and the scheduled start within
45 minutes. Ambiguous matches show no prices. Past and completed games show no
live odds. Failed odds reads or stale score responses hide prices. Games with
no posted markets remain visible with an explicit unavailable/not-posted label.

Tests: npm test; python3 -m unittest discover -s deploy/dashboard -p 'test_sports*.py'.

Rollback baseline: Git tag before-olg-odds-2026-10-08. An independent source and
backend backup is in /home/damato/Backups/inxs-before-olg-2026-10-08. To undo this
feature, revert its commit, restore the matching backend files and restart the
dashboard user service; reverting just the frontend hides odds but leaves the
backend requests running.
