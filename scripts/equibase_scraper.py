#!/usr/bin/env python3
"""
Equibase Entry Scraper for Gulfstream Park (and other tracks).
Usage: ~/scraping_env/bin/python3 scripts/equibase_scraper.py [--track GP] [--date YYYY-MM-DD]

Uses Playwright with real Chrome to bypass Imperva bot protection.
"""

import sys
import os
import json
import argparse
import re
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Use venv site-packages
sys.path.insert(0, '/home/damato/scraping_env/lib/python3.12/site-packages')

from bs4 import BeautifulSoup

WORKSPACE = Path('/home/damato/.openclaw/workspace')
ET = ZoneInfo('America/Toronto')
CHROME_PATH = '/usr/bin/google-chrome'

TRACK_NAMES = {
    'GP': 'GULFSTREAM PARK',
    'AQU': 'AQUEDUCT',
    'SA': 'SANTA ANITA',
    'KEE': 'KEENELAND',
    'CD': 'CHURCHILL DOWNS',
}


def build_url(track: str, date: datetime) -> str:
    """Build Equibase static entry URL."""
    mmddyy = date.strftime('%m%d%y')
    return f"https://www.equibase.com/static/entry/{track}{mmddyy}USA-EQB.html"


def fetch_page_html(url: str) -> str:
    """
    Fetch Equibase page using Playwright + real Chrome.
    Removes webdriver property to bypass Imperva bot detection.
    Waits for networkidle to ensure JS challenge resolves.
    """
    from playwright.sync_api import sync_playwright

    print(f"  Launching browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH,
            args=['--no-sandbox', '--disable-dev-shm-usage'],
        )
        ctx = browser.new_context(
            user_agent=(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/121.0.0.0 Safari/537.36'
            ),
            java_script_enabled=True,
        )
        # Bypass webdriver detection
        ctx.add_init_script(
            'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        )
        page = ctx.new_page()

        print(f"  Loading: {url}")
        try:
            page.goto(url, wait_until='networkidle', timeout=90000)
        except Exception as e:
            if 'Timeout' in str(e):
                print(f"  ⚠️  networkidle timeout — grabbing current page state")
            else:
                raise

        # Extra wait to ensure JS fully renders
        time.sleep(5)
        html = page.content()
        browser.close()

    return html


def parse_race_section(race_div) -> dict | None:
    """Parse a single race div (id=Race1, Race2, ...) into structured data."""
    # Race number from div id
    div_id = race_div.get('id', '')
    race_num_match = re.match(r'Race(\d+)', div_id)
    if not race_num_match:
        return None
    race_num = int(race_num_match.group(1))

    # Race info (conditions, post time)
    race_info = race_div.find('div', class_='race-info')
    race_type = ''
    purse = ''
    details = ''
    post_time = 'TBD'

    if race_info:
        h3 = race_info.find('h3')
        h5 = race_info.find('h5')
        if h3:
            race_type = h3.get_text(strip=True)
        if h5:
            h5_text = h5.get_text(' ', strip=True)
            # Extract post time
            pt_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM)\s*ET)', h5_text, re.I)
            if pt_match:
                post_time = pt_match.group(1).strip()
            # Clean up h5 text for details (remove post time)
            details = re.sub(r'\d{1,2}:\d{2}\s*(?:AM|PM)\s*ET', '', h5_text).strip()
            details = re.sub(r'\s+', ' ', details).strip(' .')

    # Build conditions string
    conditions_parts = [p for p in [race_type, details] if p]
    conditions = ' - '.join(conditions_parts) if conditions_parts else 'N/A'

    # Parse entries from contenders div
    entries = []
    contenders = race_div.find('div', class_='contenders')
    if contenders:
        entry_rows = contenders.find_all('div', class_='row', recursive=False)
        for row in entry_rows:
            entry = parse_entry_row(row)
            if entry:
                entries.append(entry)

    return {
        'race_num': race_num,
        'conditions': conditions,
        'post_time': post_time,
        'entries': entries,
    }


def parse_entry_row(row) -> dict | None:
    """Parse a single entry row div."""
    # Post position from saddlecloth div
    saddlecloth = row.find('div', class_=re.compile(r'saddlecloth-\d+'))
    if not saddlecloth:
        return None
    pp_text = saddlecloth.get_text(strip=True)
    # Handle coupled entries like "1A"
    pp_match = re.match(r'^(\d+)', pp_text.strip())
    if not pp_match:
        return None
    pp = int(pp_match.group(1))

    # Horse name from h4 > b > a
    h4 = row.find('h4')
    if not h4:
        return None
    horse_link = h4.find('a')
    horse = horse_link.get_text(strip=True) if horse_link else h4.find('b').get_text(strip=True) if h4.find('b') else ''
    # Remove country suffix like "(KY)"
    horse = re.sub(r'\s*\([A-Z]{2,3}\)\s*$', '', horse).strip()

    # Morning line odds from "M/L Odds: X/Y" or mobileOdds span
    morning_line = 'N/A'
    # Try the M/L Odds text first (most reliable)
    row_text = row.get_text(' ', strip=True)
    ml_match = re.search(r'M/L Odds:\s*([\d/]+|Even|MTO)', row_text, re.I)
    if ml_match:
        morning_line = ml_match.group(1)
    else:
        # Fallback: live-odds span
        odds_span = row.find('span', class_=re.compile(r'mobileOdds-\d'))
        if odds_span:
            morning_line = odds_span.get_text(strip=True)

    # Jockey
    jockey = ''
    jockey_div = row.find('div', string=re.compile(r'Jockey:', re.I))
    if not jockey_div:
        # Find div containing "Jockey:" text
        for div in row.find_all('div', class_='col-xs-12'):
            if 'Jockey:' in div.get_text():
                jockey_div = div
                break
    if jockey_div:
        jockey_link = jockey_div.find('a')
        if jockey_link:
            jockey = jockey_link.get_text(strip=True)
        else:
            jockey = jockey_div.get_text(strip=True).replace('Jockey:', '').strip()

    # Trainer
    trainer = ''
    for div in row.find_all('div', class_='col-xs-12'):
        div_text = div.get_text()
        if 'Trainer:' in div_text:
            trainer_link = div.find('a')
            if trainer_link:
                trainer = trainer_link.get_text(strip=True)
            else:
                trainer = div_text.replace('Trainer:', '').strip()
            break

    # Scratch detection — look for scratch class or "SCR" in text
    row_classes = ' '.join(row.get('class', []))
    is_scratched = (
        'scratch' in row_classes.lower() or
        bool(re.search(r'\bSCR\b|\bScratched\b', row_text, re.I))
    )

    return {
        'pp': pp,
        'horse': horse.upper(),
        'jockey': jockey,
        'trainer': trainer,
        'morning_line': morning_line,
        'scratched': is_scratched,
    }


def parse_entries_page(html: str, track: str, date: datetime) -> dict:
    """Parse the full Equibase entries HTML page."""
    soup = BeautifulSoup(html, 'html.parser')

    # Find all race divs (id=Race1, Race2, ...)
    race_divs = soup.find_all('div', id=re.compile(r'^Race\d+$'))

    if not race_divs:
        page_title = soup.title.string if soup.title else 'unknown'
        print(f"  ⚠️  No race divs found. Page title: {page_title}")
        print(f"  Page length: {len(html)} chars")
        return {
            'track': track,
            'date': date.strftime('%Y-%m-%d'),
            'generated': datetime.now(ET).isoformat(timespec='seconds'),
            'total_races': 0,
            'scratches': [],
            'races': [],
            '_parse_warning': f'No race sections found (page title: {page_title}). Page may be blocked or structure changed.',
        }

    races = []
    scratches = []

    for race_div in race_divs:
        race_data = parse_race_section(race_div)
        if race_data:
            races.append(race_data)
            for entry in race_data['entries']:
                if entry['scratched']:
                    scratches.append(f"{entry['horse']} (Race {race_data['race_num']})")

    races.sort(key=lambda r: r['race_num'])

    return {
        'track': track,
        'date': date.strftime('%Y-%m-%d'),
        'generated': datetime.now(ET).isoformat(timespec='seconds'),
        'total_races': len(races),
        'scratches': scratches,
        'races': races,
    }


def save_outputs(data: dict, date: datetime):
    """Save JSON and scratches.txt to racing/picks/MMMDD/."""
    month_day = date.strftime('%b%d').lower()  # e.g. "feb27"
    out_dir = WORKSPACE / 'racing' / 'picks' / month_day
    out_dir.mkdir(parents=True, exist_ok=True)

    # JSON
    json_path = out_dir / 'equibase_entries.json'
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n✅ JSON saved: {json_path}")

    # Scratches.txt
    scratches_path = out_dir / 'scratches.txt'
    now_str = datetime.now(ET).strftime('%I:%M %p')
    date_str = date.strftime('%B %d, %Y')
    track_name = TRACK_NAMES.get(data['track'], data['track'])

    lines = [
        f"{track_name} SCRATCHES - {date_str}",
        f"Generated: {now_str} ET",
        f"Source: Equibase.com",
        "",
        "=" * 60,
        f"{track_name} ({data['track']}) SCRATCHES:",
        "=" * 60,
    ]

    if data['scratches']:
        for s in data['scratches']:
            lines.append(s)
    else:
        lines.append("[NONE REPORTED]")

    lines += [
        "",
        "=" * 60,
        "NOTES:",
        "- Re-check scratches closer to post time for late changes",
        f"- Total {data['track']} races today: {data['total_races']}",
        "=" * 60,
    ]

    with open(scratches_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"✅ Scratches saved: {scratches_path}")

    return json_path, scratches_path


def print_summary(data: dict):
    """Print human-readable summary to stdout."""
    track_name = TRACK_NAMES.get(data['track'], data['track'])
    print(f"\n{'='*60}")
    print(f"  {track_name} ENTRIES — {data['date']}")
    print(f"  Generated: {data['generated']}")
    print(f"{'='*60}")
    print(f"  Total Races: {data['total_races']}")

    if data['scratches']:
        print(f"\n  SCRATCHES ({len(data['scratches'])}):")
        for s in data['scratches']:
            print(f"    • {s}")
    else:
        print(f"\n  SCRATCHES: None reported")

    print()
    for race in data['races']:
        total = len(race['entries'])
        active = sum(1 for e in race['entries'] if not e['scratched'])
        print(f"  Race {race['race_num']:>2}  {race['post_time']:<14}  {race['conditions'][:55]}")
        for e in race['entries']:
            scr = ' [SCR]' if e['scratched'] else ''
            print(f"         {e['pp']:>2}. {e['horse']:<28} {e['morning_line']:>5}  {e['jockey']}{scr}")
        print()

    if '_parse_warning' in data:
        print(f"  ⚠️  WARNING: {data['_parse_warning']}")

    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description='Equibase Entry Scraper')
    parser.add_argument('--track', default='GP', help='Track code (default: GP)')
    parser.add_argument('--date', default=None, help='Date YYYY-MM-DD (default: today ET)')
    args = parser.parse_args()

    if args.date:
        date = datetime.strptime(args.date, '%Y-%m-%d').replace(tzinfo=ET)
    else:
        date = datetime.now(ET)

    track = args.track.upper()
    url = build_url(track, date)

    print(f"\n🏇 Equibase Scraper")
    print(f"   Track: {track}  |  Date: {date.strftime('%Y-%m-%d')}")
    print(f"   URL: {url}\n")

    try:
        html = fetch_page_html(url)
    except Exception as e:
        print(f"\n❌ Failed to fetch Equibase page: {e}")
        sys.exit(1)

    if len(html) < 5000:
        print(f"\n❌ Page seems too short ({len(html)} chars) — likely blocked or wrong URL.")
        print(f"   First 500 chars: {html[:500]}")
        sys.exit(1)

    print(f"  ✅ Page loaded ({len(html):,} chars). Parsing...")

    try:
        data = parse_entries_page(html, track, date)
    except Exception as e:
        print(f"\n❌ Parse error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    save_outputs(data, date)
    print_summary(data)

    if data['total_races'] == 0:
        print("⚠️  No races parsed — check page structure or URL.")
        sys.exit(1)

    print(f"\n✅ Done! {data['total_races']} races, {len(data['scratches'])} scratches.")


if __name__ == '__main__':
    main()
