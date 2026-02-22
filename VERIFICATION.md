# Verification Protocol

**Purpose:** Catch errors before delivery. The agent that builds ≠ the agent that reviews.

---

## Quick Self-Check (Use for Everything)

Before delivering ANY work to Carlo, run this checklist:

### 1. Requirements Check ✓
- [ ] Re-read the original request
- [ ] Did I answer what was actually asked?
- [ ] Did I include all requested components?

### 2. Common Mistakes Check ✓
- [ ] Check `memory/lessons.md` for relevant past mistakes
- [ ] Verify no repeated errors from previous work

### 3. Output Validation ✓
- [ ] All mentioned files actually exist
- [ ] File sizes are reasonable (not empty, not huge)
- [ ] Formats are correct (PDF is PDF, JSON is valid JSON, etc.)

### 4. Spot Test ✓
- [ ] Pick one example and verify by hand
- [ ] Does the first item/entry look correct?

### 5. Communication Check ✓
- [ ] Is the message clear and complete?
- [ ] Did I explain what I did (not just "done")?
- [ ] Any caveats or limitations mentioned?

**Time cost:** 1-2 minutes. **Error prevention:** ~30-50% of mistakes caught.

---

## Deep Verification (Use for High-Stakes Work)

**When to use:**
- Racing analysis ($$ stakes)
- Code generation (syntax errors matter)
- Important emails (reputation matters)
- Data extraction (accuracy critical)

### Step 1: Self-Review Checklist

Complete the Quick Self-Check above, PLUS:

#### Domain-Specific Checks

**For Racing Analysis:**
- [ ] Every scratched horse actually appears in scratch notifications
- [ ] No horse listed in multiple races
- [ ] Odds are reasonable (no 500-1 favorites, no 1-5 longshots)
- [ ] Race numbers sequential 1-N
- [ ] Post times are chronological
- [ ] All referenced horses have their number (not just name)
- [ ] Track conditions consistent across races
- [ ] Beyer figures make sense (not negative, not >120 for claimers)

**For Code Generation:**
- [ ] Syntax is valid (run through linter if possible)
- [ ] All imports are defined
- [ ] No undefined variables
- [ ] File paths are correct
- [ ] Permissions are set (chmod +x for scripts)

**For Email/Messages:**
- [ ] Recipient is correct
- [ ] Subject line matches content
- [ ] No typos in critical information (names, numbers, dates)
- [ ] Attachments referenced are actually attached
- [ ] Tone matches context (formal vs casual)

**For Data Processing:**
- [ ] Row/record counts match expectations
- [ ] No duplicate entries (unless expected)
- [ ] All required fields populated
- [ ] Date formats consistent
- [ ] Numeric fields are actually numbers

### Step 2: Sub-Agent Review (Optional for Critical Work)

When stakes are very high, spawn a reviewer:

```markdown
sessions_spawn(
  task: "Review [work-type] for errors. Check: [specific checklist]. 
         Output: List of errors found or APPROVE",
  agentId: "main",
  model: "sonnet",  # Use strong model for review
  runTimeoutSeconds: 300,
  cleanup: "delete"  # Remove session after review
)
```

**Review agent instructions:**
- Be critical, not polite
- Look for factual errors, not style issues
- If APPROVE, say why (builds confidence)
- If errors found, be specific (line numbers, exact issue)

---

## Verification Templates

### Racing Analysis Verification

```markdown
## Pre-Delivery Verification: Racing Analysis

**File:** [filename]
**Track:** [track name]
**Date:** [race date]

### Quick Checks:
- [ ] Race count matches card (expected: X races)
- [ ] All post times present and sequential
- [ ] Scratches section complete
- [ ] Best bets summary at top
- [ ] Betting strategies section included

### Scratch Verification:
- [ ] Cross-reference scratch list with updated picks
- [ ] No scratched horses in "top picks"
- [ ] Odds updated for depleted fields
- [ ] New favorites identified

### Data Validation:
- [ ] Beyer figures reasonable for class level
- [ ] Trainer/jockey stats formatted correctly
- [ ] Odds estimates reasonable
- [ ] Race conditions match (turf/dirt/synthetic)

### Spot Test:
- [ ] Picked one race (Race #___) and verified all horses exist
- [ ] Checked odds for top 3 picks are logical

**Result:** ✅ APPROVED / ⚠️ ISSUES FOUND

**Issues (if any):**
- 

**Time spent on verification:** ___ minutes
```

### Code Review Template

```markdown
## Pre-Delivery Verification: Code

**File:** [filename]
**Language:** [language]
**Purpose:** [what it does]

### Syntax & Structure:
- [ ] Syntax valid (linter passed / manual check)
- [ ] Indentation consistent
- [ ] No obvious logic errors

### Dependencies:
- [ ] All imports defined
- [ ] Required libraries installed
- [ ] File paths exist

### Testing:
- [ ] Ran with test input: [describe test]
- [ ] Output matches expected: [describe result]
- [ ] Error handling works: [describe test]

### Security:
- [ ] No hardcoded credentials (check for passwords/keys)
- [ ] Input validation present
- [ ] No dangerous commands without confirmation

**Result:** ✅ APPROVED / ⚠️ ISSUES FOUND

**Issues (if any):**
-

**Time spent on verification:** ___ minutes
```

---

## When Verification Fails

If you find errors during verification:

### 1. Fix Immediately (Minor Issues)
- Typos
- Formatting issues
- Missing obvious data

**Document in lessons.md:** What mistake pattern to watch for

### 2. Rebuild (Major Issues)
- Wrong approach
- Missing critical components
- Data integrity problems

**Don't just patch:** Rebuild properly. Note the root cause in lessons.md.

### 3. Ask Carlo (Unclear)
- Requirements ambiguous
- Trade-offs to choose between
- Missing information needed

**Be specific:** "Found issue X. Option A vs B. Recommend [choice] because [reason]."

---

## Measuring Verification Effectiveness

Track in `memory/self-review.md`:

```markdown
### Verification Stats (Weekly)

**Week of [date]:**
- Deliveries with verification: X
- Issues caught pre-delivery: X
- Issues found post-delivery (by Carlo): X
- Time spent on verification: X minutes
- Error prevention rate: X%
```

**Goal:** Catch 80%+ of errors before Carlo sees them.

---

## Quick Reference

**Every delivery:**
1. Run 5-point Quick Self-Check
2. Pick one example and spot-test it
3. Check lessons.md for past mistakes

**High-stakes work:**
1. Run Quick Self-Check
2. Run domain-specific deep check
3. Consider sub-agent review
4. Document verification in template

**Time investment:** 
- Quick: 1-2 min
- Deep: 5-10 min
- Sub-agent: 3-5 min

**ROI:** Prevents 30-80% of errors. Builds trust. Worth it.

---

**Philosophy:** "Measure twice, cut once." Verification is cheap. Mistakes are expensive.
