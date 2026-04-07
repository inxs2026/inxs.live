# WORKFLOWS - Standard Operating Procedures

**Purpose:** Clear documentation of how things work. Read this before asking Carlo questions.

**Last updated:** February 19, 2026

**Related:** [[TOP-3-PICKS-METHODOLOGY.md]] | [[HEARTBEAT.md]] | [[docs/CRON-JOBS.md]]

---

## 🏇 RACING PICKS WORKFLOW

### WHEN CARLO SENDS DRF (1-2 days before race day)

**I receive:** DRF PDF via Telegram attachment

**I do immediately:**
1. Note the race date from DRF filename/content
2. Create folder: `/home/damato/.openclaw/workspace/racing/YYYY-MM-DD/`
3. Save as: `racing/YYYY-MM-DD/gulfstream_[date]_drf.pdf`
4. Confirm to Carlo: "DRF saved for [date]. Ready for race day."
5. **DO NOT generate picks yet** - wait for race day

### RACE DAY - 11:45 AM (Thu/Fri/Sat/Sun)

**Automated job runs:**

**STEP 1: GET SCRATCHES FIRST**
- Navigate to TrackData.live (login: damatopi)
- Get TODAY'S Gulfstream race card
- Note ALL scratches and changes
- Create scratch list

**STEP 2: ANALYZE ONLY RUNNING HORSES**
- Read TOP-3-PICKS-CRITERIA.md
- Use the DRF already saved in `racing/[today]/` folder
- **SKIP scratched horses entirely** - don't analyze them
- Calculate Beyer averages (last 3 races)
- Follow full methodology: form, class, trainer, pace
- Generate top 3 picks per race with detailed reasoning

**STEP 3: CREATE CLEAN REPORT**
- Field lists show ONLY running horses
- NO "(SCR)" notations - scratched horses don't appear
- Top 3 picks per race with full analysis
- Beyer calculations displayed
- Professional format

**STEP 4: GENERATE & EMAIL PDF**
- Create PDF using browser.pdf
- Save to: `racing/[today]/gulfstream_[date]_picks.pdf`
- Email using script:
  ```bash
  python3 /home/damato/.openclaw/workspace/send_email_pdf.py \
    cdamato@rogers.com \
    "Gulfstream Picks - [Date]" \
    "Your picks are attached. Scratches implemented as of 11:45 AM EST. Good luck!" \
    [path-to-pdf]
  ```
- Verify email sent successfully

### RACE DAY - 8:00 PM (Results)

**Automated job runs:**
1. Check if today's picks exist
2. Get results from TrackData.live or DRF
3. Compare picks vs actual results
4. Calculate: win %, board %, ROI
5. Create results summary markdown
6. Convert to PDF
7. Email PDF to Carlo
8. Brief summary announcement

---

## 📊 STOCK REPORTS WORKFLOW

### AUTOMATED REPORTS

**Schedule:**
- **10:00 AM EST** - Morning report (Mon-Fri)
- **3:00 PM EST** - Afternoon report (Mon-Fri)

**What happens:**
1. Check if TSX market is open (9:30 AM - 4:00 PM, no holidays)
2. If open: Fetch live prices (~15 min delay via yfinance)
3. Calculate portfolio snapshot (average change, gainers/losers/flat)
4. Generate report with:
   - Portfolio snapshot one-liner
   - All 18 stocks with current price, $ change, comment
   - Top gainer/loser summary
5. Send complete report to Carlo via Telegram

**Market closed:** Show "MARKET CLOSED (Last Close)" with previous close prices

### ON-DEMAND REPORTS

Carlo asks "stock report" or "how are my stocks?" → run report immediately

---

## 📅 DAILY BRIEFING WORKFLOW

### AUTOMATED - 7:00 AM EST (Every day)

**What happens:**
1. Run: `python3 morning_briefing_with_reminders.py`
2. Includes:
   - Reminders from `memory/reminders.md` and `memory/active-tasks.md`
   - Live weather (Mississauga & YYZ)
   - Top 3 Canada news headlines
   - Top 3 USA news headlines  
   - Stock market summary (TSX direction, top 3 headlines)
   - Racing schedule (Thu/Fri/Sat/Sun - Gulfstream days)
3. Send to Carlo via Telegram

---

## 🧹 DAILY MAINTENANCE WORKFLOW

### AUTOMATED - 5:00 AM EST (Every day)

**What happens:**
1. Run storage cleanup: `auto_cleanup.sh`
2. Backup important files:
   - memory/ folder
   - Racing analyses (last 30 days)
   - AGENTS.md, SOUL.md, USER.md, TOOLS.md, HEARTBEAT.md
   - Save to: `~/backups/openclaw/YYYY-MM-DD/`
3. Cleanup old backups (keep 4 most recent)
4. Session hygiene check
5. Check workspace size
6. Log summary to `memory/YYYY-MM-DD.md`
7. **Alert Carlo ONLY if:**
   - Workspace >1GB
   - Session >1.5MB  
   - Backup failed

**Silent operation unless problems.**

---

## 📝 WHEN CARLO ASKS FOR ANALYSIS

### General Pattern

1. **Check memory first:** Use `memory_search` for context
2. **Read relevant criteria:** TOP-3-PICKS-CRITERIA.md, CLAIMING-PROSPECTS-CRITERIA.md, etc.
3. **Use appropriate tools:** Browser for data, exec for scripts, etc.
4. **Document as you go:** Update memory files with decisions/learnings
5. **Deliver properly:** PDF via email for racing, Telegram for quick updates

---

## 🔄 FILE ORGANIZATION

### Racing Files
```
/home/damato/.openclaw/workspace/racing/
├── 2026-02-15/
│   ├── gulfstream_feb15_drf.pdf
│   ├── gulfstream_feb15_picks.pdf
│   └── gulfstream_feb15_results.md
├── 2026-02-19/
│   ├── gulfstream_feb19_drf.pdf
│   └── gulfstream_feb19_picks.pdf
```

### Memory Files
```
/home/damato/.openclaw/workspace/memory/
├── YYYY-MM-DD.md (daily logs)
├── active-tasks.md (current work)
├── lessons.md (things learned)
├── self-review.md (weekly reflections)
└── projects.md (long-term ideas)
```

### Scripts
```
/home/damato/.openclaw/workspace/
├── send_email_pdf.py (email with attachments)
├── stock_watchlist.py (stock reports)
├── morning_briefing_with_reminders.py (daily briefing)
├── heartbeat_check.sh (health checks)
└── auto_cleanup.sh (storage cleanup)
```

---

## ❌ WHAT NOT TO DO

**Racing:**
- ❌ Don't generate picks before getting scratches
- ❌ Don't analyze scratched horses
- ❌ Don't include "(SCR)" in final reports - just omit them
- ❌ Don't ask for DRF on race day - it's already saved

**Stock Reports:**
- ❌ Don't send summaries only - send FULL report with all stocks
- ❌ Don't narrate the report - just deliver it

**General:**
- ❌ Don't ask Carlo questions already answered in WORKFLOWS.md
- ❌ Don't duplicate work - check what's already done
- ❌ Don't send half-finished work
- ❌ Don't forget to email when workflow says to email

---

## 🎯 CRITICAL SUCCESS FACTORS

1. **Scratches BEFORE picks** (racing)
2. **Email must work** (verify send, don't assume)
3. **Complete reports** (all races, all stocks)
4. **Proper timing** (11:45 AM for picks, not 12:15 PM scramble)
5. **Clean presentation** (no scratched horses in final output)

---

**If unsure:** Read this file first, THEN ask Carlo if still unclear.
