# HEARTBEAT.md - Quick Health Checks Only

**Philosophy:** Heartbeats run frequently (~1hr). Keep checks FAST (<30 sec total).  
Heavy work → cron jobs. Heartbeat → quick file/flag checks only.

---

## Instructions

Run the heartbeat check script:

```bash
bash [[scripts/heartbeat_check.sh]]
```

The script will:
1. Check session size (>2MB = warning)
2. Check active tasks (any incomplete work?)
3. Check workspace size once per day (>1GB = warning)
4. Verify cron jobs ran yesterday (once per day)
5. Note if racing results may be ready (race days after 7 PM)

If all checks pass: Returns `HEARTBEAT_OK`  
If issues found: Lists them with recommendations

**Time:** <30 seconds total, usually <5 seconds

See `HEARTBEAT-GUIDE.md` for full documentation.

---

## Heartbeat Protocol

**When heartbeat poll arrives:**
1. Run ALL checks below (they're fast, no API calls)
2. If ANY check triggers: Report it
3. If NOTHING needs attention: Reply `HEARTBEAT_OK`

**Time budget:** <30 seconds total

---

## Active Checks

### 1. Session Hygiene Monitor (every heartbeat)
**Purpose:** Catch session bloat before it's a problem  
**Check:** File size of sessions.json

```bash
SESSION_SIZE=$(stat -c%s ~/.openclaw/agents/main/sessions/sessions.json 2>/dev/null || echo 0)
WARN_SIZE=$((2 * 1024 * 1024))  # 2MB

if [ $SESSION_SIZE -gt $WARN_SIZE ]; then
  echo "⚠️ Session size: $((SESSION_SIZE / 1024 / 1024))MB (>2MB threshold)"
  echo "Consider archiving: openclaw archive or /reset"
fi
```

**Time cost:** <1 second

---

### 2. Active Tasks Monitor (every heartbeat)
**Purpose:** Don't forget incomplete work  
**Check:** Is active-tasks.md non-empty?

```bash
ACTIVE_TASKS=$(grep -v "^#" memory/active-tasks.md | grep -v "^$" | grep -v "^---" | wc -l)

if [ $ACTIVE_TASKS -gt 5 ]; then  # More than just template lines
  echo "📋 Reminder: You have active tasks in memory/active-tasks.md"
  echo "Check if any need attention or can be completed."
fi
```

**Time cost:** <1 second

---

### 3. Workspace Size Monitor (once per day)
**Purpose:** Prevent disk bloat  
**Check:** Workspace directory size, but only check once per day

```bash
LAST_CHECK_FILE=".heartbeat-workspace-check"
TODAY=$(date +%Y-%m-%d)

if [ ! -f "$LAST_CHECK_FILE" ] || [ "$(cat $LAST_CHECK_FILE)" != "$TODAY" ]; then
  WORKSPACE_SIZE=$(du -sh ~/.openclaw/workspace | cut -f1)
  WORKSPACE_BYTES=$(du -sb ~/.openclaw/workspace | cut -f1)
  THRESHOLD=$((1024 * 1024 * 1024))  # 1GB
  
  if [ $WORKSPACE_BYTES -gt $THRESHOLD ]; then
    echo "💾 Workspace size: $WORKSPACE_SIZE (>1GB)"
    echo "Consider running cleanup or archiving old files."
  fi
  
  echo "$TODAY" > "$LAST_CHECK_FILE"
fi
```

**Time cost:** 2-3 seconds (only once per day)

---

### 4. Cron Job Health (once per day)
**Purpose:** Make sure scheduled jobs are running  
**Check:** Did cron jobs run recently? (file timestamp check)

```bash
LAST_CHECK_FILE=".heartbeat-cron-check"
TODAY=$(date +%Y-%m-%d)

if [ ! -f "$LAST_CHECK_FILE" ] || [ "$(cat $LAST_CHECK_FILE)" != "$TODAY" ]; then
  # Check if daily cleanup ran (should create log entry)
  YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)
  
  if [ -f "memory/$YESTERDAY.md" ]; then
    if ! grep -q "Daily Storage Cleanup\|Storage cleanup\|Cron" "memory/$YESTERDAY.md" 2>/dev/null; then
      echo "⚠️ Daily cleanup job may not have run yesterday"
      echo "Check cron job status: openclaw cron list"
    fi
  fi
  
  echo "$TODAY" > "$LAST_CHECK_FILE"
fi
```

**Time cost:** <1 second (only once per day)

---

### 5. Racing Results Ready? (only on race days)
**Purpose:** Trigger results processing when available  
**Check:** If today's analysis exists, flag for evening results check

```bash
TODAY=$(date +%Y-%m-%d)
TODAY_COMPACT=$(date +%b%d | tr 'A-Z' 'a-z')  # feb14

# Check if we have today's racing analysis
if ls *_${TODAY_COMPACT}_*.md 2>/dev/null | grep -q .; then
  HOUR=$(date +%H)
  
  # Only flag after 7 PM (races should be done)
  if [ $HOUR -ge 19 ]; then
    RESULTS_FLAG=".racing-results-$TODAY"
    
    if [ ! -f "$RESULTS_FLAG" ]; then
      echo "🏇 Racing analysis for today exists - results may be available"
      echo "Cron job will check at 8 PM. (No action needed now)"
      # Don't create flag - let cron job handle it
    fi
  fi
fi
```

**Time cost:** <1 second

---

## ❌ NOT in Heartbeat (Too Heavy)

These belong in **cron jobs**, NOT heartbeat:

- ❌ Email fetching (IMAP calls)
- ❌ Web scraping / API calls
- ❌ Calendar checking (external API)
- ❌ File processing (parsing PDFs, generating reports)
- ❌ Data analysis
- ❌ Sending emails
- ❌ Complex calculations

**Why?** Heartbeats run every ~1hr. Heavy work wastes tokens and time.

---

## Heartbeat State Files

**Purpose:** Track "last checked" timestamps to avoid redundant checks

**Files in workspace root:**
- `.heartbeat-workspace-check` - Last workspace size check (YYYY-MM-DD)
- `.heartbeat-cron-check` - Last cron health check (YYYY-MM-DD)

These are ephemeral flags. It's OK if they're deleted.

---

## Example Heartbeat Response

**If nothing needs attention:**
```
HEARTBEAT_OK
```

**If session is getting large:**
```
⚠️ Session size: 2.3MB (>2MB threshold)
Consider archiving: openclaw archive or /reset
```

**If workspace is bloated:**
```
💾 Workspace size: 1.2GB (>1GB)
Consider running cleanup or archiving old files.
```

**If multiple issues:**
```
⚠️ Session size: 2.1MB (>2MB threshold)
💾 Workspace size: 1.3GB (>1GB)

Recommend: Run cleanup tonight and consider /reset to clear session.
```

---

## Performance Metrics

**Current heartbeat checks:**
- 5 checks total
- 2 run every heartbeat (session size, active tasks)
- 3 run once per day (workspace size, cron health, racing results)

**Time budget:**
- Per heartbeat: <5 seconds (mostly file stat calls)
- Once per day: +3 seconds (du command)
- **Total: <30 seconds worst case**

**Token cost:** Minimal (just reading files, no LLM calls unless something triggers)

---

## Future Optimizations

### If heartbeat becomes slow:
1. Reduce daily checks to every 2 days
2. Skip workspace size check (cron cleanup already monitors this)
3. Remove racing results check (cron handles it)

### Additional quick checks we could add:
- Git status (uncommitted changes?) - `git status --porcelain | wc -l`
- Memory file counts (too many daily logs?) - `ls memory/*.md | wc -l`
- Temp file accumulation - `find /tmp -user damato -mtime -1 | wc -l`

---

**Philosophy:** Heartbeat = "Is everything healthy?" not "Do all the work."  
Fast checks catch problems early. Heavy lifting goes to cron jobs.
