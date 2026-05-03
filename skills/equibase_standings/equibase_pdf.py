#!/usr/bin/env python3
"""
Equibase Standings PDF Generator — Charlie's Edition
=====================================================
Generates landscape PDF reports for Equibase trainer/jockey/owner standings.

Purpose
-------
Produce a formatted, printer-friendly PDF combining trainer, jockey, and owner
standings for a single track. Used by Charlie to deliver weekly/daily standings
reports via email or Telegram.

Usage (shell)
--------------
    # All 3 types for Woodbine
    python3 skills/equibase_standings/equibase_pdf.py --track WO

    # Just trainers for Gulfstream
    python3 skills/equibase_standings/equibase_pdf.py --track GP --types trainer

    # Trainer + jockey only
    python3 skills/equibase_standings/equibase_pdf.py --track WO --types trainer jockey

    # Different year
    python3 skills/equibase_standings/equibase_pdf.py --track WO --year 2025

Usage (import)
--------------
    from skills.equibase_standings.equibase_pdf import build_pdf

    build_pdf(
        track_code="WO",
        track_name="WOODBINE",
        location="Toronto, Ontario",
        data_by_type={
            'trainer': [...entries...],
            'jockey': [...entries...],
            'owner': [...entries...],
        },
        output_path="standings/WO_standings_20260503.pdf"
    )

Output
-------
    standings/{TRACK}_standings_{YYYYMMDD}.pdf

    e.g.  standings/WO_standings_20260503.pdf

PDF Layout
----------
    [WOODBINE header — navy blue]
    Toronto, Ontario
    Equibase Year-to-Date Standings — 2026 Season
    Generated: May 03, 2026
    ───────────────────────────────────────────────────

    TRAINERS
    Rk  Name                   St   St  1st  2nd  3rd  Earnings      Win%  WPS%
    ─────────────────────────────────────────────────────────────────────
    1   Mark E. Casse          24   --    5    2    3    $254,649     21%   42%
    ...

    JOCKEYS
    [same table format]

    OWNERS
    [same table format]

    ───────────────────────────────────────────────────
    Data © Equibase Company LLC | WOODBINE 2026 season
    Generated 2026-05-03 14:16 ET by Charlie

Design
------
  - Page size: Landscape Letter (11 × 8.5 in)
  - Track brand colors: WO = navy (#1a3a5c), GP = forest green (#1a4a2e)
  - Alternating row shading (white / light gray)
  - Track-colored header row per table
  - Top 25 entries per category
  - Tracks color-coded section labels (TRAINERS / JOCKEYS / OWNERS)

Arguments
---------
  --track    Track code: WO (default), GP, CD, SA, DMR, BEL, SAR, KEE, AQU, TAM, OP, GG
  --types    Data types to include: trainer jockey owner (default: all 3)
  --year     4-digit year (default: 2026)
  --output   Output path (default: auto-generated under standings/)

Track Codes & Colors
--------------------
  WO  — Woodbine          — Navy #1a3a5c
  GP  — Gulfstream Park   — Forest green #1a4a2e
  CD  — Churchill Downs   — Default gray
  SA  — Santa Anita       — Default gray
  DMR — Del Mar           — Default gray
  BEL — Belmont Park      — Default gray
  SAR — Saratoga          — Default gray
  KEE — Keeneland         — Default gray
  AQU — Aqueduct          — Default gray
  TAM — Tampa Bay Downs   — Default gray
  OP  — Oaklawn Park      — Default gray
  GG  — Golden Gate Fields — Default gray

Dependencies
------------
  Hermes venv Python (reportlab, playwright already installed):
    ~/.hermes/hermes-agent/venv/bin/python

  Wraps the Hermes crawler internally:
    ~/.hermes/hermes-agent/venv/bin/python /home/damato/equibase_standings_crawler.py

  Intermediate JSON files written to /tmp/charlie_{track}_{type}.json

Notes
-----
  - PDF generation takes ~30–60 seconds (3 crawler calls + PDF build)
  - Imperva anti-bot may add delays; crawler retries automatically
  - If crawler fails for one type, PDF still builds with available data
  - Output path is always absolute to avoid cwd confusion
  - "By Charlie" footer identifies the source of the report
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HERMES_PYTHON = "/home/damato/.hermes/hermes-agent/venv/bin/python"
CRAWLER = "/home/damato/equibase_standings_crawler.py"
JSON_DIR = "/tmp"
OUTPUT_DIR = "/home/damato/.openclaw/workspace/standings"

# Track metadata: (code, display_name, city_state)
TRACKS: List[Tuple[str, str, str]] = [
    ('WO', 'WOODBINE', 'Toronto, Ontario'),
    ('GP', 'GULFSTREAM PARK', 'Hallandale Beach, FL'),
    ('CD', 'CHURCHILL DOWNS', 'Louisville, KY'),
    ('SA', 'SANTA ANITA PARK', 'Arcadia, CA'),
    ('DMR', 'DEL MAR', 'Del Mar, CA'),
    ('BEL', 'BELMONT PARK', 'Elmont, NY'),
    ('SAR', 'SARATOGA', 'Saratoga Springs, NY'),
    ('KEE', 'KEENELAND', 'Lexington, KY'),
    ('AQU', 'AQUEDUCT', 'Queens, NY'),
    ('TAM', 'TAMPA BAY DOWNS', 'Tampa, FL'),
    ('OP', 'OAKLAWN PARK', 'Hot Springs, AR'),
    ('GG', 'GOLDEN GATE FIELDS', 'Berkeley, CA'),
]

# Lookup maps
TRACK_MAP: Dict[str, Tuple[str, str]] = {code: (name, loc) for code, name, loc in TRACKS}

# Brand colors per track
TRACK_COLORS: Dict[str, str] = {
    'WO': '#1a3a5c',
    'GP': '#1a4a2e',
}

DATA_TYPES: List[Tuple[str, str]] = [
    ('trainer', 'TRAINERS'),
    ('jockey', 'JOCKEYS'),
    ('owner', 'OWNERS'),
]

# PDF column widths (landscape letter, 10 in available width after margins)
# Col: Rk(0.4) | Name(2.4) | Starts(0.5) | St(0.35) | 1st(0.4) |
#      2nd(0.4) | 3rd(0.4) | Earnings(1.0) | Win%(0.5) | WPS%(0.5)
COL_WIDTHS = [
    0.4, 2.4, 0.5, 0.35, 0.4, 0.4, 0.4, 1.0, 0.5, 0.5
]

# ---------------------------------------------------------------------------
# Data Fetching
# ---------------------------------------------------------------------------

def fetch_standings(
    track_code: str,
    data_type: str,
    year: int = 2026,
) -> List[Dict]:
    """
    Pull standings data for one track/type via Hermes crawler.

    Args:
        track_code:  e.g. 'WO', 'GP'
        data_type:   'trainer', 'jockey', or 'owner'
        year:        4-digit year

    Returns:
        List of entry dicts (same format as equibase_crawl.py output)
    """
    output_file = (
        f"{JSON_DIR}/charlie_{track_code.lower()}_{data_type}.json"
    )

    cmd = [
        HERMES_PYTHON, CRAWLER,
        '--track', track_code,
        '--type', data_type,
        '--year', str(year),
        '--output', output_file,
        '--top', '25',
    ]

    print(f"  → {track_code} {data_type}...")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=180,
    )

    if result.returncode != 0:
        print(f"  ⚠ Crawler failed: {result.stderr[:300]}")
        return []

    try:
        with open(output_file) as f:
            data = json.load(f)
        entries = data.get('entries', [])
        print(f"    {len(entries)} entries fetched")
        return entries
    except Exception as e:
        print(f"  ⚠ JSON read error: {e}")
        return []


# ---------------------------------------------------------------------------
# PDF Building
# ---------------------------------------------------------------------------

def _hexcolor(hex_str: str):
    """Convert '#rrggbb' to a ReportLab Color object."""
    from reportlab.lib import colors
    return colors.HexColor(hex_str)


def build_pdf(
    track_code: str,
    track_name: str,
    location: str,
    data_by_type: Dict[str, List[Dict]],
    output_path: str,
) -> str:
    """
    Build a landscape PDF for one track containing trainer/jockey/owner sections.

    Args:
        track_code:     'WO', 'GP', etc.
        track_name:     Display name e.g. 'WOODBINE'
        location:       'Toronto, Ontario'
        data_by_type:   Dict of {data_type: [entries...]}
                        e.g. {'trainer': [...], 'jockey': [...], 'owner': [...]}
        output_path:    Absolute path for output PDF

    Returns:
        The same output_path (for convenience)

    Raises:
        RuntimeError: If PDF build fails
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle,
        Paragraph, Spacer, HRFlowable,
    )
    from reportlab.lib.enums import TA_CENTER

    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    # ── Styles ────────────────────────────────────────────────────────────
    styles = getSampleStyleSheet()
    track_color = _hexcolor(TRACK_COLORS.get(track_code, '#555555'))

    title_style = ParagraphStyle(
        'Title',
        fontSize=18,
        textColor=track_color,
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        fontSize=10,
        textColor=colors.gray,
        alignment=TA_CENTER,
    )
    section_style = ParagraphStyle(
        'Section',
        fontSize=11,
        textColor=track_color,
        spaceBefore=8,
        spaceAfter=3,
    )
    footer_style = ParagraphStyle(
        'Footer',
        fontSize=7,
        textColor=colors.gray,
        alignment=TA_CENTER,
    )

    # ── Document story ───────────────────────────────────────────────────
    story = []

    # Header block
    story.append(Paragraph(track_name.upper(), title_style))
    story.append(Paragraph(location, subtitle_style))
    story.append(Paragraph(
        "Equibase Year-to-Date Standings — 2026 Season", subtitle_style
    ))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y')}", subtitle_style
    ))
    story.append(Spacer(1, 0.08 * inch))
    story.append(HRFlowable(width="100%", thickness=2, color=track_color))
    story.append(Spacer(1, 0.1 * inch))

    # ── Tables ────────────────────────────────────────────────────────────
    for data_type, label in DATA_TYPES:
        entries = data_by_type.get(data_type, [])

        if not entries:
            story.append(Paragraph(f"  {label} — No data available", section_style))
            continue

        story.append(Paragraph(f"  {label}", section_style))

        # Build table data
        table_data = [[
            'Rank', 'Name', 'Starts', 'St', '1st', '2nd', '3rd',
            'Earnings', 'Win%', 'WPS%',
        ]]

        for e in entries[:25]:
            table_data.append([
                e.get('rank', '-'),
                e.get('name', '-')[:28],
                e.get('starts', '-'),
                e.get('starters', '-') or '-',
                e.get('first', '-'),
                e.get('second', '-'),
                e.get('third', '-'),
                e.get('earnings', '-'),
                e.get('win_pct', '-'),
                e.get('wps_pct', '-') or '-',
            ])

        # Apply column widths (inches)
        col_widths_inches = [w * inch for w in COL_WIDTHS]

        table = Table(table_data, colWidths=col_widths_inches, repeatRows=1)
        table.setStyle(TableStyle([
            # ── Header row ──────────────────────────────────────────────
            ('BACKGROUND', (0, 0), (-1, 0), track_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 3),
            ('TOPPADDING', (0, 0), (-1, 0), 3),

            # ── Data rows ─────────────────────────────────────────────
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),   # Rank
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),      # Name
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),   # Numbers
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
            ('TOPPADDING', (0, 1), (-1, -1), 2),

            # ── Alternating rows ──────────────────────────────────────
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.white, colors.HexColor('#f5f5f5')]),

            # ── Grid ─────────────────────────────────────────────────
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#dddddd')),
            ('LINEBELOW', (0, 0), (-1, 0), 1, track_color),

            # ── Rank column bold ─────────────────────────────────────
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))

        story.append(table)
        story.append(Spacer(1, 0.12 * inch))

    # ── Footer ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.06 * inch))
    story.append(HRFlowable(
        width="100%", thickness=0.5, color=colors.HexColor('#cccccc')
    ))
    story.append(Paragraph(
        f"Data © Equibase Company LLC | {track_name} 2026 season | "
        f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M ET')} by Charlie",
        footer_style
    ))

    doc.build(story)
    return output_path


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog='equibase_pdf.py',
        description=(
            "Charlie Equibase PDF Generator — build standings PDF for a track. "
            "Pulls trainer/jockey/owner data via Hermes crawler, builds landscape PDF."
        ),
        epilog=(
            "Example: python3 equibase_pdf.py --track WO\n"
            "  → builds standings/WO_standings_YYYYMMDD.pdf with all 3 types"
        ),
    )
    parser.add_argument(
        '--track', default='WO',
        help="Track code (default: WO). See SKILL.md for full list."
    )
    parser.add_argument(
        '--types', nargs='+',
        default=['trainer', 'jockey', 'owner'],
        metavar='TYPE',
        help="Data types to include: trainer jockey owner (default: all 3)"
    )
    parser.add_argument(
        '--year', type=int, default=2026,
        help="4-digit year (default: 2026)"
    )
    parser.add_argument(
        '--output',
        help="Output path (default: standings/{TRACK}_standings_{YYYYMMDD}.pdf)"
    )

    args = parser.parse_args()

    track_code = args.track.upper()

    # Validate track
    if track_code not in TRACK_MAP:
        valid = ', '.join(TRACK_MAP.keys())
        print(f"Unknown track: {args.track}. Valid: {valid}")
        sys.exit(1)

    track_name, location = TRACK_MAP[track_code]

    # Validate types
    valid_types = ['trainer', 'jockey', 'owner']
    types = [t for t in args.types if t in valid_types]
    if not types:
        print(f"No valid types specified. Use: {' '.join(valid_types)}")
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(
            OUTPUT_DIR,
            f"{track_code}_standings_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

    # ── Header ────────────────────────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"  Equibase PDF — {track_name}")
    print(f"  {datetime.now().strftime('%b %d, %Y %H:%M')}")
    print(f"  Types: {', '.join(types)}")
    print(f"{'='*55}\n")

    # ── Fetch all data types ──────────────────────────────────────────────
    data_by_type: Dict[str, List[Dict]] = {}

    for dtype in types:
        entries = fetch_standings(track_code, dtype, year=args.year)
        data_by_type[dtype] = entries
        time.sleep(2)  # Rate-limit between crawler calls

    if not data_by_type:
        print("❌ No data fetched. Check Imperva blocking or network.")
        sys.exit(1)

    # ── Build PDF ──────────────────────────────────────────────────────────
    print(f"\nBuilding PDF → {output_path}")
    try:
        result = build_pdf(
            track_code,
            track_name,
            location,
            data_by_type,
            output_path,
        )
        size_kb = os.path.getsize(result) // 1024
        print(f"\n✅ Done — {result} ({size_kb}KB)")
    except Exception as e:
        print(f"❌ PDF build failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
