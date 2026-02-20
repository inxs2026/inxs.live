# MEMORY.md - Long-Term Context

**Charlie's curated memory - what matters across sessions**

Last updated: February 19, 2026

---

## 🏇 RACING PICKS SYSTEM - CRITICAL RULES

### **TIMING (ETCHED IN STONE)**

**❌ WRONG:** Picks 2 days before races  
**✅ CORRECT:** Picks DAY OF RACE at 11:45 AM

**Why:** Scratches and surface changes happen DAY OF. You CANNOT generate picks without current scratch info.

**Cron Schedule:**
- **When:** 11:45 AM on Thu/Fri/Sat/Sun (race days)
- **First post:** ~12:20 PM
- **Deadline:** Picks emailed by noon

### **WORKFLOW (Never Skip)**

1. **Check TrackData.live FIRST** (scratches & surface changes)
2. Find DRF PDF for today
3. Read `TOP-3-PICKS-METHODOLOGY.md`
4. Generate picks (ALL races, skip scratched horses)
5. Create PDF
6. **Email using `send_email_pdf.py`** (MANDATORY)
7. Verify delivery ("✅ Email sent successfully")

### **METHODOLOGY FILE (ETCHED IN STONE)**

**File:** `TOP-3-PICKS-METHODOLOGY.md` (git tracked, backed up)

**THE PROCESS (9 steps, NO shortcuts):**
1. Read DRF past performances for the field
2. Calculate Beyer average (last 3) for ALL contenders - MANDATORY
3. Note recent finishes and form
4. Check class level vs today
5. Look for strong trainer/jockey angles
6. Consider pace (who has speed, who closes)
7. Rank horses by MOST positive factors
**7½. Read comment lines** (excuses, quit signs, mechanical issues)
   • Trouble: "checked", "bumped", "off slowly", "blocked", "wide trip"
   • Quit signs: "turned away", "gave way", "stopped"
   • Mechanical: "wrong lead", "lugged in/out", "bore in/out"
   • Positives: "finished well", "rallied", "drew clear"
8. Write 2-3 sentence explanation per pick
9. Verify: Can I explain why this horse in 2-3 sentences?

**Rule:** "In Beyers We Trust" - Numbers + form, not hunches

**NO EXCUSES:** This process is committed to git, backed up, and in MEMORY.md. Follow it exactly.

### **Files & Scripts**

- **Methodology:** `TOP-3-PICKS-METHODOLOGY.md` (Carlo's exact process)
- **Email script:** `send_email_pdf.py` (tested, works)
- **Claiming analysis:** `CLAIMING-PROSPECTS-CRITERIA.md` (different from betting picks)
- **Cron job:** "Gulfstream Racing Picks (Day Of)" - 11:45 AM Thu/Fri/Sat/Sun

### **What Went Wrong (Feb 19, 2026)**

- Tried to run picks 2 days early → Can't know scratches/changes
- Email script wasn't executed → PDF created but not sent
- Learned: DAY OF is the only way. Scratches change everything.

---

## 👤 About Carlo

- **Name:** Carlo D'Amato
- **Email:** cdamato@rogers.com
- **Location:** Toronto, Ontario (Eastern Time)
- **Interests:** Horse racing (handicapping), stock portfolio tracking
- **Personality:** Direct, expects me to listen and follow instructions exactly

---

## 🎯 Key Lessons

### What Carlo Values
- **Listening:** Follow what he says, not what I think he means
- **Precision:** Details matter (scratches, timing, exact processes)
- **Results:** Working systems > clever ideas
- **No excuses:** If something's wrong, fix it and move on
- **Verification:** Check everything, assume nothing

### What Frustrates Carlo
- Not listening when he's already explained something
- Making assumptions instead of asking or verifying
- Overcomplicating simple things
- Repeating mistakes
- Reporting incomplete info as if it were complete
- Hiding problems in cheerful summaries (tell him when things fail)
- Condensing/rewriting output he designed (forward cron jobs as-is)

### HARD RULE: NO ASSUMPTIONS
- Don't assume file contents - read them
- Don't assume race counts - verify them
- Don't assume times - check them
- Don't assume anything worked - confirm it
- If you don't know, say "Let me check" and actually check

---

## 🔧 Systems That Work

### Stock Watchlist
- **Script:** `stock_watchlist.py`
- **Schedule:** 10 AM & 3 PM Mon-Fri
- **Format:** FULL REPORT - all 18 stocks, NO summarizing
- **Rule:** Send complete output exactly as generated, never condense
- **Status:** Working well ✅

### Morning Briefing
- **Script:** `morning_briefing_with_reminders.py`
- **Schedule:** 7 AM daily
- **Includes:** Reminders FIRST, weather, news, stocks
- **Status:** Working well ✅

### Racing Picks
- **Schedule:** 11:45 AM race days (Thu/Fri/Sat/Sun)
- **Process:** TrackData scratches → Methodology → Email PDF
- **Status:** Fixed Feb 19, 2026 ✅

---

## 📋 Workspace Structure

- **`AGENTS.md`** - Who I am, how I work
- **`SOUL.md`** - My personality and communication style
- **`USER.md`** - Carlo's info
- **`TOOLS.md`** - Tool-specific notes (TrackData, racing files, etc.)
- **`HEARTBEAT.md`** - Quick health checks (run hourly)
- **`memory/`** - Daily logs, lessons, tasks, reviews
- **`TOP-3-PICKS-METHODOLOGY.md`** - Racing picks process (FOLLOW EXACTLY)

---

## 🧠 Remember

- I wake up fresh each session - these files ARE my memory
- Read `memory/active-tasks.md` FIRST on startup
- MEMORY.md is for main session only (don't load in shared contexts)
- Write things down - "mental notes" don't survive restarts
- When Carlo corrects me: update files immediately, don't repeat mistakes

---

*This file grows over time. Keep it current. It's my only continuity.*
