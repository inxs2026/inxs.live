#!/usr/bin/env python3
"""
Equibase Horse Profile PDF Generator — Charlie's Edition
=========================================================
Generate a formatted PDF report for a horse profile.

Usage
-----
    python3 skills/equibase_profiles/equibase_profile_pdf.py --horse "Awesome Bourbon"
    python3 skills/equibase_profiles/equibase_profile_pdf.py --horse "Awesome Bourbon" --races 10
    python3 skills/equibase_profiles/equibase_profile_pdf.py --horse "Some Horse" --output /tmp/horse.pdf

Output
------
    horses/{HORSE_NAME}_profile_{YYYYMMDD}.pdf
"""

import argparse
import os
import sys
import time
from datetime import datetime
from typing import Dict

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

HERMES_PYTHON = "/home/damato/.hermes/hermes-agent/venv/bin/python"
OUTPUT_DIR = "/home/damato/.openclaw/workspace/horses"


def _hexcolor(hex_str: str):
    from reportlab.lib import colors
    return colors.HexColor(hex_str)


def build_profile_pdf(
    profile_data: Dict,
    output_path: str,
    races_limit: int = 20,
) -> str:
    """
    Build a landscape PDF for a horse profile.

    Args:
        profile_data:  Dict from equibase_profile.get_profile()
        output_path:  Absolute path for output PDF
        races_limit:  Max races to show in table (default 20)

    Returns:
        The output_path (for convenience)
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
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    styles = getSampleStyleSheet()
    navy = _hexcolor('#1a3a5c')

    title_style = ParagraphStyle(
        'Title', fontSize=20, textColor=navy,
        alignment=TA_LEFT, spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        'Sub', fontSize=10, textColor=colors.gray,
        alignment=TA_LEFT, spaceAfter=2,
    )
    section_style = ParagraphStyle(
        'Section', fontSize=11, textColor=navy,
        spaceBefore=8, spaceAfter=3,
    )
    footer_style = ParagraphStyle(
        'Footer', fontSize=7, textColor=colors.gray,
        alignment=TA_CENTER,
    )
    label_style = ParagraphStyle(
        'Label', fontSize=8, textColor=colors.gray,
    )
    value_style = ParagraphStyle(
        'Value', fontSize=9, textColor=colors.black,
    )

    story = []

    # ── Header ──────────────────────────────────────────────────────────
    name = profile_data.get('name', 'Unknown')
    registry = profile_data.get('registry', '')
    foaled = profile_data.get('foaled', '')
    stakes_class = profile_data.get('stakes_class', '')

    story.append(Paragraph(
        f"{name}{' (' + registry + ')' if registry else ''}",
        title_style
    ))
    story.append(Paragraph(foaled, subtitle_style))
    story.append(Paragraph(
        f"Best Class: {stakes_class}" if stakes_class else "",
        subtitle_style
    ))
    story.append(Spacer(1, 0.05 * inch))
    story.append(HRFlowable(width="100%", thickness=2, color=navy))
    story.append(Spacer(1, 0.1 * inch))

    # ── Info Grid (2 columns) ───────────────────────────────────────────
    trainer = profile_data.get('trainer', '-')
    jockey = profile_data.get('jockey', '-')
    owner = profile_data.get('owner', '-')
    sire = profile_data.get('sire', '-')
    breeder = profile_data.get('breeder', '-')
    cs = profile_data.get('career_stats', {})

    # Build a clean info table
    info_data = [
        ['Trainer', trainer],
        ['Jockey', jockey],
        ['Owner', owner],
        ['Breeder', breeder],
        ['Sire / Dam', sire],
    ]

    info_table = Table(info_data, colWidths=[1.0 * inch, 5.0 * inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LINEBELOW', (0, 0), (-1, -1), 0.3, colors.HexColor('#eeeeee')),
    ]))

    # Career stats box
    cs_data = [
        ['Starts', cs.get('starts', '-')],
        ['Wins', cs.get('wins', '-')],
        ['Seconds', cs.get('seconds', '-')],
        ['Thirds', cs.get('thirds', '-')],
        ['Best Beyer', cs.get('best', '-')],
        ['Earnings', cs.get('earnings', '-')],
    ]

    cs_table = Table(cs_data, colWidths=[0.9 * inch, 1.1 * inch])
    cs_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
        ('TEXTCOLOR', (1, 0), (1, -1), navy),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
    ]))

    # Side-by-side layout
    header_data = [[info_table, cs_table]]
    header_table = Table(header_data, colWidths=[6.5 * inch, 2.2 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (1, 0), (1, 0), 12),
    ]))

    story.append(header_table)
    story.append(Spacer(1, 0.12 * inch))

    # ── Race History Table ───────────────────────────────────────────────
    races = profile_data.get('race_history', [])
    if races:
        races = races[:races_limit]
        story.append(Paragraph(
            f"Race History ({len(races)} of {len(profile_data.get('race_history', []))} shown)",
            section_style
        ))

        # Table columns: Date | Track | Race | Finish | Beyer | Type
        race_rows = [['Date', 'Track', 'Race', 'Fin', 'Beyer', 'Type / Class']]
        for r in races:
            finish = r.get('finish', '-')
            beyer = r.get('beyer', '-')
            rtype = r.get('type', '-')
            if len(rtype) > 45:
                rtype = rtype[:44] + '…'

            race_rows.append([
                r.get('date', '-'),
                r.get('track', '-'),
                r.get('race', '-'),
                f"#{finish}" if finish else '-',
                beyer if beyer else '-',
                rtype,
            ])

        race_col_widths = [0.9*inch, 1.1*inch, 0.45*inch, 0.4*inch, 0.5*inch, 6.0*inch]
        race_table = Table(race_rows, colWidths=race_col_widths, repeatRows=1)
        race_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 3),
            ('TOPPADDING', (0, 0), (-1, 0), 3),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # Date
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Track
            ('ALIGN', (2, 1), (4, -1), 'CENTER'),   # Race, Fin, Beyer
            ('ALIGN', (5, 1), (5, -1), 'LEFT'),     # Type
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
            ('TOPPADDING', (0, 1), (-1, -1), 2),

            # Alternating rows
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.white, colors.HexColor('#f5f5f5')]),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#dddddd')),
            ('LINEBELOW', (0, 0), (-1, 0), 1, navy),

            # Finish column: highlight wins (1st)
            ('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold'),
        ]))

        story.append(race_table)

    # ── Workouts ────────────────────────────────────────────────────────
    workouts = profile_data.get('workouts', [])
    if workouts:
        story.append(Spacer(1, 0.08 * inch))
        story.append(Paragraph(f"Recent Workouts ({len(workouts)} shown)", section_style))
        workout_text = '  |  '.join(workouts[:8])
        story.append(Paragraph(workout_text, value_style))

    # ── Footer ─────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.08 * inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
    story.append(Paragraph(
        f"Data © Equibase Company LLC | {name} profile | "
        f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M ET')} by Charlie",
        footer_style
    ))

    doc.build(story)
    return output_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a PDF report for a horse profile"
    )
    parser.add_argument('--horse', required=True, help='Horse name to look up')
    parser.add_argument('--races', type=int, default=20, help='Max races in table (default: 20)')
    parser.add_argument('--output', help='Output PDF path (default: auto)')

    args = parser.parse_args()

    # Import and run the profile crawler
    import subprocess
    import json

    output_json = f"/tmp/charlie_profile_{datetime.now().strftime('%Y%m%d%H%M')}.json"
    crawl_cmd = [
        HERMES_PYTHON,
        os.path.join(os.path.dirname(__file__), 'equibase_profile.py'),
        '--horse', args.horse,
        '--format', 'json',
        '--output', output_json,
    ]

    if args.races:
        crawl_cmd.extend(['--races', str(args.races)])

    print(f"Fetching profile for: {args.horse}...", file=sys.stderr)
    result = subprocess.run(crawl_cmd, capture_output=True, text=True, timeout=180)

    if result.returncode != 0:
        print(f"❌ Profile fetch failed:\n{result.stderr[:500]}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(output_json) as f:
            profile_data = json.load(f)
    except Exception as e:
        print(f"❌ Could not read profile JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not profile_data.get('success'):
        print(f"❌ {profile_data.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_pdf = args.output
    else:
        # Sanitize horse name for filename
        safe_name = args.horse.replace(' ', '_').replace("'", '').replace('"', '')
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_pdf = os.path.join(
            OUTPUT_DIR,
            f"{safe_name}_profile_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

    print(f"Building PDF → {output_pdf}", file=sys.stderr)
    result_path = build_profile_pdf(profile_data, output_pdf, races_limit=args.races)
    size_kb = os.path.getsize(result_path) // 1024
    print(f"✅ Done — {result_path} ({size_kb}KB)", file=sys.stderr)


if __name__ == '__main__':
    main()