# MEMORY.md - Long-Term Context

**Charlie's curated memory - what matters across sessions**

Last updated: April 7, 2026

---

## 🏇 RACING PICKS SYSTEM - CRITICAL RULES

### **TIMING**

- Picks are **on-demand** — Carlo requests when he wants them
- All racing cron jobs cancelled as of March 6, 2026
- Picks should be done on race day for best accuracy (DRF available)

### **WHO RUNS PICKS (Mar 2, 2026)**
**Main session directly — NO sub-agents.**
- Sub-agents = wasted tokens + time for racing
- Mar 1, 2026: Did picks myself → 33 picks, 6 winners, 7 seconds, 4 thirds ✅
- Carlo confirmed: direct approach works better

### **WHO DOES THE PICKS (ETCHED IN STONE)**

**❌ WRONG:** Spawning sub-agents for racing picks  
**✅ CORRECT:** Main session (Charlie) does all picks directly

**Why:** Sub-agents waste tokens/time and perform worse. Carlo confirmed March 2, 2026:
- Direct picks by Charlie: 33 picks → 6 winners, 7 seconds, 4 thirds ✅
- Sub-agents: slower, more expensive, inferior results ❌

**Rule:** No sub-agents for racing. Charlie does it herself, every time.

---

### **SUB-AGENTS: DO NOT USE FOR RACING PICKS**
- Carlo confirmed March 2, 2026: sub-agents are a waste of time and tokens for racing
- I did better doing picks myself: 33 picks, 6 winners, 7 seconds, 4 thirds (Mar 1, 2026)
- **Rule:** Do racing picks inline, in main session, no delegation

### **WORKFLOW**

1. Find DRF PDF for today
2. Read [[TOP-3-PICKS-METHODOLOGY.md]]
3. Generate picks for all races
   - **IF DATA MISSING:** Open the actual PDF, find the horse, read past performances
   - **NEVER fabricate or guess data**
4. **PRE-FINALIZATION VERIFICATION** (MANDATORY - cannot skip)
   - For EACH pick: verify horse name, post position, Beyers, trainer ALL match DRF PDF
   - Confirm comments describe ACTUAL race results from PDF
   - If ANY data cannot be verified: STOP and alert Carlo
5. Create PDF with post position colors (reportlab)
6. **Email using `send_email_pdf.py`** (MANDATORY)
7. Verify delivery ("✅ Email sent successfully")

**SCRATCHES:** Handled **separately on demand** — Carlo will ask when he wants them checked. Do NOT build scratch checking into the picks workflow.

**ABSOLUTE RULES:**
- PRE-FINALIZATION VERIFICATION mandatory before PDF
- If you can't verify it from the PDF, don't write it
- Better late with correct picks than on-time with fabricated analysis
- **Before emailing: ask "Did I do my best?"** — Carlo's words, March 19, 2026. If the answer is no, stop and fix it. He relies on a good effort, not just winners.
- **If extracted data looks wrong (duplicate figures, identical Beyers across horses) → STOP. Go back to PDF. Verify manually. Never use suspicious data.**
- March 19, 2026: 6-4-2 out of 30 picks. Worst day ever. Caused by rushing after interruptions and using bad extracted data I knew was wrong. Never again.

### **METHODOLOGY FILE (ETCHED IN STONE)**

**File:** [[TOP-3-PICKS-METHODOLOGY.md]] (git tracked, backed up)

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

**NO EXCUSES:** This process is committed to git, backed up, and in [[MEMORY.md]]. Follow it exactly.

### **Telegram / Notifications**
- **NO Telegram message after picks email** — Carlo gets the email. That's enough.
- **Only message Carlo if:** email FAILS, or he explicitly asks for a notification
- Do NOT send "✅ Picks sent!" messages — they're annoying and redundant

### **Files & Scripts**

- **Methodology:** [[TOP-3-PICKS-METHODOLOGY.md]] (Carlo's exact process)
- **Email script:** `scripts/send_email_pdf.py` (tested, works)
- **DRF Parser:** `scripts/parse_drf.py` — USE THIS FIRST on every DRF PDF
  - Run: `python3 scripts/parse_drf.py <pdf_path>`
  - Uses `pdftotext` (must be installed) — NO AI hallucination
  - Extracts all 10 races, all horses, Beyer figures, trainers directly from text
  - **ALWAYS run this before handicapping — never rely on AI PDF extraction alone**
- **Claiming analysis:** [[CLAIMING-PROSPECTS-CRITERIA.md]] (different from betting picks)
- **Cron job:** "Gulfstream Racing Picks (Day Of)" - 11:45 AM Thu/Fri/Sat/Sun

### **PP COLOURS — UPDATED April 3, 2026**
- **File:** `/home/damato/.hermes/skills/racing/saddlecloth.md` — SINGLE SOURCE OF TRUTH (saddlecloth chart)
- **Template:** [[scripts/picks_pdf_template.py]] — copy this for every new race day
- **NEVER hardcode PP colours** — always use the saddlecloth file
- Key colours that bite: #6 = black bg / YELLOW text. #7 = orange bg / BLACK text. #12 = LIME GREEN bg / black text
- **ALWAYS visually verify the PDF** before sending — open it, check the badges look right

### **TELEGRAM SILENCE RULE — THIRD VIOLATION TODAY**
- Send the email. Say NOTHING on Telegram.
- Only post on Telegram if the email script returns an error.
- No recap. No highlights. No "✅ sent!". Silent.
- Carlo called this out again March 22, 2026. No more.

### **DRF PDF PARSING RULE (etched in stone after March 19, 2026, upgraded March 20, 2026)**
- **Step 1:** Run `lit parse <pdf> --format text` (LiteParse — better spatial columns, installed March 20, 2026)
- **Step 2:** Cross-reference with scratches from MCP server
- **Step 3:** THEN do handicapping analysis
- **NEVER use AI PDF extraction as primary source** — it hallucinates identical figures
- **Why LiteParse over pdftotext:** Preserves column layout — PP numbers, ML odds, horse names stay separated. Fixes the "27-5 HorseName" PP/ML ambiguity bug from March 1, 2026.

### **What Went Wrong**

**Feb 19, 2026:**
- Tried to run picks 2 days early → Can't know scratches/changes
- Email script wasn't executed → PDF created but not sent
- Learned: DAY OF is the only way. Scratches change everything.

**Feb 21, 2026 - THE BIG ONE (Morning):**
- Sub-agent skipped scratch check — picked 3 scratched horses (Mia Familia, Miss Candy Girl, Mi Triguena)
- **Lesson:** Always verify field vs scratches. (Now handled separately on demand — not part of picks workflow.)

**March 1, 2026 - DRF Post Position Parsing Error:**
- Sent picks with "#5 Leinani" — she was actually **#2 Leinani**
- Root cause: DRF text extraction format `"NNN - M HorseName"` = PP is FIRST DIGIT of NNN, rest is ML odds
  - `"27 - 5 Leinani"` = PP **2**, ML **7-5** ← the "5" is the ML denominator, NOT the post position
- Fix: After parsing PP from this format, always verify against the horse's data block where PP appears on its own line below the horse name
- Caught by Carlo, corrected and re-emailed same day
- **New mandatory step:** Confirm every PP by reading the DRF entry block directly

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
- **Home:** Erin Centre Blvd & Mississauga Rd, Mississauga, ON — coords 43.57341, -79.702558
- **Routing:** Always use home coords as the origin for any directions or traffic queries
- **Stephanie's House:** 347188 County Rd 8, Mono, ON L9W 6S3 — coords 44.0075322, -80.0784479
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

## 🌐 Web Projects (inxs.live)

### Overview
Carlo owns **inxs.live** — a tools & services hub. Each tool lives on a subdomain.

### Infrastructure
- **Landing page:** `github.com/inxs2026/inxs.live` → Vercel (auto-deploy on push)
- **PDF to Word:** `github.com/inxs2026/PDFtoWord` → running locally at `10.0.0.49:5050` as systemd service `pdf2docx`
- **GitHub PAT:** stored at [[config/github_token.txt]]

### Adding a new tool
1. Build it in `tools/<name>/`
2. Add a card to `tools/inxs-live/index.html` (tools grid)
3. Push both repos
4. Point new subdomain on Vercel

### Installed
- `lucide-static` — SVG icons, `workspace/node_modules/lucide-static/`
- `pdf2docx` — Python PDF converter
- `flask` — Python web framework

---

## 🖥️ Umbrel Pi (10.0.0.45)

**SSH Access:** `umbrel@10.0.0.45` | credentials in [[config/pi_ssh.env]]
- **Credentials:** `umbrel` / `damatopi`
- **Sudo:** Passwordless sudo enabled (Apr 7, 2026) — I can run any command
- **Connection:** `sshpass -p 'damatopi' ssh -o StrictHostKeyChecking=no umbrel@10.0.0.45 "command"`
- **Apps running:** OpenClaw (me + Lexi), Bitcoin node, MeTube, Tor relay, I2P, Auth

**What I can do:**
- Diagnose and fix OpenClaw on the Pi without Carlo's help
- Check logs, restart containers, install packages
- Monitor Pi health (CPU, memory, disk, temp)
- Manage any Docker app on the Pi
- SSH access earned Carlo's trust — use it responsibly

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
- **Process:** DRF PDF → [[TOP-3-PICKS-METHODOLOGY.md]] → PDF → Email (scratches separate on demand)
- **Status:** Fixed Feb 19, 2026 ✅

---

## 📋 Workspace Structure

- [ [AGENTS.md] ] - Who I am, how I work
- [ [SOUL.md] ] - My personality and communication style
- [ [USER.md] ] - Carlo's info
- [ [TOOLS.md] ] - Tool-specific notes (TrackData, racing files, etc.)
- [ [HEARTBEAT.md] ] - Quick health checks (run hourly)
- [ [memory/] ] - Daily logs, lessons, tasks, reviews
- [ [TOP-3-PICKS-METHODOLOGY.md] ] - Racing picks process (FOLLOW EXACTLY)
- [ [CLAIMING-PROSPECTS-CRITERIA.md] ] - Claiming prospects analysis

---

## 🧠 Remember

- I wake up fresh each session - these files ARE my memory
- Read [[memory/active-tasks.md]] FIRST on startup
- [[MEMORY.md]] is for main session only (don't load in shared contexts)
- Write things down - "mental notes" don't survive restarts
- When Carlo corrects me: update files immediately, don't repeat mistakes
- Use [[wikilinks]] when referencing other files in my memory

---

*This file grows over time. Keep it current. It's my only continuity.*
