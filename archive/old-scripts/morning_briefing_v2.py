#!/usr/bin/env python3
"""
Daily Morning Briefing for Carlo
Using Open-Meteo for reliable weather data
"""
import subprocess
import datetime
import json
import sys

def get_weather_openmeteo(lat, lon, location_name):
    """Get weather from Open-Meteo (free, no API key)"""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&temperature_unit=celsius&windspeed_unit=kmh&timezone=America/Toronto"
        
        result = subprocess.run(
            ['curl', '-s', url, '--max-time', '10'],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            current = data.get('current_weather', {})
            
            temp = current.get('temperature', 'N/A')
            windspeed = current.get('windspeed', 'N/A')
            
            # Weather codes
            wmo_codes = {
                0: '☀️ Clear', 1: '🌤️ Mainly clear', 2: '⛅ Partly cloudy',
                3: '☁️ Overcast', 45: '🌫️ Foggy', 48: '🌫️ Foggy',
                51: '🌦️ Light drizzle', 53: '🌦️ Drizzle', 55: '🌧️ Heavy drizzle',
                61: '🌧️ Light rain', 63: '🌧️ Rain', 65: '🌧️ Heavy rain',
                71: '🌨️ Light snow', 73: '🌨️ Snow', 75: '🌨️ Heavy snow',
                77: '🌨️ Snow grains', 80: '🌦️ Rain showers', 81: '🌧️ Rain showers',
                82: '⛈️ Heavy rain showers', 85: '🌨️ Snow showers', 86: '🌨️ Heavy snow showers',
                95: '⛈️ Thunderstorm', 96: '⛈️ Thunderstorm with hail', 99: '⛈️ Severe thunderstorm'
            }
            
            weather_code = current.get('weathercode', 0)
            condition = wmo_codes.get(weather_code, '🌤️ Unknown')
            
            return f"{location_name}: {condition} {temp}°C | Wind: {windspeed} km/h"
        
        return f"{location_name}: Weather unavailable"
        
    except Exception as e:
        return f"{location_name}: Error - {str(e)[:50]}"

def main():
    """Generate morning briefing"""
    now = datetime.datetime.now()
    
    briefing = f"""📅 MORNING BRIEFING - {now.strftime('%A, %B %d, %Y')}
{'=' * 60}

🌤️  WEATHER

   {get_weather_openmeteo(43.5890, -79.6441, 'Mississauga')}
   {get_weather_openmeteo(43.6777, -79.6248, 'Pearson Airport (YYZ)')}

{'=' * 60}

📰 NEWS HEADLINES

   🇨🇦 CANADA - TOP 3
   (News API not configured - manual check recommended)
   • CBC News: https://www.cbc.ca/news
   • Globe and Mail: https://www.theglobeandmail.com
   • Toronto Star: https://www.thestar.com

   🇺🇸 USA - TOP 3
   (News API not configured - manual check recommended)
   • Reuters: https://www.reuters.com
   • AP News: https://apnews.com
   • NPR: https://www.npr.org

{'=' * 60}

📈 STOCK MARKET OUTLOOK

   (Market API not configured - manual check recommended)
   • S&P 500 futures
   • TSX index
   • Dow Jones
   
   Quick check: https://finance.yahoo.com

{'=' * 60}
"""

    # Add racing schedule if Thu-Sun
    day_name = now.strftime('%A')
    if day_name in ['Thursday', 'Friday', 'Saturday', 'Sunday']:
        briefing += f"""
🏇 RACING SCHEDULE
   Today is {day_name} - Gulfstream racing day!
   Scratches available at noon.

{'=' * 60}
"""
    
    briefing += f"""
✅ Briefing complete - {now.strftime('%I:%M %p')}

💡 Add Brave Search API for automated news/market data
"""
    
    print(briefing)

if __name__ == "__main__":
    main()
