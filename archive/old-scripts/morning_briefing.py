#!/usr/bin/env python3
"""
Daily Morning Briefing for Carlo
- Weather (Mississauga & Pearson Airport)
- News headlines (placeholder until API available)
- Stock market outlook (placeholder until API available)
"""
import subprocess
import datetime
import sys

def get_weather(location):
    """Get weather from wttr.in"""
    try:
        result = subprocess.run(
            ['curl', '-s', f'wttr.in/{location}?format=%l:+%c+%t+%h+%w', '--max-time', '5'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return f"{location}: Weather data unavailable"
    except Exception as e:
        return f"{location}: Error - {e}"

def main():
    """Generate morning briefing"""
    now = datetime.datetime.now()
    
    print(f"📅 MORNING BRIEFING - {now.strftime('%A, %B %d, %Y')}")
    print("=" * 60)
    print()
    
    # Weather
    print("🌤️  WEATHER")
    print()
    print("   Mississauga:")
    print(f"   {get_weather('Mississauga,Canada')}")
    print()
    print("   Pearson Airport (YYZ):")
    print(f"   {get_weather('YYZ')}")
    print()
    print("=" * 60)
    print()
    
    # News (placeholder)
    print("📰 NEWS HEADLINES")
    print()
    print("   🇨🇦 CANADA - TOP 3")
    print("   Without news API, check:")
    print("   • CBC.ca - https://www.cbc.ca/news")
    print("   • Globe and Mail - https://www.theglobeandmail.com")
    print("   • CTV News - https://www.ctvnews.ca")
    print()
    print("   🇺🇸 USA - TOP 3")
    print("   Without news API, check:")
    print("   • Reuters - https://www.reuters.com")
    print("   • AP News - https://apnews.com")
    print("   • NPR - https://www.npr.org")
    print()
    print("=" * 60)
    print()
    
    # Stock Market (placeholder)
    print("📈 STOCK MARKET OUTLOOK")
    print()
    print("   Without market API, check:")
    print("   • Yahoo Finance - https://finance.yahoo.com")
    print("   • Bloomberg - https://www.bloomberg.com/markets")
    print("   • TSX - https://money.tmx.com")
    print()
    print("   Looking for: S&P 500, TSX, Dow Jones trends")
    print()
    print("=" * 60)
    print()
    
    # Calendar check (if racing day)
    day_name = now.strftime('%A')
    if day_name in ['Thursday', 'Friday', 'Saturday', 'Sunday']:
        print("🏇 RACING SCHEDULE")
        print(f"   Today is {day_name} - Gulfstream racing day!")
        print("   Scratches available at noon.")
        print()
        print("=" * 60)
        print()
    
    print(f"✅ Briefing complete - {now.strftime('%I:%M %p')}")
    print()
    print("💡 TIP: Get Brave Search API for live news/market data")

if __name__ == "__main__":
    main()
