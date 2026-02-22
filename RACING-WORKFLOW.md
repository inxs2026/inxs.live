# Racing Analysis Workflow

**Purpose:** Standard process for analyzing race cards and delivering picks

---

## Step 1: Gather Data

**Sources:**
- DRF past performances (PDF or text)
- TrackData.live for scratches/changes
- Memory of past analyses for patterns

**Checklist:**
- [ ] Identify track, date, number of races
- [ ] Check for scratches/jockey changes on TrackData.live
- [ ] Note any stakes races or special conditions

---

## Step 2: Analyze Each Race

**⚠️ CLAIMING PROSPECTS:** If analyzing claiming races for prospects (not betting picks), **READ CLAIMING-PROSPECTS-CRITERIA.md FIRST!**

**💡 MULTI-AGENT STRATEGY (Recommended for full cards):**
- **Sub-agent 1:** Claiming prospects analysis (soundness-focused)
- **Sub-agent 2:** Top 3 picks for all races (betting-focused)
- **Main session:** Combine, verify, format final report
- **Benefit:** Better accuracy, specialized focus, parallel work
- **Don't worry about using "too many" sub-agents - accuracy > speed**

**For each race:**
1. Read conditions (distance, surface, class level)
2. Identify top 3-5 contenders based on:
   - Recent form (Beyer figures, finishes)
   - Class (moving up/down)
   - Trainer/jockey stats
   - Workouts
   - Breeding/surface fit
3. Note pace scenario (speed vs closers)
4. Estimate odds for top picks

**Document:**
- Top pick + reasoning
- Runner-up(s)
- Key angles (class drop, trainer pattern, etc.)
- Pace analysis
- Exacta/trifecta suggestions

---

## Step 3: Create Analysis Document

**Structure:**
```markdown
# [Track] - [Date]
## Complete Race Analysis

**Summary Table** (12 races with top picks)

---

## RACE 1: [Conditions]
**Post:** [time] | **Purse:** [amount]

### Top 3 Picks
1️⃣ #X HORSE NAME (odds)
- Key stats
- Reasoning
- Key factors

2️⃣ #X HORSE NAME (odds)
...

### Pace Analysis
### Other Contenders

---

[Repeat for all races]

---

## Betting Strategies
- Best single-race plays
- Exacta plays
- Multi-race tickets (Pick 3/4/5/6)

## Notes & Cautions
- Weather watch
- Scratches to monitor
- Surface changes
```

---

## Step 4: Scratch Updates (If Applicable)

**When scratches occur:**
1. Create new file: `[track]_[date]_UPDATED.md`
2. Note all scratches at top
3. Re-analyze affected races:
   - Identify new favorite
   - Update odds estimates
   - Adjust pace scenario
   - Revise multi-race tickets
4. Clearly mark what changed

**Mark scratched horses:**
```markdown
- **Race 5:** #4 Bella Jak ❌ (was 2nd choice)
→ New favorite: #1 Magic Colors (5-2 ⬆️)
```

---

## Step 5: PRE-DELIVERY VERIFICATION ⚠️

**MANDATORY before sending to Carlo:**

### Quick Verification (5 min):
- [ ] Race count matches card
- [ ] All post times present and sequential
- [ ] Every race has top picks identified
- [ ] Betting strategies section complete
- [ ] Summary table at top

### Scratch Verification (if applicable):
- [ ] Every scratched horse in update actually scratched
- [ ] No scratched horses in "top picks" sections
- [ ] Odds updated for depleted fields
- [ ] New favorites clearly identified

### Data Validation:
- [ ] Beyer figures reasonable for class
  - Maiden claimers: 40-70
  - Claiming: 60-85
  - Allowance: 75-95
  - Stakes: 85-110
- [ ] Odds reasonable (no 500-1 favorites)
- [ ] Horse numbers + names (not just names)
- [ ] Track surface consistent (turf/dirt/tapeta)

### Spot Test (pick 2 races):
- [ ] Race #___ - verified all horses exist, data accurate
- [ ] Race #___ - checked trainer/jockey stats make sense

**Verification time:** ~5 minutes  
**Document:** Keep verification checklist in file comments or separate note

---

## Step 6: Convert to PDF

```bash
cd /home/damato/.openclaw/workspace
soffice --headless --convert-to pdf --outdir . [filename].md
```

**Verify:**
- [ ] PDF created successfully
- [ ] File size reasonable (50-200 KB)
- [ ] Readable (open and spot-check)

---

## Step 7: Email Delivery

**Subject format:** `[Track] [Date] - Analysis` or `[Track] [Date] - UPDATED Analysis (Post-Scratch)`

**Body template:**
```
Carlo,

Here's your complete [Track] analysis for [Date].

[If scratches:]
MAJOR SCRATCHES:
• Race X: Horse Name (was Yth choice)
• Race Y: Horse Name (TOP PICK scratched)

Top Plays:
✅ Race X: Horse Name WIN (odds)
✅ Race Y: Horse Name WIN (odds)
✅ Race Z: Horse Name WIN (odds)

[Brief summary of key angles or stakes races]

Complete analysis attached as PDF.

Good luck! 🏇
-Chi

Sent: [timestamp]
```

**Commands:**
```bash
python3 send_email_pdf.py "cdamato@rogers.com" "Subject" "Body" "/path/to/file.pdf"
```

**Verify before sending:**
- [ ] Recipient correct (cdamato@rogers.com)
- [ ] Subject clear
- [ ] Body mentions attachment
- [ ] PDF path correct and file exists
- [ ] Run email script, confirm success

---

## Step 8: Document in Memory

**Update `memory/YYYY-MM-DD.md`:**
```markdown
## [Track] Analysis - [Time]
- Analyzed [N] races for [date]
- [If scratches:] Major scratches: X horses including [notable ones]
- Top picks: Race X (Horse), Race Y (Horse), Race Z (Horse)
- Created: [filename].md + .pdf
- Email sent to cdamato@rogers.com at [time]
```

**Update `memory/projects.md` if needed:**
- Note any new patterns discovered
- Add to Racing Analytics Suite progress

---

## Post-Race: Results Tracking (Future)

**When races complete:**
1. Fetch results from TrackData.live or DRF
2. Compare picks vs actual results
3. Calculate win %, board %, ROI
4. Update `racing-tools/data/performance/`
5. Generate weekly/monthly report

**Tools:**
- `racing-tools/scripts/track_results.py`
- Daily report generator (TBD)

---

## Common Pitfalls

### ❌ Don't:
- Skip scratch verification (costs $$$)
- Forget to update multi-race tickets after scratches
- Send analysis without PDF attachment
- Use generic "good luck" - be specific about top plays
- Rush verification - 5 min now saves hours of regret

### ✅ Do:
- Check TrackData.live LAST (closest to send time) for late scratches
- Spot-test 2 races minimum
- Keep scratch updates in separate file (don't overwrite original)
- Document all work in memory
- Note any new patterns in lessons.md

---

## Time Estimates

**Full card analysis (12 races):**
- Data gathering: 10 min
- Race-by-race analysis: 60-90 min (5-8 min per race)
- Betting strategies: 10 min
- Verification: 5 min
- PDF + email: 5 min
- **Total: 90-120 min**

**Scratch updates:**
- Identify scratches: 5 min
- Re-analyze affected races: 20-30 min (varies by # of scratches)
- Update multi-race tickets: 10 min
- Verification: 5 min
- PDF + email: 5 min
- **Total: 45-60 min**

---

**Philosophy:** Quality over speed. Verification prevents costly mistakes. Structure ensures consistency.
