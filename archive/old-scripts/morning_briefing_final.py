#!/usr/bin/env python3
"""
Complete Daily Morning Briefing for Carlo
- Weather (Open-Meteo API - free)
- News headlines (RSS feeds - free)
- Stock market (Yahoo Finance - free)
"""
import subprocess
import datetime
import json
import xml.etree.ElementTree as ET

def get_weather(lat, lon, location_name):
    """Get weather from Open-Meteo"""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&temperature_unit=celsius&windspeed_unit=kmh&timezone=America/Toronto"
        
        result = subprocess.run(
            ['curl', '-s', url, '--max-time', '10'],
            capture_output=True, text=True, timeout=15
        )
        
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            current = data.get('current_weather', {})
            
            temp = current.get('temperature', 'N/A')
            windspeed = current.get('windspeed', 'N/A')
            
            wmo_codes = {
                0: '☀️ Clear', 1: '🌤️ Mainly clear', 2: '⛅ Partly cloudy',
                3: '☁️ Overcast', 45: '🌫️ Foggy', 48: '🌫️ Foggy',
                51: '🌦️ Light drizzle', 53: '🌦️ Drizzle', 55: '🌧️ Heavy drizzle',
                61: '🌧️ Light rain', 63: '🌧️ Rain', 65: '🌧️ Heavy rain',
                71: '🌨️ Light snow', 73: '🌨️ Snow', 75: '🌨️ Heavy snow',
                80: '🌦️ Rain showers', 95: '⛈️ Thunderstorm'
            }
            
            weather_code = current.get('weathercode', 0)
            condition = wmo_codes.get(weather_code, '🌤️')
            
            return f"{location_name}: {condition} {temp}°C | Wind: {windspeed} km/h"
        
        return f"{location_name}: Weather unavailable"
    except:
        return f"{location_name}: Error"

def get_rss_headlines(url, count=3):
    """Fetch RSS feed headlines"""
    try:
        result = subprocess.run(
            ['curl', '-s', '-L', '-A', 'Mozilla/5.0', url, '--max-time', '10'],
            capture_output=True, text=True, timeout=15
        )
        
        if result.returncode != 0 or not result.stdout:
            return []
        
        root = ET.fromstring(result.stdout)
        headlines = []
        
        # RSS 2.0
        for item in root.findall('.//item')[:count]:
            title = item.find('title')
            if title is not None and title.text:
                headlines.append(title.text.strip())
        
        # Atom
        if not headlines:
            for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry')[:count]:
                title = entry.find('{http://www.w3.org/2005/Atom}title')
                if title is not None and title.text:
                    headlines.append(title.text.strip())
        
        return headlines
    except:
        return []

def get_market_data():
    """Get stock market overview (simplified without API)"""
    # Note: Without API, we show a basic message
    # Yahoo Finance API would require key or scraping
    return """   Check current status:
   • S&P 500, TSX, Dow Jones
   • Quick view: https://finance.yahoo.com"""

def main():
    """Generate complete morning briefing"""
    now = datetime.datetime.now()
    
    print(f"📅 MORNING BRIEFING - {now.strftime('%A, %B %d, %Y')}")
    print("=" * 60)
    print()
    
    # Weather
    print("🌤️  WEATHER")
    print()
    print("   " + get_weather(43.5890, -79.6441, 'Mississauga'))
    print("   " + get_weather(43.6777, -79.6248, 'Pearson Airport (YYZ)'))
    print()
    print("=" * 60)
    print()
    
    # Canada News
    print("🇨🇦 CANADA NEWS - TOP 3")
    print()
    cbc = get_rss_headlines('https://www.cbc.ca/webfeed/rss/rss-topstories', 3)
    if cbc:
        for i, headline in enumerate(cbc, 1):
            print(f"   {i}. {headline}")
    else:
        print("   • Unable to fetch headlines")
    print()
    
    # USA News
    print("🇺🇸 USA NEWS - TOP 3")
    print()
    us_feeds = [
        'https://feeds.nbcnews.com/nbcnews/public/news',
        'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
    ]
    
    us_headlines = []
    for feed in us_feeds:
        us_headlines = get_rss_headlines(feed, 3)
        if us_headlines:
            break
    
    if us_headlines:
        for i, headline in enumerate(us_headlines, 1):
            print(f"   {i}. {headline}")
    else:
        print("   • Unable to fetch headlines")
    print()
    print("=" * 60)
    print()
    
    # Stock Market
    print("📈 STOCK MARKET OUTLOOK")
    print()
    print(get_market_data())
    print()
    print("=" * 60)
    print()
    
    # Racing Schedule
    day_name = now.strftime('%A')
    if day_name in ['Thursday', 'Friday', 'Saturday', 'Sunday']:
        print("🏇 RACING SCHEDULE")
        print(f"   Today is {day_name} - Gulfstream racing day!")
        print("   Scratches available at noon.")
        print()
        print("=" * 60)
        print()
    
    print(f"✅ Briefing complete - {now.strftime('%I:%M %p')}")

if __name__ == "__main__":
    main()
