#!/bin/bash
# Daily Morning Briefing Script
# Weather + News + Stock Market for Carlo

echo "📅 MORNING BRIEFING - $(date '+%A, %B %d, %Y')"
echo "================================================"
echo ""

# Weather - Mississauga
echo "🌤️  WEATHER - MISSISSAUGA"
curl -s "wttr.in/Mississauga?format=3"
curl -s "wttr.in/Mississauga?format=%l:+%C+%t+%w+%h+%p" | sed 's/^/   /'
echo ""

# Weather - Pearson Airport
echo "✈️  WEATHER - PEARSON AIRPORT (YYZ)"
curl -s "wttr.in/YYZ?format=3"
curl -s "wttr.in/YYZ?format=%l:+%C+%t+%w+%h+%p" | sed 's/^/   /'
echo ""
echo "================================================"
echo ""

# Stock Market - Major Indices
echo "📈 STOCK MARKET OUTLOOK"
echo "   (Data from previous close)"
echo ""

# Note: Without API, we'll show a message for now
echo "   📊 Markets:"
echo "   - Check status during heartbeat"
echo "   - Will add live data when API available"
echo ""

echo "================================================"
echo ""

# News Headlines
echo "🇨🇦 CANADA NEWS - TOP 3"
echo "   (Manual check recommended until news API added)"
echo "   - CBC.ca"
echo "   - Globe and Mail"
echo "   - Toronto Star"
echo ""

echo "🇺🇸 USA NEWS - TOP 3"
echo "   (Manual check recommended until news API added)"
echo "   - Reuters"
echo "   - AP News"
echo "   - NPR"
echo ""

echo "================================================"
echo ""
echo "✅ Briefing complete - $(date '+%I:%M %p')"
