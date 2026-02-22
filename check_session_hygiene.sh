#!/bin/bash
# Session Hygiene Monitor
# Checks session size and alerts when thresholds are exceeded

SESSION_DIR="$HOME/.openclaw/agents/main/sessions"
SESSION_FILE="$SESSION_DIR/sessions.json"

# Thresholds
WARN_SIZE_MB=2
ALERT_SIZE_MB=5
WARN_SIZE_BYTES=$((WARN_SIZE_MB * 1024 * 1024))
ALERT_SIZE_BYTES=$((ALERT_SIZE_MB * 1024 * 1024))

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

if [ ! -f "$SESSION_FILE" ]; then
    echo "❌ Session file not found: $SESSION_FILE"
    exit 1
fi

# Get file size in bytes
FILE_SIZE=$(stat -c%s "$SESSION_FILE" 2>/dev/null || stat -f%z "$SESSION_FILE" 2>/dev/null)
FILE_SIZE_MB=$(echo "scale=2; $FILE_SIZE / 1024 / 1024" | bc)

# Count messages (rough estimate)
MSG_COUNT=$(grep -o '"role":' "$SESSION_FILE" | wc -l)

echo "📊 Session Hygiene Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Session file: $SESSION_FILE"
echo "Size: ${FILE_SIZE_MB} MB ($FILE_SIZE bytes)"
echo "Messages: ~$MSG_COUNT"
echo ""

# Check thresholds
if [ "$FILE_SIZE" -gt "$ALERT_SIZE_BYTES" ]; then
    echo -e "${RED}🚨 ALERT: Session size exceeds ${ALERT_SIZE_MB}MB!${NC}"
    echo ""
    echo "Recommended actions:"
    echo "  1. Archive old messages: openclaw archive [session-key]"
    echo "  2. Review and delete unnecessary history"
    echo "  3. Consider starting a new session with /reset"
    echo ""
    exit 2
elif [ "$FILE_SIZE" -gt "$WARN_SIZE_BYTES" ]; then
    echo -e "${YELLOW}⚠️  WARNING: Session size exceeds ${WARN_SIZE_MB}MB${NC}"
    echo ""
    echo "Consider archiving soon to prevent performance issues."
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ Session size is healthy (<${WARN_SIZE_MB}MB)${NC}"
    echo ""
    exit 0
fi
