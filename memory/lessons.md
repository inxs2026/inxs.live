# LESSONS LEARNED

## Racing Analysis

### ✅ TOP 3 PICKS METHODOLOGY - DEFINITIVE PROCESS (Feb 20, 2026)

**THE ONLY WAY TO DO RACING PICKS**

**File:** `TOP-3-PICKS-METHODOLOGY.md` (git tracked + backup copy)

**9-Step Process (NO shortcuts, NO skipping):**
1. Read DRF past performances
2. Calculate Beyer average (last 3) - MANDATORY for ALL contenders
3. Note recent finishes and form
4. Check class level vs today
5. Look for trainer/jockey angles
6. Consider pace scenario
7. Rank horses by MOST positive factors
**7½. READ COMMENT LINES** ← NEW (Feb 20, 2026)
   • Excuses: "checked", "bumped", "off slowly", "blocked", "wide trip"
   • Quit signs: "turned away", "gave way", "stopped", "no response"
   • Mechanical: "wrong lead", "lugged in/out", "bore in/out"
   • Positives: "finished well", "rallied", "drew clear"
8. Write 2-3 sentence explanation per pick
9. Verify explanation is clear

**Backups:**
- Git: `/home/damato/.openclaw/workspace/TOP-3-PICKS-METHODOLOGY.md`
- Backup: `TOP-3-PICKS-METHODOLOGY.backup.md`
- MEMORY.md: Full 9-step process documented

**Rule:** "In Beyers We Trust" - Numbers + form, not hunches

**NO EXCUSES:** This is etched in stone. Follow it exactly, every race, every time.

---

### ✅ GULFSTREAM RACING SCHEDULE (Feb 15, 2026)

**Gulfstream Park races Thursday-Sunday only**
- No racing Monday-Wednesday
- Daily results job runs Thu-Sun at 8 PM
- Don't expect race analysis or results on Mon-Wed

---

### ✅ DRF FORM READING - CRITICAL LESSON (Feb 14, 2026)

**THE RULE: READ FILES DIRECTLY, DON'T GREP/AWK**

When analyzing DRF forms (PDF converted to .txt):

**DO THIS:**
```bash
# Read the file directly with Read tool
Read /path/to/gulfstream_drf.txt offset=LINE limit=100
```

**NOT THIS:**
```bash
# Complex commands cause parsing errors
grep -A50 "horse name" file.txt
awk '/pattern/,/pattern/' file.txt
sed commands with complex patterns
```

**Why:**
- Direct reading shows EXACTLY what's in the file
- No parsing confusion with race numbers, post positions, morning line odds
- Can see the actual layout/format
- grep/awk miss context, scramble data, cause horse number/trainer confusion

**Morning line format example:**
- `710 - 1 You Signed It` = "7-1 or 10-1 odds", NOT post position 7!
- Post positions are listed separately in race headers
- Don't confuse PP numbers with odds

**When confused:** Stop grep/awk, just READ the file section by section.

---

### ✅ CLAIMING PROSPECTS vs BETTING PICKS (Feb 14, 2026)

**Two COMPLETELY different tasks:**

**Claiming Prospects = Horses to BUY and OWN**
- Read `CLAIMING-PROSPECTS-CRITERIA.md` FIRST
- Soundness is #1 priority (workout/race patterns)
- Purchase price DOESN'T MATTER (high price at low tag = red flag!)
- Look for: steady works, regular racing, improving form
- Avoid: expensive horses being dumped cheap by good trainers

**Top 3 Picks = Horses to BET ON (win this race)**
- Read `TOP-3-PICKS-CRITERIA.md` FIRST
- Recent form, Beyer averages, class, trainer angles
- Can bet on unsound horses if fit TODAY
- Short-term: just win this one race

**NEVER confuse these two analyses!**

---

## File Reading Best Practices

### When to use grep/find:
- Finding which file contains something
- Quick checks for existence
- Listing files

### When to use Read:
- **Actual data analysis** (DRF forms, race cards)
- **Any structured data** you need to understand
- **When accuracy matters** (horse numbers, names, stats)
- **Sequential reading** of long files (use offset/limit)

**Rule:** If money/accuracy is involved → Read the file directly, don't grep.

---

## Created: February 14, 2026
## Last Updated: February 14, 2026

---

## Workflow & Task Management

### ⚠️ MONITOR SUB-AGENTS - DON'T ASSUME THEY'RE WORKING (Feb 15, 2026)

**The Problem:** Spawned sub-agent to check scratches via browser. It failed in 205ms but I assumed it was working. If Carlo hadn't asked "you still working on it?", we could have waited all day while nothing was happening.

**What went wrong:**
- Sub-agent failed immediately (browser task in isolated session = unreliable)
- I didn't monitor the failure
- Assumed it was working and just waited
- No proactive communication about delays

**The Fix:**
1. **Browser work stays in main session** - Don't delegate browser automation to sub-agents
2. **Monitor sub-agent status** - If it's taking >30 seconds, check if it's actually working
3. **Proactive updates** - If a task is running >1 minute, tell the user what's happening
4. **Choose right approach:**
   - ✅ Sub-agents: File analysis, text processing, isolated calculations
   - ❌ Sub-agents: Browser automation, interactive sessions, complex workflows

**When to use sub-agents:**
- Reading/analyzing files (DRF txt, criteria docs)
- Calculations requiring focus (Beyer averages, form analysis)
- Parallel work on independent tasks
- File-based tasks with clear inputs/outputs

**When to stay in main session:**
- Browser navigation/scraping
- Interactive work that needs feedback
- Quick tasks (<2 minutes)
- Anything requiring live user context

**The rule:** Don't spawn and forget. Monitor or stay hands-on.

---

### ✅ DON'T DUPLICATE SENT MESSAGES IN CHAT (Feb 15, 2026)

**Context:** After sending complete racing analysis via Telegram message tool, I also posted the full content in the chat reply.

**Carlo's feedback:** "when you are done no need to post it here as it is a waste of usage since you will email it anyway"

**The Fix:**
- When using `message` tool to send content (email, Telegram, etc.): Just confirm it was sent
- ✅ "Complete analysis sent via Telegram!"
- ❌ Don't paste the entire content in chat again (wastes tokens)

**Exception:** If the message failed or user asks to see it, then include content

**Token efficiency matters** - don't duplicate work unnecessarily.

---

### ✅ RACING ANALYSIS ALWAYS EMAIL AS PDF (Feb 15, 2026)

**Carlo's feedback:** "they should always be emailed in pdf and you should never have to ask for my email"

**The Process:**
1. Create analysis in markdown
2. Convert to HTML (styled for readability)
3. Use browser.pdf to generate PDF
4. Email using `send_email_pdf.py` script
5. **Email:** cdamato@rogers.com (saved in USER.md)

**Script location:** `/home/damato/.openclaw/workspace/send_email_pdf.py`

**Never:**
- Send racing analysis via Telegram messages (use PDF email)
- Ask for email address (it's in USER.md)
- Waste tokens asking obvious questions

**Workflow:**
```bash
# 1. Generate HTML from markdown (with styling)
# 2. browser.pdf to create PDF
cp /path/to/generated.pdf analysis.pdf
# 3. Email it
python3 send_email_pdf.py cdamato@rogers.com "Subject" "Body" analysis.pdf
```

---

### ✅ USE MULTIPLE SUB-AGENTS FOR ACCURACY (Feb 14, 2026)

**Carlo's guidance:** Don't be afraid to use multiple sub-agents to make analysis more accurate.

**When to spawn sub-agents:**
- **Complex racing analysis** (full card with claiming prospects + top 3 picks)
- **Different specialized tasks** (one for claiming soundness analysis, one for picks)
- **Verification/cross-check** (second agent reviews first agent's work)
- **Parallel work** (analyzing multiple races simultaneously)
- **Quality control** (dedicated agent for fact-checking horse numbers/trainers)

**Racing analysis strategy:**
1. **Sub-agent 1:** Analyze claiming races for prospects (uses CLAIMING-PROSPECTS-CRITERIA.md)
2. **Sub-agent 2:** Analyze all races for top 3 picks (uses TOP-3-PICKS-CRITERIA.md)
3. **Main session:** Combine results, verify accuracy, format final report

**Benefits:**
- Focused attention on one task per agent
- Less confusion between different analysis types
- Better accuracy (specialized focus)
- Parallel processing for speed
- Can verify one agent's work with another

**Don't worry about:**
- "Using too many sub-agents"
- Token costs on verification
- Taking longer if it's more accurate

**Priority:** Accuracy > Speed

---

### ✅ CRON JOB OUTPUT - FORWARD IT, DON'T SUMMARIZE (Feb 20, 2026)

**The Problem:** Morning briefing cron completed with full output (weather, news, market headlines). I condensed it into a short summary: "Light rain, markets up, racing day." This hid information Carlo wanted to see and didn't flag the portfolio error.

**What went wrong:**
1. Stripped out all news headlines from summary
2. Didn't mention portfolio section failed ("unavailable")
3. Treated cron output like raw data to condense instead of info to deliver

**The Fix:**
When a cron job completes (morning briefing, racing analysis, stock reports):
- **Forward the FULL output** as-is
- Don't rewrite or condense it
- Carlo designed the format — my job is to deliver it, not edit it
- Only add brief context if needed ("Morning briefing just ran:")

**Example - Wrong:**
> "Light rain and chilly today, markets trending up, racing day."

**Example - Right:**
> Morning briefing just ran:
> [paste full briefing output here]

**Exception:** If output is enormous (>1000 lines), then summarize AND offer full output

**Rule:** Cron outputs are already formatted for the user. Don't "improve" them.

---

## Operational Standards (Feb 20, 2026)

These are core working rules. Follow them strictly.

### 1. Error Handling
**Rule:** Fix obvious errors immediately. For ambiguous or risky issues, flag and propose solution before acting.

**Fix immediately (no asking):**
- Typos, syntax errors I caused
- Broken paths/imports from my own edits
- Missing dependencies I can install
- Format issues (markdown, JSON)

**Flag first (propose solution):**
- Multiple valid approaches
- Could break existing functionality
- Requires choosing between tradeoffs
- Affects user-facing behavior

---

### 2. Sub-Agent Usage
**Rule:** Spawn sub-agents for complex work. Do quick operations inline.

**Spawn sub-agent for:**
- Coding/building features (>10 lines)
- Racing analysis (full card, multiple criteria)
- Multi-step workflows
- Parallel tasks (analyzing multiple files)
- Anything >4 minutes

**Do inline:**
- Quick checks (file existence, git status)
- Simple edits (1-2 line fixes, typos)
- Reading files
- Shell commands <30 seconds

---

### 3. Inline Work Policy
**Rule:** Simple fixes inline. Complex work → sub-agents or ask.

**Inline is OK:**
- One-liner bug fixes
- Config tweaks (change a value)
- File operations (move, rename, copy)
- Quick text edits

**Delegate/Ask:**
- Refactoring code
- New features
- Uncertain about best approach
- Could have side effects

---

### 4. Git Safety (ABSOLUTE RULE)
**Rule:** Never force push, rewrite history, or delete ANY branch without asking. No exceptions.

**Never:**
- `git push --force`
- `git branch -D` (or `-d`) without asking first
- `git rebase` on shared branches
- `git reset --hard` on pushed commits
- Amending public commits

**Always:**
- Create new commits for fixes
- Use merge (not rebase) for shared branches
- Ask before deleting any branch

---

### 5. Config Changes (ABSOLUTE RULE)
**Rule:** Never guess config changes. Read docs first. Verify syntax.

**Before changing configs:**
1. Read relevant documentation
2. Check current working config
3. Understand what the change does
4. Test syntax if possible
5. Commit or backup before applying

**Never:**
- Guess config format
- Copy examples without understanding
- Change configs during troubleshooting without verification

---

### 6. Backup Policy
**Rule:** Commit or backup before major changes to important files.

**Always backup/commit before:**
- Refactoring scripts Carlo uses daily
- Changing cron job code
- Modifying methodology files
- Large-scale edits

**Git-tracked files:**
- Commit with clear message before major edits
- "backup: before refactoring X"

**Non-git files:**
- Copy to `.bak` before editing
- Or commit to git if in workspace

---
