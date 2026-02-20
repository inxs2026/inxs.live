# Saturday Feb 21, 2026 - Pre-Flight Checklist

**Last Updated:** Friday Feb 20, 2026 5:45 PM

---

## ✅ Files Ready

- [x] DRF PDF saved: `/home/damato/.openclaw/workspace/racing/feb21/gulfstream_feb21_drf.pdf` (902KB, 12 races)
- [x] Methodology updated: `TOP-3-PICKS-METHODOLOGY.md` (10 steps, post positions mandatory)
- [x] Split-batch workflow: `SPLIT-BATCH-WORKFLOW.md` (documented process)
- [x] Verification script: `verify_picks.py` (ready to use)
- [x] Email script: `send_email_pdf.py` (tested, works)
- [x] MEMORY.md updated (10-step process etched in stone)
- [x] Lessons documented: `memory/lessons.md` (Feb 20 errors recorded)

---

## ✅ Cron Jobs Configured

**11:30 AM - Pre-Check:**
- Verifies DRF exists
- Checks TrackData.live access
- Confirms methodology file present
- Silent if OK, alerts if problems

**11:45 AM - Racing Picks (UPDATED):**
- Reads SPLIT-BATCH-WORKFLOW.md
- Reads TOP-3-PICKS-METHODOLOGY.md (10 steps)
- Splits 12 races → Batch 1 (1-6), Batch 2 (7-12)
- **Mandatory:** Post positions on every pick
- **Mandatory:** Verification before each email
- Timeout: 7200 seconds (2 hours - plenty of time)

---

## ✅ Operational Rules in Place

1. **Error Handling:** Fix obvious, flag risky
2. **Sub-Agent Usage:** >4 min tasks
3. **Inline Work Policy:** Simple fixes only
4. **Git Safety:** Never force push/delete branches
5. **Config Changes:** Read docs first, verify syntax
6. **Backup Policy:** Commit before major changes

---

## ✅ Racing Picks Process (10 Steps)

1. Read DRF past performances
2. Calculate Beyer averages (last 3) - MANDATORY
3. Note recent finishes and form
4. Check class level vs today
5. Look for trainer/jockey angles
6. Consider pace scenario
7. Rank horses by MOST positive factors
**7½.** Read comment lines (excuses, quit signs, mechanical issues)
8. Write explanations **WITH POST POSITIONS**: `#3 HORSE NAME`
9. **VERIFY DATA INTEGRITY** - name, post, Beyers, trainer match DRF
10. Final check: Can I explain each pick clearly?

---

## ✅ Split-Batch Timeline

- **11:30 AM** → Pre-check runs (silent if OK)
- **11:45 AM** → Cron spawns sub-agent
- **~12:00 PM** → Batch 1 analysis complete
- **~12:15-12:20 PM** → Email #1 sent (Races 1-6)
- **~12:30 PM** → Batch 2 analysis complete
- **~12:45-1:00 PM** → Email #2 sent (Races 7-12)
- **12:20 PM** → First post (Carlo has Batch 1 by then)

---

## ✅ Error Prevention Measures

**Post Positions (#3 HORSE NAME):**
- Forces explicit mapping
- Prevents wrong names
- Standard racing format

**Verification (Step 9):**
- Cross-checks every pick against DRF
- Horse name matches post position?
- Beyers match this horse's data?
- Trainer matches this horse?
- **BLOCKS email if errors found**

**Split-Batch Timing:**
- 6 races in ~30-40 min (manageable)
- Time for quality checks
- Time for verification
- No rushing

---

## ✅ Success Criteria

Tomorrow's test run is successful if:
- [  ] Both emails sent on time (Batch 1 before 12:20 PM)
- [  ] ZERO data scrambling errors (right names, right trainers, right Beyers)
- [  ] Post positions included on ALL picks
- [  ] Verification step completed for both batches
- [  ] Full 10-step methodology followed for all 12 races
- [  ] Carlo receives quality picks he can trust

---

## ✅ Backups Created

- `TOP-3-PICKS-METHODOLOGY.backup.md` (first backup)
- `TOP-3-PICKS-METHODOLOGY.backup2.md` (after post position update)
- All critical files committed to git (6 commits today)
- Git log shows complete history

---

## 🚀 Ready to Go

Everything is locked in. Tomorrow at 11:45 AM, the system will:
1. Read the split-batch workflow
2. Follow the 10-step methodology
3. Include post positions on every pick
4. Verify data integrity before emailing
5. Send two quality batches on time

**No excuses. No data scrambling. Quality picks delivered.**

---

**If anything goes wrong tomorrow:** Check this checklist, verify files exist, review cron job logs.
