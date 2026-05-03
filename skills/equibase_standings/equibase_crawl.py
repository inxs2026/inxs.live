#!/usr/bin/env python3
"""
Equibase Standings Crawler — Charlie's Edition
===============================================
Wraps the Hermes Equibase crawler and adds Charlie's output formatting.

Purpose
-------
Pull jockey, trainer, or owner standings from Equibase meet pages.
Used by Charlie to answer on-demand questions about any trainer/jockey/owner
at WO, GP, or other supported tracks.

Usage (shell)
-------------
    python3 skills/equibase_standings/equibase_crawl.py --track WO --type trainer
    python3 skills/equibase_standings/equibase_crawl.py --track GP --type jockey --top 10
    python3 skills/equibase_standings/equibase_crawl.py --track WO --type owner --output /tmp/wo_owner.json

Usage (import)
--------------
    from skills.equibase_standings.equibase_crawl import get_standings, format_standings
    data = get_standings("WO", "trainer", year=2026)
    text = format_standings("WO", "trainer", data)
    print(text)

Arguments
---------
  --track    Track code: WO, GP, CD, SA, DMR, BEL, SAR, KEE, AQU, TAM, OP, GG
  --type     Data type: trainer (default), jockey, owner
  --year     4-digit year (default: 2026)
  --top      Number of entries to show in console output (default: 25, max: 100)
  --output   Optional path to write JSON output file
  --visible  Show browser window (for debugging Imperva blocks)

Output Format (console)
-----------------------
    🏇 {TRACK NAME} — {DATA TYPE} STANDINGS  (as of {MM/DD/YYYY})
    ──────────────────────────────────────────────────────────────
    Rk   Name                        St     1st   Win%   Earnings
    ──────────────────────────────────────────────────────────────
    1    Mark E. Casse               24     5     21%    $254,649
    2    Kevin Attard                10     2     20%    $120,485
    ...
    ──────────────────────────────────────────────────────────────
    Total trainers: 88

Output Format (JSON, when --output specified)
--------------------------------------------
    {
      "track": "WOODBINE",
      "type": "trainer",
      "year": 2026,
      "url": "https://www.equibase.com/stats/View.cfm?tf=meet&rbt=TB&tb=trainer",
      "as_of": "05/03/2026",
      "entries": [
        {
          "rank": "1", "name": "Mark E. Casse", "starts": "24",
          "starters": "--", "first": "5", "second": "2", "third": "3",
          "earnings": "$254,649", "win_pct": "21%", "wps_pct": "42%",
          "per_start": "$10,610", "wps_per_start": "0.42"
        },
        ...
      ]
    }

Track Codes
-----------
  WO  — Woodbine (Toronto, Ontario)
  GP  — Gulfstream Park (Hallandale Beach, FL)
  CD  — Churchill Downs (Louisville, KY)
  SA  — Santa Anita Park (Arcadia, CA)
  DMR — Del Mar (Del Mar, CA)
  BEL — Belmont Park (Elmont, NY)
  SAR — Saratoga (Saratoga Springs, NY)
  KEE — Keeneland (Lexington, KY)
  AQU — Aqueduct (Queens, NY)
  TAM — Tampa Bay Downs (Tampa, FL)
  OP  — Oaklawn Park (Hot Springs, AR)
  GG  — Golden Gate Fields (Berkeley, CA)

Data Types
---------
  trainer  — Trainer standings (default). Includes "starters" column.
  jockey   — Jockey standings. No starters column.
  owner    — Owner standings. No starters column.

Dependencies
------------
  Hermes venv Python (playwright, reportlab already installed):
    ~/.hermes/hermes-agent/venv/bin/python

Notes
-----
- Imperva anti-bot may cause 45-second delays on first load
- If blocked, wait 5 minutes and re-run
- JSON output is authoritative; console table is for human reading only
- Trainer/jockey/owner tables have different columns — crawler handles this
  via header-indexed lookup so column positions don't matter
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HERMES_CRAWLER = "/home/damato/equibase_standings_crawler.py"
HERMES_PYTHON = "/home/damato/.hermes/hermes-agent/venv/bin/python"

TRACKS: Dict[str, str] = {
    'WO': 'WOODBINE',
    'GP': 'GULFSTREAM PARK',
    'CD': 'CHURCHILL DOWNS',
    'SA': 'SANTA ANITA PARK',
    'DMR': 'DEL MAR',
    'BEL': 'BELMONT PARK',
    'SAR': 'SARATOGA',
    'KEE': 'KEENELAND',
    'AQU': 'AQUEDUCT',
    'TAM': 'TAMPA BAY DOWNS',
    'OP': 'OAKLAWN PARK',
    'GG': 'GOLDEN GATE FIELDS',
}

DATA_TYPES: List[str] = ['trainer', 'jockey', 'owner']

# ---------------------------------------------------------------------------
# Core Functions
# ---------------------------------------------------------------------------


def get_standings(
    track: str,
    data_type: str,
    year: int = 2026,
    top: int = 100,
    output: Optional[str] = None,
) -> List[Dict]:
    """
    Pull standings data from Equibase via Hermes crawler.

    Args:
        track:      Track code (e.g. 'WO', 'GP')
        data_type:  'trainer', 'jockey', or 'owner'
        year:       4-digit year (default 2026)
        top:        Number of entries to fetch (default 100, max JSON rows)
        output:     Optional path to write JSON file

    Returns:
        List of entry dicts. Each dict has keys:
        rank, name, starts, starters, first, second, third,
        earnings, win_pct, wps_pct, per_start, wps_per_start

    Raises:
        RuntimeError: If crawler exits non-zero
    """
    cmd = [
        HERMES_PYTHON, HERMES_CRAWLER,
        '--track', track,
        '--type', data_type,
        '--year', str(year),
        '--top', str(top),
    ]
    if output:
        cmd.extend(['--output', output])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

    if result.returncode != 0:
        raise RuntimeError(
            f"Crawler failed (exit {result.returncode}):\n{result.stderr[:500]}"
        )

    # Parse JSON file if output path was specified
    if output:
        try:
            with open(output) as f:
                data = json.load(f)
            return data.get('entries', [])
        except Exception as e:
            raise RuntimeError(f"Failed to read JSON output ({output}): {e}")

    # Otherwise, parse from console output (less reliable — prefer JSON)
    # JSON is the authoritative source; console is a fallback.
    return []


def load_json(path: str) -> Dict:
    """Load and return a JSON file written by the crawler."""
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

# Console column layout (character widths)
# Rank(4) | Name(28) | Starts(5) | 1st(4) | Win%(5) | Earnings(10)
_CONSOLE_WIDTH = 62  # total characters per separator line


def format_standings(
    track: str,
    data_type: str,
    entries: List[Dict],
    as_of: Optional[str] = None,
) -> str:
    """
    Format standings entries into a human-readable console table.

    Args:
        track:      Track code (used for header display)
        data_type:  'trainer', 'jockey', or 'owner'
        entries:    List of entry dicts from get_standings()
        as_of:      Date string for header (default: today)

    Returns:
        Formatted multi-line string, ready to print.

    Output format:
        🏇 {TRACK NAME} — {DATA TYPE} STANDINGS  (as of {MM/DD/YYYY})
        ──────────────────────────────────────────────────────────────
        Rk   Name                        St     1st   Win%   Earnings
        ──────────────────────────────────────────────────────────────
        1    Mark E. Casse               24     5     21%    $254,649
        ...
        ──────────────────────────────────────────────────────────────
        Total trainers: 88
    """
    track_name = TRACKS.get(track.upper(), track.upper())
    dtype_label = data_type.upper()
    date_str = as_of or datetime.now().strftime('%m/%d/%Y')

    # Emoji: trainers=🏇, jockeys=🧢, owners=💰
    emoji = {'trainer': '🏇', 'jockey': '🧢', 'owner': '💰'}.get(data_type, '📊')

    lines: List[str] = []

    # Header
    lines.append(f"{emoji} {track_name} — {dtype_label} STANDINGS  (as of {date_str})")
    lines.append("─" * _CONSOLE_WIDTH)

    # Column headers (different for trainer vs jockey/owner)
    if data_type == 'trainer':
        header = f"{'Rk':<4} {'Trainer':<28} {'St':>4} {'Str':>4} {'1st':>4} {'Win%':>5}   Earnings"
    else:
        header = f"{'Rk':<4} {'Name':<28} {'St':>4} {'1st':>4} {'Win%':>5}   Earnings"

    lines.append(header)
    lines.append("─" * _CONSOLE_WIDTH)

    # Data rows
    for e in entries:
        rank = e.get('rank', '?')
        name = e.get('name', '-')[:27]
        starts = e.get('starts', '-')
        first = e.get('first', '-')
        win_pct = e.get('win_pct', '-') or '-'
        earnings = e.get('earnings', '-') or '-'

        if data_type == 'trainer':
            starters = e.get('starters', '-') or '-'
            lines.append(
                f"{rank:<4} {name:<28} {starts:>4} {starters:>4} {first:>4} "
                f"{win_pct:>5}   {earnings}"
            )
        else:
            lines.append(
                f"{rank:<4} {name:<28} {starts:>4} {first:>4} "
                f"{win_pct:>5}   {earnings}"
            )

    # Footer
    lines.append("─" * _CONSOLE_WIDTH)
    total = len(entries)
    lines.append(f"Total entries: {total}")

    return '\n'.join(lines)


def format_single_trainer(entries: List[Dict], trainer_name: str) -> str:
    """
    Find and format a single trainer's stats.

    Args:
        entries:    Full list of standings entries
        trainer_name: Name to search for (partial match, case-insensitive)

    Returns:
        Formatted string for one trainer, or "not found" message.
    """
    trainer_name_lower = trainer_name.lower()

    # Partial match: find any entry where name contains the search term
    matches = [
        e for e in entries
        if trainer_name_lower in e.get('name', '').lower()
    ]

    if not matches:
        return f"No trainer found matching '{trainer_name}'"

    # If multiple matches (e.g. "Casse" → "Mark E. Casse", "John Casse"), show all
    if len(matches) > 1:
        lines = [f"Multiple matches for '{trainer_name}':"]
        for e in matches:
            lines.append(
                f"  #{e.get('rank')} {e.get('name')} — "
                f"{e.get('starts')} starts, {e.get('first')} wins, "
                f"{e.get('win_pct')} Win%, {e.get('earnings')}"
            )
        return '\n'.join(lines)

    e = matches[0]

    emoji = '🏇'
    rank = e.get('rank', '?')
    name = e.get('name')
    starts = e.get('starts', '-')
    first = e.get('first', '-')
    second = e.get('second', '-')
    third = e.get('third', '-')
    earnings = e.get('earnings', '-')
    win_pct = e.get('win_pct', '-') or '-'
    wps_pct = e.get('wps_pct', '-') or '-'

    lines = [
        f"{emoji} {name} — WOODBINE Trainer Standings 2026",
        f"",
        f"  Rank      #{rank}",
        f"  Starts   {starts}",
        f"  1st       {first}",
        f"  2nd       {second}",
        f"  3rd       {third}",
        f"  Win%      {win_pct}",
        f"  WPS%      {wps_pct}",
        f"  Earnings  {earnings}",
    ]

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog='equibase_crawl.py',
        description="Charlie Equibase Standings — pull trainer/jockey/owner stats",
        epilog="Example: python3 equibase_crawl.py --track WO --type trainer --top 25",
    )
    parser.add_argument(
        '--track', default='WO',
        help="Track code (default: WO). See SKILL.md for full list."
    )
    parser.add_argument(
        '--type', default='trainer', choices=DATA_TYPES,
        help="Data type (default: trainer)"
    )
    parser.add_argument(
        '--year', type=int, default=2026,
        help="4-digit year (default: 2026)"
    )
    parser.add_argument(
        '--top', type=int, default=25,
        help="Number of entries in console output (default: 25)"
    )
    parser.add_argument(
        '--output', default=None,
        help="Write JSON to this path (authoritative data)"
    )
    parser.add_argument(
        '--visible', action='store_true',
        help="Show browser window (for debugging Imperva blocks)"
    )

    args = parser.parse_args()

    track_upper = args.track.upper()
    if track_upper not in TRACKS:
        print(f"Unknown track: {args.track}. Valid codes: {', '.join(TRACKS)}")
        sys.exit(1)

    # Optional JSON output path (unique per session to avoid stale reads)
    if not args.output:
        args.output = f"/tmp/charlie_{track_upper.lower()}_{args.type}.json"

    try:
        entries = get_standings(
            track_upper,
            args.type,
            year=args.year,
            top=args.top,
            output=args.output,
        )

        # Print formatted console output
        text = format_standings(track_upper, args.type, entries)
        print(text)

    except RuntimeError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
