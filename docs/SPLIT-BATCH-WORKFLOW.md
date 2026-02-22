# Split-Batch Racing Picks Workflow

**Effective:** Saturday, February 21, 2026  
**Purpose:** Quality picks delivered on time using two-email approach

---

## Timeline

**11:45 AM** - Cron job spawns sub-agent  
**~12:15-12:20 PM** - Email #1 (Races 1-6) sent  
**~12:45-1:00 PM** - Email #2 (Races 7-12) sent  
**First post:** 12:20 PM

---

## Batch 1: Races 1-6

### Step 1: Generate Picks (Full Methodology)
- Read DRF for races 1-6
- Follow **all 10 steps** of TOP-3-PICKS-METHODOLOGY.md
- Calculate Beyer averages (last 3) for ALL contenders
- Read comment lines (step 7½)
- **CRITICAL:** Format picks with POST POSITIONS:
  ```markdown
  **1. #3 HORSE NAME** - Avg Beyer (last 3): 72.0
  ```

### Step 2: VERIFY DATA INTEGRITY (MANDATORY)
Before creating PDF, cross-check EVERY pick:

- Does horse name exist in this race? ✓
- Is it at the post position I claimed? ✓  
- Do Beyers match this horse's DRF data? ✓
- Does trainer match this horse? ✓

**If ANY mismatch → STOP, fix, re-verify**

### Step 3: Create & Email PDF
- Convert markdown → HTML → PDF
- Email using `send_email_pdf.py`
- Subject: "Gulfstream Picks Feb 21 - Races 1-6"
- Verify delivery ("✅ Email sent successfully")

---

## Batch 2: Races 7-12

### Repeat Same Process
- Full methodology for races 7-12
- Same verification requirements
- Same quality standards
- Email subject: "Gulfstream Picks Feb 21 - Races 7-12"

---

## Quality Checklist (BEFORE EMAILING)

For each pick in BOTH batches, verify:

- [ ] Post position included (#1, #2, #3)
- [ ] Horse name matches DRF for that post position
- [ ] Beyer average calculated and matches DRF data (±5 tolerance)
- [ ] Trainer name matches this horse
- [ ] 2-3 sentence explanation provided
- [ ] Scratches noted and excluded from picks

**ZERO TOLERANCE for data scrambling errors.**

---

## Why This Works

**Two batches = more time:**
- Batch 1: ~30 min for 6 races → quality maintained
- Batch 2: ~30-40 min for 6 races → no rushing

**Post positions = error prevention:**
- Forces explicit mapping (post # → name → data)
- Makes mistakes obvious before emailing

**Verification = safety net:**
- Catches wrong names, wrong trainers, wrong Beyers
- Blocks email if errors found

---

## Tomorrow's Test Run

Saturday Feb 21, 2026 - 12 races at Gulfstream

**Success criteria:**
- Both emails sent on time
- ZERO data scrambling errors
- Full methodology followed for all 12 races
- Post positions included on all picks
- Verification passed before both emails

After Saturday, we'll evaluate whether to make this permanent.

---

**Rule:** Quality over speed. Split-batch gives us time to do it right.
