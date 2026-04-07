# Cron Jobs - Automated Tasks

**Purpose:** Scheduled autonomous work in isolated sessions

**Related:** [[HEARTBEAT.md]] for quick health checks | [[memory/lessons.md]] for lessons learned

---

## Active Jobs (3)

### 1. Daily Racing Results Tracking 🏇
**Schedule:** Every day at 8:00 PM EST  
**Cron:** `0 20 * * *`  
**Model:** Sonnet (needs quality for data accuracy)  
**Timeout:** 5 minutes  
**Delivery:** Announce (sends result summary to Carlo)

**What it does:**
1. Checks workspace for today's race analysis file
2. Looks for results on TrackData.live or DRF
3. If results available:
   - Compares picks vs actual results
   - Calculates win %, board %, ROI
   - Updates `racing-tools/data/performance/`
   - Sends summary to Carlo
4. If no results: Notes to check tomorrow

**Why isolated session:**
- No context pollution from our main chat
- Runs even if I'm "asleep" or idle
- Uses separate token budget
- Output delivered directly, not mixed with conversation

**Next run:** Tonight at 8:00 PM

---

### 2. Weekly Self-Review 📊
**Schedule:** Every Sunday at 8:00 PM EST  
**Cron:** `0 20 * * 0`  
**Model:** Sonnet (needs thoughtful analysis)  
**Timeout:** 10 minutes  
**Delivery:** Announce (sends review summary to Carlo)

**What it does:**
1. Reads `memory/lessons.md` and `memory/self-review.md`
2. Reviews past 7 days of daily logs
3. Analyzes:
   - What went well this week
   - Mistakes made
   - New patterns learned
   - Improvement goals for next week
4. Updates `memory/self-review.md` with findings
5. Sends summary to Carlo (3-5 highlights, 1-2 lessons, 1-2 goals)

**Why isolated session:**
- Deep reflection needs focus, not chat interruptions
- Can read all memory files without cluttering main session
- Dedicated time for self-improvement
- Weekly cadence prevents burnout

**Next run:** Sunday, February 16 at 8:00 PM

---

### 3. Daily Storage Cleanup 🧹
**Schedule:** Every day at midnight (12:00 AM EST)  
**Cron:** `0 0 * * *`  
**Model:** Haiku (simple tasks, cheaper)  
**Timeout:** 5 minutes  
**Delivery:** None (only alerts Carlo if issues found)

**What it does:**
1. Runs `auto_cleanup.sh` (deletes old racing files)
2. Checks workspace size (`du -sh`)
3. Archives old racing PDFs (>7 days)
4. Runs `cleanup_backups.sh` (keeps 4 most recent)
5. Runs `check_session_hygiene.sh` (checks session size)
6. Reports summary to daily log
7. **Only alerts Carlo if:**
   - Workspace >1GB
   - Session >1.5MB
   - Cleanup errors

**Why isolated session:**
- Maintenance shouldn't interrupt conversations
- Runs while everyone's asleep
- Silent unless there's a problem
- Uses cheap model (simple file operations)

**Next run:** Tonight at midnight

---

## Cron Job Philosophy

### Isolated Sessions = Clean Separation
**Benefits:**
- No context bleed (racing results don't mix with chat history)
- Different models per task (Haiku for cleanup, Sonnet for analysis)
- Predictable timing (not "sometime in the next hour")
- Independent failure (one job failing doesn't crash others)

### Delivery Modes
- **`announce`** - Sends results to Carlo via Telegram
- **`none`** - Silent (only logs to memory, alerts if issues)

### When to Use Cron vs Heartbeat
**Use Cron when:**
- ✅ Exact timing matters (daily at 8 PM, not "evening-ish")
- ✅ Task needs isolation from main chat
- ✅ Want different model/thinking level
- ✅ Output should deliver directly to Carlo

**Use Heartbeat when:**
- ✅ Multiple quick checks can batch together
- ✅ Needs recent conversational context
- ✅ Timing can drift (every ~30 min is fine)

---

## Managing Cron Jobs

### List all jobs
```bash
openclaw cron list
# or use tool:
cron(action: "list")
```

### Check specific job runs
```bash
cron(action: "runs", jobId: "55b73e49-ddae-4896-b48d-1c66cb548e3e")
```

### Manually trigger a job (for testing)
```bash
cron(action: "run", jobId: "55b73e49-ddae-4896-b48d-1c66cb548e3e")
```

### Disable a job temporarily
```bash
cron(action: "update", jobId: "55b73e49-...", patch: {"enabled": false})
```

### Remove a job
```bash
cron(action: "remove", jobId: "55b73e49-...")
```

---

## Job IDs (for reference)

| Name | ID | Schedule |
|------|-----|----------|
| Daily Racing Results | `55b73e49-ddae-4896-b48d-1c66cb548e3e` | Daily 8 PM |
| Weekly Self-Review | `ff99648b-7dfb-4659-ac09-9e8a16f2f565` | Sunday 8 PM |
| Daily Storage Cleanup | `505a1058-8702-4749-a081-a9a7a27a6a05` | Daily midnight |

---

## Future Cron Jobs (Ideas)

### Morning Briefing (if Carlo wants it)
**Schedule:** Daily 7 AM  
**Purpose:** Check calendar, weather, important emails, and deliver morning summary

### Weekly Performance Report
**Schedule:** Friday 6 PM  
**Purpose:** Analyze week's racing performance, calculate ROI, identify patterns

### Monthly Archive
**Schedule:** 1st of month, midnight  
**Purpose:** Archive old memory files, compress workspace, clean up old data

---

## Monitoring & Debugging

### If a job fails:
1. Check `cron(action: "runs", jobId: "...")` for error logs
2. Review the isolated session (if it logged anything)
3. Test manually with `cron(action: "run", ...)`
4. Update job with fixed message/logic

### If a job doesn't run:
1. Check `cron(action: "status")` - is cron enabled?
2. Verify `nextRunAtMs` timestamp is correct
3. Check if job is `enabled: true`
4. Look at gateway logs for cron scheduler errors

---

**Philosophy:** Cron jobs turn me from reactive chatbot into autonomous operator. I do useful work even when Carlo's not asking.
