#!/bin/bash
# Detect when new DRF PDF arrives and trigger pick generation
# Run this from a cron job or file watcher

RACING_DIR="/home/damato/.openclaw/workspace/racing"
TRIGGER_FILE="/tmp/drf_trigger_sent"

# Find PDFs modified in last 2 hours
NEW_PDFS=$(find "$RACING_DIR" -name "*.pdf" -mmin -120 -type f)

if [ -n "$NEW_PDFS" ]; then
    # Check if we already triggered for this batch
    LATEST_PDF=$(echo "$NEW_PDFS" | head -1)
    LATEST_TIME=$(stat -c %Y "$LATEST_PDF")
    
    if [ -f "$TRIGGER_FILE" ]; then
        LAST_TRIGGER=$(cat "$TRIGGER_FILE")
    else
        LAST_TRIGGER=0
    fi
    
    # Only trigger if this is newer than last trigger
    if [ "$LATEST_TIME" -gt "$LAST_TRIGGER" ]; then
        echo "New DRF PDF detected: $LATEST_PDF"
        echo "Triggering pick generation..."
        
        # Wake the main agent to generate picks
        openclaw wake "New DRF PDF arrived at: $LATEST_PDF - Generate racing picks ASAP using TOP-3-PICKS-CRITERIA.md and email to cdamato@rogers.com"
        
        # Record trigger time
        echo "$LATEST_TIME" > "$TRIGGER_FILE"
        echo "Pick generation triggered successfully"
    else
        echo "Already triggered for this PDF batch"
    fi
else
    echo "No new DRF PDFs found (checked last 2 hours)"
fi
