#!/bin/bash
# Auto-cleanup racing files - runs daily
# Deletes PDFs and analyses 1 day after race

WORKSPACE="/home/damato/.openclaw/workspace"
RACE_DATE=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)

echo "Cleaning up files from $RACE_DATE..."

# Delete processed PDFs from yesterday
find "$WORKSPACE" -name "GP--${RACE_DATE}*.pdf" -type f -delete 2>/dev/null
find "$WORKSPACE" -name "*drf_text*.txt" -type f -delete 2>/dev/null

# Delete old analyses (keep last 7 days)
find "$WORKSPACE" -name "gulfstream_*_analysis.md" -type f -mtime +7 -delete 2>/dev/null
find "$WORKSPACE" -name "gulfstream_*_analysis.pdf" -type f -mtime +7 -delete 2>/dev/null

echo "Cleanup complete - racing files older than 1 day removed"
