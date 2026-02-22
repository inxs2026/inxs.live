#!/bin/bash
# Heartbeat Health Checks
# Run quick checks, report issues, or return HEARTBEAT_OK

WORKSPACE="$HOME/.openclaw/workspace"
cd "$WORKSPACE" || exit 1

ISSUES_FOUND=0

#############################################
# 1. Session Hygiene Monitor (every heartbeat)
#############################################
SESSION_FILE="$HOME/.openclaw/agents/main/sessions/sessions.json"
if [ -f "$SESSION_FILE" ]; then
    SESSION_SIZE=$(stat -c%s "$SESSION_FILE" 2>/dev/null || stat -f%z "$SESSION_FILE" 2>/dev/null || echo 0)
    WARN_SIZE=$((2 * 1024 * 1024))  # 2MB
    
    if [ "$SESSION_SIZE" -gt "$WARN_SIZE" ]; then
        SESSION_MB=$(echo "scale=1; $SESSION_SIZE / 1024 / 1024" | bc)
        echo "⚠️ Session size: ${SESSION_MB}MB (>2MB threshold)"
        echo "Consider archiving: openclaw archive or /reset"
        echo ""
        ISSUES_FOUND=1
    fi
fi

#############################################
# 2. Active Tasks Monitor (every heartbeat)
#############################################
if [ -f "memory/active-tasks.md" ]; then
    # Look for actual task sections (lines starting with "### " that aren't template)
    TASK_SECTIONS=$(grep "^### " memory/active-tasks.md | grep -v "\[Task Name\]" | wc -l | tr -d ' ')
    
    # If there are actual tasks (not just template)
    if [ "$TASK_SECTIONS" -gt 0 ]; then
        echo "📋 Reminder: You have $TASK_SECTIONS active task(s) in memory/active-tasks.md"
        echo "Check if any need attention or can be completed."
        echo ""
        ISSUES_FOUND=1
    fi
fi

#############################################
# 3. Workspace Size Monitor (once per day)
#############################################
LAST_WS_CHECK=".heartbeat-workspace-check"
TODAY=$(date +%Y-%m-%d)

if [ ! -f "$LAST_WS_CHECK" ] || [ "$(cat $LAST_WS_CHECK 2>/dev/null)" != "$TODAY" ]; then
    WORKSPACE_BYTES=$(du -sb "$WORKSPACE" 2>/dev/null | cut -f1)
    THRESHOLD=$((1024 * 1024 * 1024))  # 1GB
    
    if [ -n "$WORKSPACE_BYTES" ] && [ "$WORKSPACE_BYTES" -gt "$THRESHOLD" ]; then
        WORKSPACE_SIZE=$(du -sh "$WORKSPACE" 2>/dev/null | cut -f1)
        echo "💾 Workspace size: $WORKSPACE_SIZE (>1GB)"
        echo "Consider running cleanup or archiving old files."
        echo ""
        ISSUES_FOUND=1
    fi
    
    echo "$TODAY" > "$LAST_WS_CHECK"
fi

#############################################
# 4. Cron Job Health (once per day)
#############################################
LAST_CRON_CHECK=".heartbeat-cron-check"

if [ ! -f "$LAST_CRON_CHECK" ] || [ "$(cat $LAST_CRON_CHECK 2>/dev/null)" != "$TODAY" ]; then
    # Check if yesterday's daily log mentions cleanup (indicates cron ran)
    YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)
    
    if [ -f "memory/$YESTERDAY.md" ]; then
        if ! grep -qi "cleanup\|storage\|cron" "memory/$YESTERDAY.md" 2>/dev/null; then
            echo "⚠️ Daily cleanup job may not have run yesterday"
            echo "Check: openclaw cron list"
            echo ""
            ISSUES_FOUND=1
        fi
    fi
    
    echo "$TODAY" > "$LAST_CRON_CHECK"
fi

#############################################
# 5. Racing Results Ready? (only on race days, after 7 PM)
#############################################
HOUR=$(date +%H)
if [ "$HOUR" -ge 19 ]; then
    TODAY_COMPACT=$(date +%b%d | tr 'A-Z' 'a-z')  # feb14
    
    # Check if we have today's racing analysis
    if ls "${WORKSPACE}"/*_${TODAY_COMPACT}_*.md 2>/dev/null | grep -q .; then
        RESULTS_FLAG=".racing-results-$TODAY"
        
        if [ ! -f "$RESULTS_FLAG" ]; then
            echo "🏇 Racing analysis for today exists - results may be available"
            echo "Cron job will check at 8 PM. (No action needed now)"
            echo ""
            # Don't mark as issue, just informational
        fi
    fi
fi

#############################################
# Report
#############################################
if [ "$ISSUES_FOUND" -eq 0 ]; then
    echo "HEARTBEAT_OK"
fi

exit 0
