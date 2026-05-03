#!/usr/bin/env python3
"""
Equibase Horse Profiles — Charlie's Edition
==========================================
Pull full horse profiles from Equibase: career stats, race history, workouts,
connections, and pedigree info.

Usage (shell)
-------------
    python3 skills/equibase_profiles/equibase_profile.py --horse "Awesome Bourbon"
    python3 skills/equibase_profiles/equibase_profile.py --horse "Awesome Bourbon" --races 5
    python3 skills/equibase_profiles/equibase_profile.py --horse "Awesome Bourbon" --format json --output /tmp/horse.json

Usage (import)
--------------
    from skills.equibase_profiles.equibase_profile import get_profile, format_profile_table
    data = get_profile("Awesome Bourbon")
    print(format_profile_table(data))

Output Format (JSON)
-------------------
    {
      "success": true,
      "name": "Awesome Bourbon",
      "registry": "KY",
      "foaled": "April 21, 2020",
      "sex": "H", "color": "B",
      "sire": "NOT BOURBON - SEA THE AWESOME (IRE), BY SEA THE STARS (IRE)",
      "trainer": "Abraham R. Katryan",
      "jockey": "Pietro Moran",
      "owner": "Carlo D'Amato",
      "career_stats": {"starts": "21", "wins": "6", "seconds": "7", "thirds": "3", "earnings": "$304,944", "best": "108"},
      "yearly_stats": [...],
      "race_history": [
        {"date": "11/15/2025", "track": "Woodbine", "race": "10",
         "type": "bet365 Kennedy Road Stakes (Gr. 2)", "finish": "2", "beyer": "101"},
        ...
      ],
      "workouts": ["Apr 30 WO 5f 1:01.4 B"],
      "stakes_class": "Graded Stakes Placed",
      "url": "https://www.equibase.com/profiles/Results.cfm?type=Horse&refno=10795115&registry=T"
    }

Dependencies
------------
  Hermes venv Python (playwright already installed):
    ~/.hermes/hermes-agent/venv/bin/python

Notes
-----
- Imperva anti-bot may cause delays; re-run with --visible if blocked
- Race history is tab-separated on the page: Track | Date | Race# | Type | Breed | Finish | Beyer
- Workouts come from the Workouts tab
"""

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HERMES_PYTHON = "/home/damato/.hermes/hermes-agent/venv/bin/python"
OUTPUT_DIR = "/home/damato/.openclaw/workspace/horses"

KNOWN_TRACKS = {
    'Woodbine', 'Gulfstream', 'Tampa Bay', 'Belmont', 'Churchill',
    'Santa Anita', 'Aqueduct', 'Saratoga', 'Keeneland', 'Del Mar',
    'Laurel', 'Parx', 'Hawthorne', 'Remington', 'Sam Houston',
    'Century Mile', 'Mountaineer', 'Mahvek', 'Will Rogers',
    'Los Alamitos', 'Prairie Meadows', 'Finger Lakes', 'Thistledown',
    'Charles Town', 'Mountaineer', 'Delta Downs',
}

# ---------------------------------------------------------------------------
# Browser Helpers
# ---------------------------------------------------------------------------

def _launch_browser(headless: bool = True):
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.launch(
        headless=headless,
        args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu',
              '--window-size=1400,1200']
    )
    context = browser.new_context(
        viewport={'width': 1400, 'height': 1200},
        user_agent=(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/122.0.0.0 Safari/537.36'
        ),
        locale='en-US',
    )
    context.set_extra_http_headers({
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    })
    return pw, browser, context


def _clear_modals(page):
    """Remove cookie consent modal if present."""
    try:
        page.evaluate('document.querySelector("#uniccmp")?.remove()')
        time.sleep(1)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Core Profile Fetch
# ---------------------------------------------------------------------------

def get_profile(
    horse_name: str,
    races_limit: Optional[int] = None,
    headless: bool = True,
) -> Dict:
    """
    Pull a complete Equibase horse profile.

    Args:
        horse_name:   Name of the horse
        races_limit:  Limit race history to last N races (None = all)
        headless:     Hide browser window

    Returns:
        Dict with keys: success, name, registry, foaled, sex, color,
        sire, trainer, jockey, owner, career_stats, yearly_stats,
        race_history, workouts, stakes_class, last_sale, url, refno
    """
    pw, browser, context = None, None, None

    try:
        pw, browser, context = _launch_browser(headless=headless)
        page = context.new_page()

        # Step 1: Clear Imperva on main page
        page.goto('https://www.equibase.com/', wait_until='networkidle', timeout=60000)
        time.sleep(4)
        _clear_modals(page)

        # Step 2: Navigate to horse search
        page.goto(
            'https://www.equibase.com/premium/eqpHorseLookup.cfm?SAP=TN',
            timeout=30000
        )
        time.sleep(4)
        _clear_modals(page)

        # Step 3: Search for horse by name
        search_box = page.query_selector('input[type=text]')
        if not search_box:
            return {'success': False, 'error': 'No search box found'}

        search_box.fill(horse_name)
        page.keyboard.press('Enter')
        time.sleep(8)
        _clear_modals(page)

        # Step 4: Verify we're on a horse profile
        if 'Horse Profile for' not in page.title():
            return {
                'success': False,
                'error': f"Not a horse profile page: {page.title()}"
            }

        profile_url = page.url
        refno = _extract_refno(profile_url)

        # Step 5: Extract basic profile data
        result = _extract_profile_data(page)
        result['url'] = profile_url
        result['refno'] = refno

        # Step 6: Get race history
        races = _get_race_history(page)
        if races_limit:
            races = races[:races_limit]
        result['race_history'] = races

        # Step 7: Get workouts
        result['workouts'] = _get_workouts(page)

        result['success'] = True
        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

    finally:
        if page:
            page.close()
        if context:
            context.close()
        if browser:
            browser.close()
        if pw:
            pw.stop()


def _extract_refno(url: str) -> str:
    m = re.search(r'refno=(\d+)', url)
    return m.group(1) if m else ''


def _extract_profile_data(page) -> Dict:
    """Extract basic info, connections, and yearly stats from the Statistics tab."""
    text = page.inner_text('body')
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    result = {
        'name': '', 'registry': '', 'foaled': '', 'sex': '', 'color': '',
        'sire': '', 'dam': '', 'breeder': '',
        'trainer': '', 'jockey': '', 'owner': '',
        'career_stats': {}, 'yearly_stats': [],
        'stakes_class': '', 'last_sale': {},
    }

    # Horse name from title
    title = page.title()
    if 'Horse Profile for' in title:
        result['name'] = title.split('Horse Profile for')[1].split('|')[0].strip()

    # Parse each meaningful line
    for i, line in enumerate(lines):
        # Registry from name: "Awesome Bourbon (KY)"
        if '(' in line and ')' in line and not any(
            nav in line for nav in ['Statistics', 'Results', 'Workouts', 'Add to']
        ):
            m = re.search(r'\(([A-Z]{2})\)', line)
            if m and not result.get('registry'):
                result['registry'] = m.group(1)
                # Also extract name if not already set
                name_m = re.match(r'^([^(]+)', line)
                if name_m and not result['name']:
                    result['name'] = name_m.group(1).strip()

        # Foaled line
        if 'FOALED' in line.upper():
            result['foaled'] = line
            parts = line.split(',')
            for p in parts:
                p = p.strip()
                if p in ['TB', 'SB', 'BB', 'CH', 'DK', 'GR', 'RO', 'GY']:
                    result['color'] = p
                elif p in ['H', 'M', 'C', 'F', 'G', 'R']:
                    result['sex'] = p

        # Sire/Dam
        if 'NOT BOURBON' in line:
            result['sire'] = line.replace('(', '').replace(')', '').strip()

        # Connections
        if line.startswith('Jockey:'):
            result['jockey'] = line.replace('Jockey:', '').strip()
        if line.startswith('Trainer:'):
            result['trainer'] = line.replace('Trainer:', '').strip()
        if line.startswith('Owner:'):
            result['owner'] = line.replace('Owner:', '').strip()
        if line.startswith('Breeder:'):
            result['breeder'] = line.replace('Breeder:', '').strip()

        # Career / yearly stats
        for prefix in ['Career', '2025', '2024', '2023', '2022', '2021', '2020']:
            if line.startswith(prefix):
                parts = line.split()
                if len(parts) >= 8:
                    year_label = prefix
                    starts = parts[1]
                    wins = parts[2]
                    seconds = parts[3]
                    thirds = parts[4]
                    best = parts[5]
                    earnings = parts[6]
                    per_start = parts[7] if len(parts) > 7 else ''

                    entry = {
                        'year': year_label,
                        'starts': starts,
                        'wins': wins,
                        'seconds': seconds,
                        'thirds': thirds,
                        'best': best,
                        'earnings': earnings,
                        'per_start': per_start,
                    }

                    if year_label == 'Career':
                        result['career_stats'] = entry
                    else:
                        result['yearly_stats'].append(entry)

        # Stakes class
        if 'BEST RACING CLASS ACHIEVED' in line:
            for j in range(i + 1, min(i + 5, len(lines))):
                next_line = lines[j]
                if next_line and not any(
                    nav in next_line for nav in [
                        'Add to Virtual', 'See Complete', 'Statistics',
                        'Filter', 'SURFACE', 'RACE TYPE'
                    ]
                ):
                    result['stakes_class'] = next_line.strip()
                    break

        # Last sale
        if 'Sold to' in line:
            result['last_sale']['sold_to'] = line.replace('Sold to', '').strip()
        if 'Consigned by' in line:
            result['last_sale']['consignor'] = line.replace('Consigned by', '').strip()

    return result


def _get_race_history(page) -> List[Dict]:
    """
    Click Results tab and extract race-by-race table.
    Table rows are tab-separated: Track | Date | Race# | Type | Breed | Finish | Beyer
    Example: Woodbine\t11/15/2025\t10\tbet365 Kennedy Road Stakes (Gr. 2)\tTB\t2\t101
    """
    races = []

    try:
        tab = page.query_selector('a[href="#results"]')
        if tab:
            tab.click()
            time.sleep(4)
            _clear_modals(page)
            time.sleep(2)
    except Exception:
        return races

    try:
        text = page.inner_text('body')
        lines = text.split('\n')

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            parts = stripped.split('\t')
            if len(parts) < 6:
                continue

            track = parts[0]
            # Filter to known tracks only
            if not any(t in track for t in KNOWN_TRACKS):
                continue

            # Skip header-like rows
            if track == 'Track' or 'Date' in stripped:
                continue

            date = parts[1]
            if not re.match(r'\d{1,2}/\d{1,2}/\d{4}', date):
                continue

            race_num = parts[2]
            race_type = parts[3]
            finish = parts[5] if len(parts) > 5 else ''
            beyer = parts[6] if len(parts) > 6 else ''

            races.append({
                'date': date,
                'track': track,
                'race': race_num,
                'type': race_type,
                'finish': finish,
                'beyer': beyer,
            })

    except Exception:
        pass

    return races


def _get_workouts(page) -> List[str]:
    """Click Workouts tab and extract workout entries."""
    workouts = []

    try:
        tab = page.query_selector('a[href="#workouts"]')
        if tab:
            tab.click()
            time.sleep(4)
            _clear_modals(page)
            time.sleep(2)
    except Exception:
        return workouts

    try:
        text = page.inner_text('body')
        lines = text.split('\n')

        in_section = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            if 'Auction History' in line:
                in_section = False
            if in_section and stripped:
                # Workout lines have month abbreviations
                if any(m in stripped for m in [
                    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
                ]):
                    workouts.append(stripped)

            if 'Rating History' in line:
                in_section = True

        return workouts[:30]  # Recent 30

    except Exception:
        return workouts


# ---------------------------------------------------------------------------
# Output Formatting
# ---------------------------------------------------------------------------

def format_profile_table(data: Dict, limit: int = 15) -> str:
    """Full formatted horse profile with race history table."""
    if not data.get('success'):
        return f"❌ Error: {data.get('error', 'unknown')}"

    lines = []
    name = data.get('name', 'Unknown')
    registry = data.get('registry', '')
    foaled = data.get('foaled', '')
    trainer = data.get('trainer', '-')
    jockey = data.get('jockey', '-')
    owner = data.get('owner', '-')
    stakes_class = data.get('stakes_class', '-')
    sire = data.get('sire', '')
    cs = data.get('career_stats', {})

    # Header
    lines.append(f"🏇 {name}{(' (' + registry + ')') if registry else ''}")
    if foaled:
        lines.append(f"   Foaled: {foaled}")
    if sire:
        lines.append(f"   Breeding: {sire}")
    lines.append(
        f"   Trainer: {trainer} | Jockey: {jockey} | Owner: {owner}"
    )
    lines.append(f"   Best Class: {stakes_class}")
    lines.append("")

    # Career stats
    lines.append(
        f"   Career: {cs.get('starts','-')}s "
        f"{cs.get('wins','-')}W {cs.get('seconds','-')}2n {cs.get('thirds','-')}3n "
        f"Best {cs.get('best','-')} — {cs.get('earnings','-')}"
    )
    lines.append("")

    # Race history
    races = data.get('race_history', [])
    if races:
        limit = min(limit, len(races))
        lines.append(f"   Race History (last {limit} of {len(races)}):")
        lines.append(
            f"   {'Date':<12} {'Trk':<5} {'Race':<5} {'Fin':<5} {'Byr':<6}  Type"
        )
        lines.append("   " + "-" * 68)

        for r in races[:limit]:
            finish = r.get('finish', '-')
            beyer = r.get('beyer', '-')
            rtype = r.get('type', '-')
            # Truncate long type names cleanly
            if len(rtype) > 40:
                rtype = rtype[:39] + '…'
            lines.append(
                f"   {r.get('date',''):<12} "
                f"{r.get('track',''):<5} "
                f"{r.get('race',''):<5} "
                f"#{finish:<5} "
                f"{beyer:<6}  {rtype}"
            )

        if len(races) > limit:
            lines.append(
                f"   ... and {len(races) - limit} more races"
            )

    # Workouts
    workouts = data.get('workouts', [])
    if workouts:
        lines.append("")
        lines.append(f"   Workouts ({len(workouts)} recent):")
        for w in workouts[:5]:
            lines.append(f"   {w}")

    last_sale = data.get('last_sale', {})
    if last_sale:
        lines.append("")
        if last_sale.get('sold_to'):
            lines.append(f"   Last Sale: Sold to {last_sale['sold_to']}")
        if last_sale.get('consignor'):
            lines.append(f"   Consignor: {last_sale['consignor']}")

    return "\n".join(lines)


def format_profile_short(data: Dict) -> str:
    """One-line summary."""
    if not data.get('success'):
        return f"❌ {data.get('error', 'unknown')}"

    cs = data.get('career_stats', {})
    name = data.get('name', 'Unknown')
    starts = cs.get('starts', '-')
    wins = cs.get('wins', '-')
    earnings = cs.get('earnings', '-')
    best = cs.get('best', '-')
    races = data.get('race_history', [])
    last = races[0] if races else {}

    return (
        f"🏇 {name} — {starts}s / {wins}W / Best {best} / {earnings}\n"
        f"   Last: {last.get('date','-')} {last.get('track','-')} "
        f"R{last.get('race','-')} → #{last.get('finish','-')} "
        f"({last.get('beyer','-')}) | Trainer: {data.get('trainer','-')}"
    )


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog='equibase_profile.py',
        description="Charlie Equibase Horse Profiles",
        epilog="Example: python3 equibase_profile.py --horse 'Awesome Bourbon' --races 10",
    )
    parser.add_argument('--horse', required=True, help='Horse name to search')
    parser.add_argument('--output', help='Write JSON to this path')
    parser.add_argument(
        '--races', type=int, default=None,
        help='Limit race history to last N races'
    )
    parser.add_argument(
        '--format', default='table',
        choices=['json', 'table', 'short'],
        help='Output format (default: table)'
    )
    parser.add_argument(
        '--visible', action='store_true',
        help='Show browser window'
    )

    args = parser.parse_args()

    print(f"Looking up: {args.horse}...", file=sys.stderr)

    data = get_profile(
        args.horse,
        races_limit=args.races,
        headless=not args.visible,
    )

    if not data.get('success'):
        print(f"❌ {data.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

    if args.format == 'json':
        output = json.dumps(data, indent=2)
    elif args.format == 'short':
        output = format_profile_short(data)
    else:
        output = format_profile_table(data, limit=args.races or 15)

    print(output)

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n💾 JSON → {args.output}", file=sys.stderr)


if __name__ == '__main__':
    main()
