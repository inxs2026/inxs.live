# Heartbeat Guide - Quick Health Checks

**Purpose:** Fast health monitoring without wasting tokens or time

---

## Philosophy

**Heartbeat = Health Monitor, NOT Worker**

- ✅ Quick file checks (<1 sec each)
- ✅ Timestamp comparisons
- ✅ Flag checks
- ❌ NO API calls (email, web, calendar)
- ❌ NO heavy processing (analysis, reports)
- ❌ NO external dependencies

**Rule:** If it takes >30 seconds, it belongs in a cron job.

---

## How It Works

### Heartbeat Prompt (configured in OpenClaw)
```
Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. 
Do not infer or repeat old tasks from prior chats. 
If nothing needs attention, reply HEARTBEAT_OK.
```

### HEARTBEAT.md
Contains instructions for what to check and how to check it.

### heartbeat_check.sh (Optional Helper)
Bash script that runs all checks and returns results.  
Can be called from HEARTBEAT.md or used standalone.

---

## Current Checks (5 Total)

### 1. Session Hygiene (every heartbeat)
**What:** Check sessions.json file size  
**Threshold:** >2MB = warning  
**Why:** Large sessions slow down responses and cost more  
**Time:** <1 second

### 2. Active Tasks (every heartbeat)
**What:** Count task sections in active-tasks.md  
**Threshold:** >0 actual tasks = reminder  
**Why:** Don't forget incomplete work  
**Time:** <1 second

### 3. Workspace Size (once per day)
**What:** Check workspace directory size  
**Threshold:** >1GB = warning  
**Why:** Prevent disk bloat  
**Time:** 2-3 seconds (only once per day)

### 4. Cron Job Health (once per day)
**What:** Verify cron jobs ran yesterday  
**How:** Check if yesterday's log mentions cleanup  
**Why:** Catch broken scheduled jobs early  
**Time:** <1 second (only once per day)

### 5. Racing Results Ready (race days only, after 7 PM)
**What:** Check if today's analysis exists  
**When:** Only after 7 PM on days with racing  
**Why:** Informational reminder that cron will check at 8 PM  
**Time:** <1 second

---

## Performance

**Total time per heartbeat:**
- Normal heartbeat: ~2-5 seconds
- Once-per-day checks included: ~8-10 seconds
- **Worst case:** <30 seconds

**Token cost:**
- If HEARTBEAT_OK: Minimal (just the response)
- If issues found: Small (brief status messages)

**Frequency:** ~1 hour (configurable)

---

## State Files (Ephemeral)

Created in workspace root to track "last checked" timestamps:

- `.heartbeat-workspace-check` - Last workspace size check (YYYY-MM-DD)
- `.heartbeat-cron-check` - Last cron health check (YYYY-MM-DD)

These prevent redundant daily checks. Safe to delete if needed.

---

## Example Outputs

### All healthy:
```
HEARTBEAT_OK
```

### Session getting large:
```
⚠️ Session size: 2.3MB (>2MB threshold)
Consider archiving: openclaw archive or /reset
```

### Multiple issues:
```
⚠️ Session size: 2.1MB (>2MB threshold)
💾 Workspace size: 1.3GB (>1GB)
📋 Reminder: You have 2 active task(s) in memory/active-tasks.md

Recommend: Run cleanup tonight and consider /reset to clear session.
```

### Informational (race day):
```
🏇 Racing analysis for today exists - results may be available
Cron job will check at 8 PM. (No action needed now)

HEARTBEAT_OK
```

---

## Using the Heartbeat System

### Option A: Direct in HEARTBEAT.md
Read HEARTBEAT.md and follow the check instructions inline.

**Pros:** No script dependency  
**Cons:** More verbose, harder to update

### Option B: Call heartbeat_check.sh
Run the bash script and report its output.

**Pros:** Centralized logic, easy to update  
**Cons:** Requires bash script

**Recommended:** Option B (call the script)

---

## Adding New Checks

### Good candidates:
- Git status (uncommitted changes?)
- Memory file count (too many daily logs?)
- Temp file accumulation
- Backup count (verify backup script works)

### Bad candidates (use cron instead):
- Email inbox checking
- Calendar API calls
- Web scraping
- Data analysis
- Report generation

### Template for new check:

```bash
#############################################
# N. Check Name (frequency)
#############################################
LAST_CHECK=".heartbeat-checkname"
TODAY=$(date +%Y-%m-%d)

if [ ! -f "$LAST_CHECK" ] || [ "$(cat $LAST_CHECK 2>/dev/null)" != "$TODAY" ]; then
    # Your quick check here (<5 seconds)
    
    if [ condition_met ]; then
        echo "🔔 Issue description"
        echo "Recommended action"
        echo ""
        ISSUES_FOUND=1
    fi
    
    echo "$TODAY" > "$LAST_CHECK"
fi
```

---

## Heartbeat vs Cron: Decision Matrix

| Task | Time | API Calls | Use |
|------|------|-----------|-----|
| Check file size | <1s | No | ✅ Heartbeat |
| Check if flag exists | <1s | No | ✅ Heartbeat |
| Count files | <1s | No | ✅ Heartbeat |
| Git status | <1s | No | ✅ Heartbeat |
| Email fetch | 5-10s | Yes | ❌ Cron |
| Calendar API | 3-5s | Yes | ❌ Cron |
| Parse PDF | 10-30s | No | ❌ Cron |
| Generate report | 30-120s | Maybe | ❌ Cron |
| Send email | 3-5s | Yes | ❌ Cron |

---

## Troubleshooting

### Heartbeat taking too long?
1. Check which checks are running (add timing statements)
2. Disable once-per-day checks temporarily
3. Reduce check frequency in OpenClaw config

### False positives?
1. Adjust thresholds in heartbeat_check.sh
2. Add better filtering logic
3. Update check to be more specific

### Not catching issues?
1. Lower thresholds
2. Add more specific checks
3. Verify state files are being created

---

## Configuration

### Adjust thresholds:

Edit `heartbeat_check.sh`:

```bash
# Session size warning
WARN_SIZE=$((2 * 1024 * 1024))  # Change to 3MB: $((3 * 1024 * 1024))

# Workspace size warning
THRESHOLD=$((1024 * 1024 * 1024))  # Change to 2GB: $((2 * 1024 * 1024 * 1024))

# Active tasks threshold
if [ "$TASK_SECTIONS" -gt 0 ]; then  # Change to: -gt 2 (only warn if >2 tasks)
```

### Change heartbeat frequency:

In OpenClaw config, adjust heartbeat interval (default ~1 hour).

---

## Maintenance

### Weekly review:
- Are checks still relevant?
- Any false positives to fix?
- New checks to add?

### When adding new cron jobs:
- Update cron health check to verify they ran

### When workspace structure changes:
- Update file path checks
- Adjust size thresholds if needed

---

**Philosophy:** Heartbeat keeps the pulse. Cron does the work. Both together = autonomous operation.
