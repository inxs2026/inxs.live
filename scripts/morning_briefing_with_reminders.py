#!/usr/bin/env python3
"""
The Daily Brief - Morning Briefing for Carlo
Generates a newspaper-style HTML file and sends it as a Telegram attachment.
"""
import subprocess
import datetime
import json
import xml.etree.ElementTree as ET
import re
import os
import sys
import urllib.request
import html as html_lib

# ─────────────────────────────────────────────
# DATA FETCHERS
# ─────────────────────────────────────────────

def get_weather(lat, lon, location_name):
    """Get weather from Open-Meteo (no API key needed)"""
    try:
        url = (f"https://api.open-meteo.com/v1/forecast"
               f"?latitude={lat}&longitude={lon}"
               f"&current_weather=true&temperature_unit=celsius"
               f"&windspeed_unit=kmh&timezone=America/Toronto")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        current = data.get('current_weather', {})
        temp = current.get('temperature', 'N/A')
        windspeed = current.get('windspeed', 'N/A')
        wmo_codes = {
            0: ('Clear', '☀️'), 1: ('Mainly clear', '🌤️'), 2: ('Partly cloudy', '⛅'),
            3: ('Overcast', '☁️'), 45: ('Foggy', '🌫️'), 48: ('Foggy', '🌫️'),
            51: ('Light drizzle', '🌦️'), 53: ('Drizzle', '🌦️'), 55: ('Heavy drizzle', '🌧️'),
            61: ('Light rain', '🌧️'), 63: ('Rain', '🌧️'), 65: ('Heavy rain', '🌧️'),
            71: ('Light snow', '🌨️'), 73: ('Snow', '🌨️'), 75: ('Heavy snow', '🌨️'),
            80: ('Rain showers', '🌦️'), 95: ('Thunderstorm', '⛈️'),
        }
        code = current.get('weathercode', 0)
        desc, icon = wmo_codes.get(code, ('Unknown', '🌤️'))
        return {'location': location_name, 'desc': desc, 'icon': icon,
                'temp': temp, 'wind': windspeed}
    except Exception:
        return {'location': location_name, 'desc': 'Unavailable', 'icon': '❓',
                'temp': 'N/A', 'wind': 'N/A'}


def get_rss(url, count=6):
    """Fetch RSS headlines with links"""
    try:
        result = subprocess.run(
            ['curl', '-s', '-L', '-A', 'Mozilla/5.0', url, '--max-time', '10'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0 or not result.stdout.strip():
            return []
        root = ET.fromstring(result.stdout)
        items = []
        # RSS 2.0
        for item in root.findall('.//item')[:count]:
            t = item.find('title')
            l = item.find('link')
            if t is not None and t.text:
                title = t.text.strip()
                link = l.text.strip() if l is not None and l.text else '#'
                items.append((title, link))
        # Atom fallback
        if not items:
            ns = '{http://www.w3.org/2005/Atom}'
            for e in root.findall(f'.//{ns}entry')[:count]:
                t = e.find(f'{ns}title')
                l = e.find(f'{ns}link')
                if t is not None and t.text:
                    link = l.get('href', '#') if l is not None else '#'
                    items.append((t.text.strip(), link))
        return items
    except Exception:
        return []


def get_market_data():
    """Fetch market data from Yahoo Finance (free, no key)"""
    symbols = {
        '^GSPC':    ('S&P 500',  ''),
        '^IXIC':    ('NASDAQ',   ''),
        '^DJI':     ('DOW',      ''),
        '^GSPTSE':  ('TSX',      ''),
        'CL=F':     ('Oil (WTI)',''),
        'GC=F':     ('Gold',     ''),
        'CADUSD=X': ('CAD/USD',  ''),
    }
    results = []
    now = datetime.datetime.now()
    is_weekend = now.weekday() >= 5
    label_suffix = ' (Fri)' if is_weekend else ''

    for sym, (name, _) in symbols.items():
        try:
            url = f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read())
            meta = data['chart']['result'][0]['meta']
            price = meta.get('regularMarketPrice', 0)
            prev  = meta.get('chartPreviousClose') or meta.get('previousClose', price)
            if prev and prev != 0:
                change_pct = ((price - prev) / prev) * 100
            else:
                change_pct = 0
            # Format price
            if sym == 'CADUSD=X':
                price_str = f'{price:.4f}'
            elif price > 1000:
                price_str = f'{price:,.0f}'
            else:
                price_str = f'{price:.2f}'
            results.append({
                'name': name + label_suffix,
                'price': price_str,
                'change': change_pct,
                'positive': change_pct >= 0,
            })
        except Exception:
            results.append({'name': name, 'price': 'N/A', 'change': 0.0, 'positive': True})

    return results


def get_reminders():
    """Get today's reminders from memory files"""
    reminders = []
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    for path in [
        os.path.expanduser('~/.openclaw/workspace/memory/reminders.md'),
        os.path.expanduser('~/.openclaw/workspace/memory/active-tasks.md'),
    ]:
        if not os.path.exists(path):
            continue
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '```' in line:
                        continue
                    if any(x in line for x in ['**', 'Format Example', 'Add reminders', 'Your Reminder']):
                        continue
                    if today in line or '[urgent]' in line.lower() or '[today]' in line.lower():
                        cleaned = re.sub(r'^[\-\*\d\.\[\] ]+', '', line).strip()
                        if cleaned and len(cleaned) > 5 and cleaned not in reminders:
                            reminders.append(cleaned)
        except Exception:
            pass
    return reminders


# ─────────────────────────────────────────────
# HTML BUILDER
# ─────────────────────────────────────────────

def esc(text):
    """Escape text for HTML"""
    return html_lib.escape(str(text))


def build_html(now, weather_data, reminders, ca_news, us_news, mkt_news, markets, is_race_day):
    date_str   = now.strftime('%A, %B %-d, %Y')
    time_str   = now.strftime('%I:%M %p EST')
    edition    = now.strftime('%A') + ' Morning Edition'
    day_name   = now.strftime('%A')

    # ── Reminder rows
    reminder_html = ''
    if reminders:
        items = ''.join(f'<li>🔔 {esc(r)}</li>' for r in reminders)
        reminder_html = f'''
        <div class="section reminder-box">
            <div class="section-title">⏰ Reminders</div>
            <ul class="reminder-list">{items}</ul>
        </div>'''

    # ── Canada news rows
    ca_rows = ''
    for i, (title, link) in enumerate(ca_news):
        cls = 'lead-story' if i == 0 else 'headline-item'
        if i == 0:
            ca_rows += f'''
            <div class="{cls}">
                <h2><a href="{esc(link)}">{esc(title)}</a></h2>
            </div>'''
        else:
            ca_rows += f'<div class="{cls}"><a href="{esc(link)}">{esc(title)}</a></div>'

    # ── USA news rows
    us_rows = ''.join(
        f'<div class="headline-item"><a href="{esc(link)}">{esc(title)}</a></div>'
        for title, link in us_news
    )

    # ── Market rows
    market_rows = ''
    for m in markets:
        sign   = '+' if m['positive'] else ''
        cls    = 'positive' if m['positive'] else 'negative'
        change = f'{sign}{m["change"]:.2f}%'
        market_rows += f'''
        <div class="market-item">
            <span class="market-name">{esc(m["name"])}</span>
            <span class="{cls}">{change}</span>
        </div>'''

    # ── Market headlines
    mkt_rows = ''.join(
        f'<div class="headline-item"><a href="{esc(link)}">{esc(title)}</a></div>'
        for title, link in mkt_news[:3]
    )

    # ── Weather rows
    weather_rows = ''
    for w in weather_data:
        weather_rows += f'''
        <div class="weather-item">
            <span class="weather-icon">{w["icon"]}</span>
            <span class="weather-place">{esc(w["location"])}</span>
            <span class="weather-temp">{esc(str(w["temp"]))}°C</span>
            <span class="weather-desc">{esc(w["desc"])}</span>
            <span class="weather-wind">💨 {esc(str(w["wind"]))} km/h</span>
        </div>'''

    # ── Racing box
    racing_html = ''
    if is_race_day:
        racing_html = f'''
        <div class="section sports-box">
            <div class="section-title">🏇 Racing</div>
            <div class="sports-content">
                <div class="race-day">{esc(day_name)}</div>
                <div class="race-track">Gulfstream Park</div>
                <div class="race-note">Scratches available at noon<br>First post ~12:20 PM</div>
            </div>
        </div>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Daily Brief — {esc(date_str)}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            background: #f4f1ea;
            color: #1a1a1a;
            line-height: 1.5;
            padding: 20px;
        }}
        .container {{
            max-width: 960px;
            margin: 0 auto;
            background: #fff;
            box-shadow: 0 2px 24px rgba(0,0,0,0.12);
        }}
        /* ── Header */
        .header {{
            text-align: center;
            border-bottom: 4px double #000;
            padding: 22px 20px 16px;
        }}
        .masthead {{
            font-size: 52px;
            font-weight: 900;
            letter-spacing: 8px;
            text-transform: uppercase;
            border-bottom: 3px solid #000;
            padding-bottom: 10px;
            margin-bottom: 8px;
        }}
        .edition {{ font-size: 13px; text-transform: uppercase; letter-spacing: 2px; color: #444; }}
        .date-line {{ font-size: 13px; font-style: italic; color: #666; margin-top: 4px; }}

        /* ── Layout */
        .main-content {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 0;
            padding: 0;
        }}
        .left-column  {{ padding: 20px; border-right: 1px solid #ccc; }}
        .right-column {{ padding: 20px; }}

        /* ── Sections */
        .section {{ margin-bottom: 22px; }}
        .section-title {{
            font-size: 13px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2px;
            border-bottom: 2px solid #000;
            padding-bottom: 5px;
            margin-bottom: 10px;
        }}

        /* ── Reminder box */
        .reminder-box {{
            background: #fff8e7;
            border: 1px solid #f0c040;
            border-left: 4px solid #f0a000;
            padding: 12px 14px;
            margin-bottom: 18px;
            border-radius: 2px;
        }}
        .reminder-box .section-title {{ border-bottom-color: #f0a000; }}
        .reminder-list {{ list-style: none; padding: 0; }}
        .reminder-list li {{ font-size: 15px; padding: 3px 0; font-weight: 600; }}

        /* ── News */
        .lead-story {{ margin-bottom: 12px; }}
        .lead-story h2 {{ font-size: 26px; font-weight: 700; line-height: 1.2; }}
        .lead-story h2 a {{ color: #1a1a1a; text-decoration: none; }}
        .lead-story h2 a:hover {{ text-decoration: underline; }}
        .headline-item {{
            font-size: 15px;
            font-weight: 600;
            padding: 6px 0;
            border-bottom: 1px solid #eee;
        }}
        .headline-item:last-child {{ border-bottom: none; }}
        .headline-item a {{ color: #1a1a1a; text-decoration: none; }}
        .headline-item a:hover {{ text-decoration: underline; color: #333; }}

        /* ── Markets */
        .market-box {{
            background: #1a1a1a;
            color: #fff;
            padding: 14px;
            border-radius: 2px;
        }}
        .market-box .section-title {{ color: #ccc; border-bottom-color: #444; }}
        .market-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 0;
            border-bottom: 1px solid #2e2e2e;
            font-size: 14px;
        }}
        .market-item:last-child {{ border-bottom: none; }}
        .market-name {{ color: #ddd; }}
        .positive {{ color: #4caf50; font-weight: 600; }}
        .negative {{ color: #f44336; font-weight: 600; }}

        /* ── Weather */
        .weather-box {{
            background: #e8f4fd;
            border: 1px solid #b3d7f0;
            padding: 12px 14px;
            border-radius: 2px;
        }}
        .weather-box .section-title {{ border-bottom-color: #4a90d9; color: #1a3a5c; }}
        .weather-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 5px 0;
            font-size: 14px;
            border-bottom: 1px solid #cce0f0;
        }}
        .weather-item:last-child {{ border-bottom: none; }}
        .weather-icon {{ font-size: 20px; }}
        .weather-place {{ font-weight: 600; flex: 1; }}
        .weather-temp {{ font-size: 18px; font-weight: 700; color: #1a3a5c; }}
        .weather-desc {{ color: #555; font-style: italic; }}
        .weather-wind {{ color: #777; font-size: 12px; }}

        /* ── Sports / Racing */
        .sports-box {{
            background: #1a3a5c;
            color: #fff;
            padding: 14px;
            border-radius: 2px;
        }}
        .sports-box .section-title {{ color: #9ecfef; border-bottom-color: #4a90d9; }}
        .sports-content {{ text-align: center; padding: 10px 0; }}
        .race-day {{ font-size: 22px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; }}
        .race-track {{ font-size: 15px; color: #9ecfef; margin: 4px 0; }}
        .race-note {{ font-size: 13px; color: #aaa; margin-top: 6px; line-height: 1.6; }}

        /* ── Market news */
        .mkt-news-box .headline-item {{ font-size: 13px; }}

        /* ── Footer */
        .footer {{
            border-top: 2px solid #000;
            padding: 12px 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}

        @media (max-width: 700px) {{
            .main-content {{ grid-template-columns: 1fr; }}
            .left-column {{ border-right: none; border-bottom: 1px solid #ccc; }}
            .masthead {{ font-size: 34px; letter-spacing: 4px; }}
        }}
    </style>
</head>
<body>
<div class="container">

    <header class="header">
        <div class="masthead">The Daily Brief</div>
        <div class="edition">{esc(edition)}</div>
        <div class="date-line">{esc(date_str)}</div>
    </header>

    <div class="main-content">

        <!-- LEFT COLUMN -->
        <div class="left-column">
            {reminder_html}

            <div class="section">
                <div class="section-title">🇨🇦 Canada</div>
                {ca_rows if ca_rows else '<div class="headline-item">Headlines unavailable</div>'}
            </div>

            <div class="section">
                <div class="section-title">🇺🇸 United States</div>
                {us_rows if us_rows else '<div class="headline-item">Headlines unavailable</div>'}
            </div>
        </div>

        <!-- RIGHT COLUMN -->
        <div class="right-column">

            <div class="section market-box">
                <div class="section-title">📈 Markets</div>
                {market_rows}
            </div>

            <div class="section weather-box">
                <div class="section-title">🌤️ Weather</div>
                {weather_rows}
            </div>

            {racing_html}

            <div class="section mkt-news-box">
                <div class="section-title">📰 Market News</div>
                {mkt_rows if mkt_rows else '<div class="headline-item">Unavailable</div>'}
            </div>

        </div>
    </div>

    <footer class="footer">
        Generated {esc(time_str)} &nbsp;|&nbsp;
        Sources: CBC, NBC News, MarketWatch, Yahoo Finance, Open-Meteo
    </footer>

</div>
</body>
</html>'''


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    test_mode = '--test' in sys.argv
    now = datetime.datetime.now()
    day_name = now.strftime('%A')
    is_race_day = day_name in ('Thursday', 'Friday', 'Saturday', 'Sunday')

    print(f'[{now.strftime("%H:%M")}] Fetching data...', flush=True)

    # Fetch all data
    weather_data = [
        get_weather(43.5890, -79.6441, 'Mississauga'),
        get_weather(43.6777, -79.6248, 'Pearson (YYZ)'),
    ]

    reminders = get_reminders()

    ca_news = get_rss('https://www.cbc.ca/webfeed/rss/rss-topstories', 6)

    us_news = []
    for feed in ['https://feeds.nbcnews.com/nbcnews/public/news',
                 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml']:
        us_news = get_rss(feed, 4)
        if us_news:
            break

    mkt_news = []
    for feed in ['https://feeds.marketwatch.com/marketwatch/topstories/',
                 'https://feeds.finance.yahoo.com/rss/topfinstories']:
        mkt_news = get_rss(feed, 3)
        if mkt_news:
            break

    markets = get_market_data()

    print(f'[{now.strftime("%H:%M")}] Building HTML...', flush=True)

    html_content = build_html(now, weather_data, reminders, ca_news, us_news,
                              mkt_news, markets, is_race_day)

    out_path = os.path.expanduser('~/.openclaw/workspace/morning_briefing.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f'[{now.strftime("%H:%M")}] Saved to {out_path}', flush=True)

    if test_mode:
        print('✅ Test mode — skipping Telegram send.')
        return

    # Send as Telegram file attachment
    print(f'[{now.strftime("%H:%M")}] Sending to Telegram...', flush=True)
    date_label = now.strftime('%A, %B %-d, %Y')
    caption = f'📰 The Daily Brief — {date_label}'

    result = subprocess.run(
        ['openclaw', 'message', 'send',
         '--channel', 'telegram',
         '--target', '1626341499',
         '--media', out_path,
         '--message', caption],
        capture_output=True, text=True, timeout=30
    )

    if result.returncode == 0:
        print(f'✅ Morning briefing sent successfully.')
    else:
        print(f'❌ Send failed: {result.stderr or result.stdout}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
