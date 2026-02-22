# MEMORY.md - Long-Term Context

**Charlie's curated memory - what matters across sessions**

Last updated: February 21, 2026

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

**STEP 0 (DO THIS FIRST, BEFORE ANYTHING ELSE):**
1. **Run:** `mcporter call trackdata.get_scratches` (gets today's scratches with horse names)
2. **Document scratches** in scratches.txt
3. **DO NOT PROCEED** until scratches are known
- *(Fallback if MCP down: go to TrackData.live, password: damatopi)*

**THEN:**
5. Find DRF PDF for today
6. Read `TOP-3-PICKS-METHODOLOGY.md`
7. Generate picks (ALL races, SKIP scratched horses)
   - **IF DATA MISSING:** Open the actual PDF, find the horse, read past performances
   - **NEVER fabricate or guess data**
8. **PRE-FINALIZATION VERIFICATION** (MANDATORY - cannot skip)
   - For EACH pick: verify horse name, post position, Beyers, trainer ALL match DRF PDF
   - Confirm comments describe ACTUAL race results from PDF
   - If ANY data cannot be verified: STOP and alert Carlo
9. Create PDF
10. **Email using `send_email_pdf.py`** (MANDATORY)
11. Verify delivery ("✅ Email sent successfully")

**ABSOLUTE RULES:** 
- Scratches FIRST, picks SECOND
- PRE-FINALIZATION VERIFICATION mandatory before PDF
- If you can't verify it from the PDF, don't write it
- Better late with correct picks than on-time with fabricated analysis

### **METHODOLOGY FILE (ETCHED IN STONE)**

**File:** `TOP-3-PICKS-METHODOLOGY.md` (git tracked, backed up)

**THE PROCESS (10 steps, NO shortcuts):**
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
8. Write explanations **WITH POST POSITIONS**: `#3 HORSE NAME - Avg Beyer...`
9. **VERIFY DATA INTEGRITY** - horse name, post position, Beyers, trainer ALL match DRF
10. Final check: Can I explain each pick in 2-3 sentences?

**Rule:** "In Beyers We Trust" - Numbers + form, not hunches

**CRITICAL:** Post positions (#1, #2, #3) are MANDATORY. Prevents data scrambling errors (Feb 20, 2026 - wrong names/trainers matched to wrong horses).

**NO EXCUSES:** This process is committed to git, backed up, and in MEMORY.md. Follow it exactly.

### **Files & Scripts**

- **Methodology:** `TOP-3-PICKS-METHODOLOGY.md` (Carlo's exact process)
- **Email script:** `send_email_pdf.py` (tested, works)
- **Claiming analysis:** `CLAIMING-PROSPECTS-CRITERIA.md` (different from betting picks)
- **Cron job:** "Gulfstream Racing Picks (Day Of)" - 11:45 AM Thu/Fri/Sat/Sun

### **What Went Wrong**

**Feb 19, 2026:**
- Tried to run picks 2 days early → Can't know scratches/changes
- Email script wasn't executed → PDF created but not sent
- Learned: DAY OF is the only way. Scratches change everything.

**Feb 21, 2026 - THE BIG ONE (Morning):**
- **Sub-agent SKIPPED scratch check entirely**
- Generated picks without checking TrackData.live first
- Result: Picked 3 SCRATCHED horses (#13 Mia Familia, #3 Miss Candy Girl, #8 Mi Triguena)
- **Root cause:** Workflow didn't enforce "STEP 0: CHECK SCRATCHES FIRST"
- **Fix:** Updated cron job with mandatory STEP 0 - scratches BEFORE any analysis
- **Lesson:** SCRATCHES FIRST is not optional. It's STEP 0. Period.

**Feb 21, 2026 - Race 3 Data Fabrication (Afternoon):**
- **Fabricated Beyers for #5 Outlaw Country** (wrote 83.0 avg when couldn't find data)
- Wrong comments for #6 Gallant Knight (scrambled race sequence/margins)
- Result: Had the WINNER (#6) but put it at #2 because fake data pushed wrong horse to #1
- **Root cause:** Didn't open actual DRF PDF to verify data, gave up and invented it
- **Fix:** Added PRE-FINALIZATION VERIFICATION checklist - mandatory before PDF
- **Lesson:** If you can't verify it from the PDF, don't write it. No fabricated data. Ever.

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

### HARD RULE: VERIFY BEFORE SENDING — ALWAYS
**"Mistakes only happen when confirmations are missed."** — Carlo, Feb 22, 2026

Before ANYTHING goes out (email, Telegram, PDF, report):
- Is every piece of data confirmed from the source? (not guessed, not assumed)
- Have all required steps been completed in order?
- Is anything missing, scratched, or changed since last check?
- Would I be comfortable if Carlo audited this line by line?

If the answer to ANY of these is uncertain → STOP and verify first.
Better late and correct than on-time and wrong. Every time.

**This applies to:** racing picks, stock reports, morning briefing, any automated output.

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
