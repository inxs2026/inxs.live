#!/bin/bash
# Chi's voice reply generator
# Usage: ./chi_voice_reply.sh "Text to speak"

TEXT="$1"
OUTPUT="/tmp/chi_voice_$(date +%s).mp3"

if [ -z "$TEXT" ]; then
    echo "Usage: $0 \"Text to speak\""
    exit 1
fi

# Generate voice using edge-tts
edge-tts -v en-US-JennyNeural -t "$TEXT" --write-media "$OUTPUT" 2>&1 >/dev/null

if [ $? -eq 0 ]; then
    echo "$OUTPUT"
else
    echo "Error generating voice" >&2
    exit 1
fi
