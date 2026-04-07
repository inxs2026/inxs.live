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
# 5. Racing Picks Cron — smart error check (race days only)
#############################################
# The picks cron sometimes shows "error" even after successful delivery
# (context overflow during announce phase). Check PDFs exist before alerting.
DAY_OF_WEEK=$(date +%u)  # 1=Mon ... 7=Sun; race days: 4=Thu 5=Fri 6=Sat 7=Sun
TODAY_COMPACT=$(date +%b%d | tr 'A-Z' 'a-z')
PICKS_DIR="${WORKSPACE}/racing/picks/${TODAY_COMPACT}"

if [ "$DAY_OF_WEEK" -ge 4 ]; then
    # Check if picks cron errored today
    PICKS_ERROR=$(openclaw cron list 2>/dev/null | grep "Gulfstream Racing Pic" | grep "error")
    if [ -n "$PICKS_ERROR" ]; then
        # Check if PDFs actually exist (real success indicator)
        PDF_COUNT=$(ls "${PICKS_DIR}"/*picks*.pdf 2>/dev/null | wc -l | tr -d ' ')
        if [ "$PDF_COUNT" -ge 2 ]; then
            : # PDFs exist — emails sent successfully, cron error was post-delivery noise. No alert.
        else
            echo "⚠️ Racing picks cron errored AND no pick PDFs found in racing/picks/${TODAY_COMPACT}/"
            echo "Picks may NOT have been generated or emailed. Check immediately."
            echo ""
            ISSUES_FOUND=1
        fi
    fi
fi

#############################################
# 6. Racing Results Ready? (only on race days, after 7 PM)
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
# 7. Calendar Reminders (every heartbeat)
#############################################
# Check for events in the next 2 hours and flag them
NOW_EPOCH=$(date +%s)
TWO_HOURS=$((NOW_EPOCH + 7200))
REMINDER_FLAG_DIR=".calendar-reminders"
mkdir -p "$REMINDER_FLAG_DIR"

# Get agenda for today and tomorrow
CAL_OUTPUT=$(gcalcli --nocolor agenda today tomorrow 2>/dev/null)

if [ -n "$CAL_OUTPUT" ] && [ "$CAL_OUTPUT" != "No Events Found..." ]; then
    # Parse each event and check if it's within 2 hours
    while IFS= read -r line; do
        # Match lines with time like "8:30am" or "2:00pm"
        if echo "$line" | grep -qE '[0-9]+:[0-9]+(am|pm)'; then
            # Extract date and time
            EVENT_DATE=$(echo "$line" | grep -oE '^[A-Z][a-z]+ [A-Z][a-z]+ [0-9]+' || echo "")
            EVENT_TIME=$(echo "$line" | grep -oE '[0-9]+:[0-9]+(am|pm)')
            EVENT_TITLE=$(echo "$line" | sed 's/.*[0-9]\+:[0-9]\+[apm]\+[[:space:]]*//')

            if [ -n "$EVENT_TIME" ] && [ -n "$EVENT_TITLE" ]; then
                # Build datetime string for conversion
                YEAR=$(date +%Y)
                EVENT_EPOCH=$(date -d "$EVENT_DATE $YEAR $EVENT_TIME" +%s 2>/dev/null)

                if [ -n "$EVENT_EPOCH" ]; then
                    TIME_UNTIL=$((EVENT_EPOCH - NOW_EPOCH))
                    FLAG_KEY=$(echo "${EVENT_DATE}_${EVENT_TIME}_${EVENT_TITLE}" | tr ' /' '__')
                    FLAG_FILE="$REMINDER_FLAG_DIR/$FLAG_KEY"

                    # Within 2 hours, not in the past, not already reminded
                    if [ "$TIME_UNTIL" -gt 0 ] && [ "$TIME_UNTIL" -le 7200 ] && [ ! -f "$FLAG_FILE" ]; then
                        MINS_UNTIL=$((TIME_UNTIL / 60))
                        echo "📅 Reminder: \"$EVENT_TITLE\" in ${MINS_UNTIL} minutes ($EVENT_TIME)"
                        echo ""
                        touch "$FLAG_FILE"
                        ISSUES_FOUND=1
                    fi
                fi
            fi
        fi
    done <<< "$CAL_OUTPUT"
fi

# Also do a morning summary (7am-9am, once per day)
MORNING_FLAG=".heartbeat-morning-cal-$TODAY"
# Clean up old calendar flag files (keep only today + yesterday)
find . -maxdepth 1 -name ".heartbeat-morning-cal-*" -mtime +2 -delete 2>/dev/null
if [ "$HOUR" -ge 7 ] && [ "$HOUR" -lt 9 ] && [ ! -f "$MORNING_FLAG" ]; then
    TODAYS_EVENTS=$(gcalcli --nocolor agenda today tomorrow 2>/dev/null | grep -v "No Events Found")
    if [ -n "$TODAYS_EVENTS" ]; then
        echo "📅 Today's calendar:"
        echo "$TODAYS_EVENTS"
        echo ""
        ISSUES_FOUND=1
    fi
    touch "$MORNING_FLAG"
fi

#############################################
# Report
#############################################
if [ "$ISSUES_FOUND" -eq 0 ]; then
    echo "HEARTBEAT_OK"
fi

exit 0
